import { getAll, put, remove, type QueuedAction } from './db';

export type ActionInput = Omit<QueuedAction, 'localId' | 'state' | 'attempts' | 'createdAt'> & { key?: string };

const actionUrl = (action: QueuedAction) => action.type === 'wo.update'
  ? `/api/workorders/${action.id}/`
  : `/api/decisions/${action.id}/`;

export async function enqueueAction(input: ActionInput) {
  const action: QueuedAction = {
    ...input,
    localId: crypto.randomUUID(),
    key: input.key ?? crypto.randomUUID(),
    state: 'pending',
    attempts: 0,
    createdAt: Date.now(),
  };
  await put('actions', action);
  await trySync();
  return action;
}

export async function trySync() {
  const actions = await getAll<QueuedAction>('actions');
  for (const action of actions.filter((item) => item.state !== 'rejected')) {
    try {
      const response = await fetch(actionUrl(action), {
        method: 'PATCH',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-FieldNode-CSRF': '1', 'Idempotency-Key': action.key },
        credentials: 'include',
        body: JSON.stringify(action.body),
      });
      if (response.ok) await remove('actions', action.localId);
      else if (response.status >= 500 || response.status === 408 || response.status === 429) {
        await put('actions', { ...action, state: 'retrying', attempts: action.attempts + 1, lastError: `HTTP ${response.status}` });
      } else {
        await put('actions', { ...action, state: 'rejected', attempts: action.attempts + 1, lastError: `HTTP ${response.status}` });
      }
    } catch {
      await put('actions', { ...action, state: 'retrying', attempts: action.attempts + 1, lastError: 'Falha de rede' });
    }
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => { void trySync(); });
}
