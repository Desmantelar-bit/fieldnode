import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const SESSION_COOKIE = 'fieldnode_session';
const API_BASE = (process.env.FIELDNODE_SERVER_API_URL || 'http://127.0.0.1:8000/api').replace(/\/+$/, '');
const localFrontendOrigins = process.env.NODE_ENV === 'production'
  ? []
  : ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3005', 'http://127.0.0.1:3005'];
const configuredFrontendOrigins = [
  ...(process.env.FIELDNODE_FRONTEND_URL || '')
  .split(',')
  .map((value) => {
    try { return new URL(value.trim()).origin; } catch { return ''; }
  })
  .filter(Boolean),
  ...localFrontendOrigins,
];

function json(body: unknown, status = 200, headers?: HeadersInit) {
  return Response.json(body, { status, headers });
}

async function proxyInternal(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const endpoint = path.join('/');
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
    const origin = request.headers.get('origin');
    if (origin) {
      let normalizedOrigin = '';
      try { normalizedOrigin = new URL(origin).origin; } catch { /* Reject malformed origins below. */ }
      if (!normalizedOrigin || (normalizedOrigin !== request.nextUrl.origin && !configuredFrontendOrigins.includes(normalizedOrigin))) {
        return json({ detail: 'Origem não permitida.' }, 403);
      }
    }
  }

  const cookieStore = await cookies();
  const sessionToken = cookieStore.get(SESSION_COOKIE)?.value;
  const headers = new Headers();
  for (const name of ['accept', 'content-type', 'x-api-key']) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  if (sessionToken && endpoint !== 'auth/login' && endpoint !== 'auth/register') {
    headers.set('authorization', `Token ${sessionToken}`);
  }
  if (endpoint === 'auth/logout' && !sessionToken) return json({ message: 'Sessão encerrada.' });

  const body = ['GET', 'HEAD'].includes(request.method) ? undefined : await request.arrayBuffer();
  let upstream: Response;
  try {
    upstream = await fetch(`${API_BASE}/${endpoint}/${request.nextUrl.search}`, {
      method: request.method,
      headers,
      body,
      cache: 'no-store',
      redirect: 'manual',
    });
  } catch {
    return json({ detail: 'Serviço indisponível.' }, 503);
  }

  const responseHeaders = new Headers(upstream.headers);
  responseHeaders.delete('content-encoding');
  responseHeaders.delete('content-length');

  if (endpoint === 'auth/login' || endpoint === 'auth/register') {
    const payload = await upstream.json().catch(() => ({})) as Record<string, unknown>;
    const token = typeof payload.token === 'string' ? payload.token : '';
    if (!upstream.ok || !token) return json(payload, upstream.status, responseHeaders);
    let user = payload.user;
    if (!user && endpoint === 'auth/login') {
      try {
        const me = await fetch(`${API_BASE}/auth/me/`, {
          headers: { Authorization: `Token ${token}`, Accept: 'application/json' },
          cache: 'no-store',
        });
        if (me.ok) user = await me.json();
      } catch { /* Login remains valid if profile enrichment is unavailable. */ }
    }
    const result = NextResponse.json({ user: user ?? { username: payload.username ?? '' } }, { status: upstream.status, headers: responseHeaders });
    result.cookies.set({
      name: SESSION_COOKIE,
      value: token,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: Math.max(60, Number(payload.expires_in) || 24 * 60 * 60),
    });
    return result;
  }

  if (endpoint === 'auth/logout') {
    const response = new NextResponse(upstream.body, { status: upstream.status, headers: responseHeaders });
    response.cookies.delete(SESSION_COOKIE);
    return response;
  }

  return new NextResponse(upstream.body, { status: upstream.status, headers: responseHeaders });
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  try {
    return await proxyInternal(request, context);
  } catch (error) {
    console.error('API proxy failure', error);
    return json({ detail: 'Falha interna no proxy da API.' }, 500);
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
