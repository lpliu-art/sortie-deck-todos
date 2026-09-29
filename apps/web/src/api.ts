import { ApiError } from "./types";

const API = "";

function authHeaders(token?: string, extra: HeadersInit = {}): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

type ApiOptions = RequestInit & { token?: string };

export async function api<T = unknown>(path: string, { token, ...options }: ApiOptions = {}): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: authHeaders(token, options.headers),
  });
  if (res.status === 401) {
    throw new ApiError("unauthorized", 401);
  }
  if (!res.ok) throw new ApiError((await res.text()) || res.statusText, res.status);
  return res.json() as Promise<T>;
}
