import { API_BASE_URL } from "@/lib/constants";
import { createClient } from "@/lib/supabase/client";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getAuthToken(): Promise<string | null> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}

function parseErrorMessage(payload: unknown): { message: string; code?: string } {
  if (!payload || typeof payload !== "object") {
    return { message: "Request failed" };
  }

  const body = payload as Record<string, unknown>;

  if (body.error && typeof body.error === "object") {
    const err = body.error as Record<string, unknown>;
    return {
      message: String(err.message ?? "Request failed"),
      code: err.code ? String(err.code) : undefined,
    };
  }

  return {
    message: String(body.detail ?? body.message ?? "Request failed"),
  };
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  if (!token) {
    throw new ApiError(401, "Not authenticated", "UNAUTHORIZED");
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const { message, code } = parseErrorMessage(payload);
    throw new ApiError(response.status, message, code);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
