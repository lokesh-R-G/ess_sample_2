import { Config } from '../config';
import { Storage } from '../utils/storage';

const TOKEN_KEY = 'ess_auth_token';
const USER_KEY = 'ess_auth_user';

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function setAuthToken(token: string, user?: any) {
  await Storage.setItem(TOKEN_KEY, token);
  if (user) {
    await Storage.setItem(USER_KEY, JSON.stringify(user));
  }
}

export async function getAuthToken(): Promise<string | null> {
  return Storage.getItem(TOKEN_KEY);
}

export async function clearAuthStorage() {
  await Storage.removeItem(TOKEN_KEY);
  await Storage.removeItem(USER_KEY);
}

export async function getStoredUser<T>(): Promise<T | null> {
  const raw = await Storage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: any;
  headers?: Record<string, string>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = await getAuthToken();
  const headers: Record<string, string> = {
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${Config.API_BASE_URL}${path}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), Config.TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers,
      body: options.body ? (options.body instanceof FormData ? options.body : JSON.stringify(options.body)) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}`;
      let errorData = null;
      try {
        errorData = await response.json();
        if (errorData && typeof errorData === 'object' && errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        errorMessage = await response.text();
      }

      if (response.status === 401) {
        await clearAuthStorage();
      }

      throw new ApiError(errorMessage, response.status, errorData);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as T;
    }
    return (await response.text()) as unknown as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new ApiError('Request timed out. Please check your network connection.', 408);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message || 'Network request failed', 0);
  }
}

export const api = {
  get: <T>(path: string, headers?: Record<string, string>) => request<T>(path, { method: 'GET', headers }),
  post: <T>(path: string, body?: any, headers?: Record<string, string>) => request<T>(path, { method: 'POST', body, headers }),
  put: <T>(path: string, body?: any, headers?: Record<string, string>) => request<T>(path, { method: 'PUT', body, headers }),
  patch: <T>(path: string, body?: any, headers?: Record<string, string>) => request<T>(path, { method: 'PATCH', body, headers }),
  delete: <T>(path: string, headers?: Record<string, string>) => request<T>(path, { method: 'DELETE', headers }),
};
