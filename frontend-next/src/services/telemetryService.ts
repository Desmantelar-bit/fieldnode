import {
  OperatorSchema,
  type Machine,
  type MachinePosition,
  type Operator,
  type Telemetry,
  type TelemetryInput,
  type AnalisePrescricao,
  type Prescricao,
  type Relatorio,
} from '@/types/telemetry';
import {
  ListaColheitadeirasSchema,
  ListaLeiturasTelemetriaSchema,
  ListaPosicoesMaquinasSchema,
  AnalisePrescricaoSchema,
  ListaPrescricoesSchema,
  RelatorioResumoSchema,
  TelemetryInputSchema,
} from '@/schemas';
import type { z } from 'zod';

declare const process: { env: Record<string, string | undefined> };

function normalizeApiUrl(value: string): string {
  const trimmed = value.replace(/\/+$/, "");
  if (!trimmed) return "http://127.0.0.1:8000/api";
  if (
    trimmed === "/api" ||
    trimmed.endsWith("/api") ||
    trimmed.includes("/api/")
  ) {
    return trimmed;
  }
  return `${trimmed}/api`;
}

export function resolveApiUrl(): string {
  if (typeof window !== "undefined") {
    const clientUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_FIELDNODE_SERVER_API_URL;
    return normalizeApiUrl(clientUrl || "/api");
  }

  const configuredUrl =
    process.env.FIELDNODE_SERVER_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.NEXT_PUBLIC_FIELDNODE_SERVER_API_URL;
  return normalizeApiUrl(configuredUrl || "http://127.0.0.1:8000/api");
}

const API_URL = resolveApiUrl();
const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY || "";
const API_TIMEOUT_MS = 10000;

function withTimeout<T>(
  request: (signal: AbortSignal) => Promise<T>,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  return request(controller.signal).finally(() => clearTimeout(timer));
}

async function handleResponse<T = unknown>(
  response: Response,
  label = "",
): Promise<T> {
  if (!response.ok) {
    let text = "";
    try {
      text = await response.text();
    } catch {
      text = response.statusText || "";
    }
    throw new Error(
      `${label} HTTP ${response.status} ${response.statusText} ${text}`.trim(),
    );
  }

  try {
    return await response.json();
  } catch (e) {
    throw new Error(`${label} Falha ao parsear JSON: ${(e as Error).message}`);
  }
}

function validateApiContract<T extends z.ZodTypeAny>(
  schema: T,
  data: unknown,
  label: string,
): z.infer<T> {
  const parseResult = schema.safeParse(data);

  if (!parseResult.success) {
    console.error('Contrato de API quebrado:', {
      endpoint: label,
      errors: parseResult.error.format(),
    });
    throw new Error('Formato de dados inesperado recebido do servidor.');
  }

  return parseResult.data;
}

