import { z } from 'zod';

export const HeatmapCellSchema = z.object({
  machine_id: z.string(), machine_external_code: z.string(), hour: z.string().datetime({ offset: true }),
  worst_severity: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']), event_count: z.number().int().nonnegative(), quality_issue: z.boolean(),
});
export const HeatmapSchema = z.object({ start: z.string().datetime({ offset: true }), end: z.string().datetime({ offset: true }), timezone: z.string(), results: z.array(HeatmapCellSchema) });
export type Heatmap = z.infer<typeof HeatmapSchema>;
export type HeatmapCell = z.infer<typeof HeatmapCellSchema>;
