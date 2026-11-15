import { z } from 'zod';

const SearchItemSchema = z.object({ id: z.string(), label: z.string(), description: z.string(), href: z.string() });
export const GlobalSearchSchema = z.object({
  query: z.string(),
  results: z.object({ machines: z.array(SearchItemSchema), operators: z.array(SearchItemSchema), decisions: z.array(SearchItemSchema) }),
});
export type GlobalSearch = z.infer<typeof GlobalSearchSchema>;
