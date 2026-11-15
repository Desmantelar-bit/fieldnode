import { GlobalSearchSchema, type GlobalSearch } from '@/schemas/busca';
import { getValidated } from '@/services/apiRead';

export function searchGlobal(query: string, signal?: AbortSignal): Promise<GlobalSearch> {
  return getValidated(`search/?q=${encodeURIComponent(query)}`, GlobalSearchSchema, signal);
}