export const telemetryService = {
  async getFleetStatus(): Promise<Machine[]> {
    const headers = new Headers({ Accept: "application/json" });
    if (API_KEY) headers.set("X-API-Key", API_KEY);
    const response = await withTimeout((signal) =>
      fetch(`${API_URL}/colheitadeira/`, {
        cache: "no-store",
        headers,
        signal,
      }),
    );
    const data = await handleResponse(response, "getFleetStatus:");
    return validateApiContract(ListaColheitadeirasSchema, data, "getFleetStatus");
  },

  async getMachinePositions(maquinaId?: string): Promise<MachinePosition[]> {
    const url = maquinaId
      ? `${API_URL}/maquinas/posicao/?maquina_id=${encodeURIComponent(maquinaId)}`
      : `${API_URL}/maquinas/posicao/`;
    const response = await withTimeout((signal) =>
      fetch(url, {
        cache: "no-store",
        headers: new Headers({ Accept: "application/json" }),
        signal,
      }),
    );
    const data = await handleResponse(response, "getMachinePositions:");
    return validateApiContract(ListaPosicoesMaquinasSchema, data, "getMachinePositions");
  },

  async getLatestReadings(): Promise<Telemetry[]> {
    const response = await withTimeout((signal) =>
      fetch(`${API_URL}/leituras/ultimas/`, {
        headers: new Headers({ Accept: "application/json" }),
        signal,
      }),
    );
    const data = await handleResponse(response, "getLatestReadings:");
    return validateApiContract(ListaLeiturasTelemetriaSchema, data, "getLatestReadings");
  },

  async getMachineReadings(machineId: string): Promise<Telemetry[]> {
    const response = await withTimeout((signal) =>
      fetch(
        `${API_URL}/telemetria/?maquina_id=${encodeURIComponent(machineId)}`,
        {
          cache: "no-store",
          headers: new Headers({ Accept: "application/json" }),
          signal,
        },
      ),
    );
    const data = await handleResponse(response, "getMachineReadings:");
    return validateApiContract(ListaLeiturasTelemetriaSchema, data, "getMachineReadings");
  },

  async getOperators(): Promise<Operator[]> {
    const headers = new Headers({ Accept: "application/json" });
    if (API_KEY) headers.set("X-API-Key", API_KEY);
    const response = await withTimeout((signal) =>
      fetch(`${API_URL}/operario/`, { cache: "no-store", headers, signal }),
    );
    const data = await handleResponse(response, "getOperators:");
    return validateApiContract(OperatorSchema.array(), data, "getOperators");
  },

  async sendTelemetry(reading: TelemetryInput) {
    const payload = validateApiContract(TelemetryInputSchema, reading, "sendTelemetry");
    const headers = new Headers({
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
    });
    const response = await withTimeout((signal) =>
      fetch(`${API_URL}/telemetria/`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
        signal,
      }),
    );
    const data = await handleResponse(response, "sendTelemetry:");
    return data;
  },

  async queueTelemetry(reading: TelemetryInput) {
    if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) {
      return telemetryService.sendTelemetry(reading);
    }

    const registration = await navigator.serviceWorker.ready;
    const worker = registration.active || navigator.serviceWorker.controller;
    worker?.postMessage({
      type: "QUEUE_TELEMETRY",
      payload: reading,
      headers: API_KEY ? { "X-API-Key": API_KEY } : {},
    });

    return { status: "queued" };
  },

  async getPrescricoes(machineId: string): Promise<Prescricao[]> {
    const headers = new Headers({ Accept: "application/json" });
    if (API_KEY) headers.set("X-API-Key", API_KEY);
    const response = await withTimeout((signal) =>
      fetch(
        `${API_URL}/prescricoes/lista/?maquina_id=${encodeURIComponent(machineId)}`,
        { cache: "no-store", headers, signal },
      ),
    );
    const data = await handleResponse(response, "getPrescricoes:");
    return validateApiContract(ListaPrescricoesSchema, data, "getPrescricoes");
  },

  async getPrescricao(machineId: string): Promise<Prescricao> {
    const prescricoes = await telemetryService.getPrescricoes(machineId);
    if (prescricoes.length === 0) {
      throw new Error("Nenhuma prescricao encontrada para esta maquina.");
    }
    return prescricoes[0];
  },

  async getAnalisePrescricao(machineId: string): Promise<AnalisePrescricao> {
    const response = await withTimeout((signal) =>
      fetch(`${API_URL}/prescricoes/${encodeURIComponent(machineId)}/`, {
        cache: "no-store",
        headers: new Headers({ Accept: "application/json" }),
        signal,
      }),
    );
    const data = await handleResponse(response, "getAnalisePrescricao:");
    return validateApiContract(
      AnalisePrescricaoSchema,
      data,
      "getAnalisePrescricao",
    );
  },

  async getRelatorio(options?: {
    formato?: "json" | "csv";
    machineId?: string;
    period?: number;
  }): Promise<Relatorio> {
    const headers = new Headers({ Accept: "application/json" });
    if (API_KEY) headers.set("X-API-Key", API_KEY);
    const params = new URLSearchParams({
      formato: options?.formato ?? "json",
    });
    if (options?.machineId) params.set("maquina_id", options.machineId);
    if (options?.period != null) params.set("periodo", String(options.period));
    const url = `${API_URL}/relatorio/?${params.toString()}`;
    const response = await withTimeout((signal) =>
      fetch(url, { cache: "no-store", headers, signal }),
    );
    const data = await handleResponse(response, "getRelatorio:");

    return validateApiContract(RelatorioResumoSchema, data, "getRelatorio");
  },
};
