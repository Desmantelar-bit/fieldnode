import { getValidated } from '@/services/apiRead';
import { HeatmapSchema } from '@/schemas/heatmap';
export function getFleetHeatmap(signal?: AbortSignal) { return getValidated('events/heatmap/', HeatmapSchema, signal); }
