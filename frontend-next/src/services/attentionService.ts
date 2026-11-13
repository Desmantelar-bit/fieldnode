import { AttentionSummarySchema, type AttentionSummary } from '@/schemas/attention';
import { getValidated } from '@/services/apiRead';

export const attentionService = {
  get(signal?: AbortSignal): Promise<AttentionSummary> {
    return getValidated('attention/summary/', AttentionSummarySchema, signal);
  },
};
