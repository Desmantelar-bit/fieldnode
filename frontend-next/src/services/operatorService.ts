import { resolveApiUrl } from '@/services/telemetryService';
import { OperatorSchema, type Operator } from '@/types/telemetry';

/* ──────────────────────────────────────────────────────────────────────────
   operatorService — ESCRITA de operários.

   Por que em arquivo próprio, e não dentro do telemetryService: aquele é o
   contrato de LEITURA de telemetria, e a regra do repositório pede para não
   mexer na sua lógica nem na sua assinatura. Além disso, escrita tem outra
   natureza — pode ser recusada por validação e precisa devolver o erro por
   campo, o que não cabe no formato dos leitores.

   Endpoint: POST /api/operario/. O `OperarioViewSet` é um ModelViewSet, então
   aceita criação; o modelo tem exatamente três campos editáveis — nome,
   tempo_de_servico e no_banco.
   ────────────────────────────────────────────────────────────────────────── */

export type OperatorInput = {
  nome: string;
  tempo_de_servico: number;
  no_banco: boolean;
};

/** Erro de cadastro já traduzido, com os erros por campo que o DRF devolveu. */
export class OperatorError extends Error {
  readonly fields: Record<string, string>;

  constructor(message: string, fields: Record<string, string> = {}) {
    super(message);
    this.name = 'OperatorError';
    this.fields = fields;
  }
}

const TIMEOUT_MS = 10000;

/** Converte o corpo de erro do DRF em algo que a tela possa exibir.
 *  O formato é `{ "nome": ["Este campo é obrigatório."] }`, ou `{ "detail": "..." }`. */
async function parseError(response: Response): Promise<OperatorError> {
  try {
    const body = (await response.json()) as Record<string, unknown>;
    const fields: Record<string, string> = {};

    for (const [chave, valor] of Object.entries(body ?? {})) {
      if (Array.isArray(valor) && valor.length) fields[chave] = String(valor[0]);
      else if (typeof valor === 'string') fields[chave] = valor;
    }

    const primeiro = Object.values(fields)[0];
    if (primeiro) return new OperatorError(primeiro, fields);
  } catch {
    // corpo não era JSON
  }

  return new OperatorError(`O servidor recusou o cadastro (HTTP ${response.status}).`);
}

export async function createOperator(input: OperatorInput): Promise<Operator> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response: Response;
  try {
    const headers = new Headers({ 'Content-Type': 'application/json', Accept: 'application/json' });
    response = await fetch(`${resolveApiUrl()}/operario/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(input),
      signal: controller.signal,
    });
  } catch {
    throw new OperatorError(
      'Não foi possível falar com o servidor. Verifique a conexão e tente de novo.',
    );
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) throw await parseError(response);

  const parsed = OperatorSchema.safeParse(await response.json());
  if (!parsed.success) {
    throw new OperatorError('O operário foi criado, mas o servidor respondeu num formato inesperado.');
  }
  return parsed.data;
}
