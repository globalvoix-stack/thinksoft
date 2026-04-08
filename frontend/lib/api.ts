/**
 * Thinksoft API client — typed, token-aware, calls FastAPI /v1/* via Vite proxy.
 *
 * Usage:
 *   const { getToken } = useAuth();
 *   const api = makeApi(getToken);
 *   const projects = await api.projects.list();
 */

const BASE = '/v1';

export interface Project {
  id: string;
  clerk_user_id: string | null;
  name: string;
  industry: string | null;
  description: string | null;
  mode: string;
  is_starred: boolean;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  name: string;
  industry?: string;
  description?: string;
  mode?: 'light' | 'autonomous' | 'max';
  image_url?: string;
}

export interface Job {
  id: string;
  project_id: string;
  session_id: string;
  mode: string;
  status: string;
  progress: number;
  current_step: string | null;
  prompt: string;
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
}

export interface GeneratePayload {
  project_id: string;
  session_id?: string;
  prompt: string;
  mode?: 'light' | 'autonomous' | 'max';
  is_first_prompt?: boolean;
}

export interface GenerateResponse {
  job_id: string;
  mode: string;
  mismatch_suggestion: string | null;
}

export interface GeneratedFile {
  id: string;
  file_path: string;
  content: string;
  language: string | null;
  version: number;
}

export interface SseProgressEvent {
  type: 'progress' | 'done' | 'error' | 'heartbeat';
  job_id?: string;
  status?: string;
  progress?: number;
  current_step?: string | null;
  result?: Record<string, unknown>;
  error?: string;
}

// ── Internal helpers ──────────────────────────────────────────────────────────

type GetToken = () => Promise<string | null>;

async function authHeaders(getToken: GetToken): Promise<Record<string, string>> {
  const token = await getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function req<T>(
  getToken: GetToken,
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: await authHeaders(getToken),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as any).detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Public factory ────────────────────────────────────────────────────────────

export function makeApi(getToken: GetToken) {
  return {
    projects: {
      list: () =>
        req<Project[]>(getToken, 'GET', '/projects'),

      create: (payload: CreateProjectPayload) =>
        req<Project>(getToken, 'POST', '/projects', payload),

      toggleStar: (projectId: string) =>
        req<Project>(getToken, 'PATCH', `/projects/${projectId}/star`),

      delete: (projectId: string) =>
        req<void>(getToken, 'DELETE', `/projects/${projectId}`),
    },

    generate: (payload: GeneratePayload) =>
      req<GenerateResponse>(getToken, 'POST', '/generate', payload),

    files: {
      forProject: (projectId: string) =>
        req<GeneratedFile[]>(getToken, 'GET', `/files?project_id=${projectId}`),
      forJob: (jobId: string) =>
        req<GeneratedFile[]>(getToken, 'GET', `/files/job/${jobId}`),
    },

    /**
     * Stream SSE events for a job. Calls the callback with each parsed event.
     * Returns a cleanup function — call it to abort the stream.
     */
    streamJob(
      projectId: string,
      jobId: string,
      onEvent: (event: SseProgressEvent) => void,
      getTokenFn: GetToken,
    ): () => void {
      let aborted = false;
      const controller = new AbortController();

      (async () => {
        const token = await getTokenFn();
        const url = `/v1/stream/${jobId}?project_id=${projectId}`;
        const response = await fetch(url, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          signal: controller.signal,
        });
        if (!response.ok || !response.body) return;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (!aborted) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() ?? '';

          let eventType = 'message';
          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventType = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
              const data = line.slice(5).trim();
              if (!data || data === '') continue;
              try {
                const parsed = JSON.parse(data);
                onEvent({ type: eventType as SseProgressEvent['type'], ...parsed });
              } catch {
                // ignore malformed frames
              }
            }
          }
        }
      })().catch(() => {/* aborted */});

      return () => {
        aborted = true;
        controller.abort();
      };
    },
  };
}
