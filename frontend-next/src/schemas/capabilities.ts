import { z } from 'zod';

export const MachineCapabilitySchema = z.object({
  canonical_parameter: z.string(),
  unidade: z.string().nullable(),
  fonte: z.object({
    manufacturer: z.string(),
    protocol: z.string(),
    mapping_version: z.string(),
  }),
  taxa_media_por_hora: z.number().nullable(),
  ultima_leitura: z.string(),
  qualidade: z.string(),
  amostras: z.number().int().nonnegative(),
});

export const MachineCapabilitiesSchema = z.object({
  machine_id: z.string(),
  external_code: z.string(),
  periodo_dias: z.number().int().positive(),
  capabilities: MachineCapabilitySchema.array(),
});

export type MachineCapability = z.infer<typeof MachineCapabilitySchema>;
export type MachineCapabilities = z.infer<typeof MachineCapabilitiesSchema>;
