import { apiClient } from "./api-client";

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  plan: string;
  analyses_used: number;
  analyses_limit: number;
  created_at: string;
}

export interface UsageStats {
  analyses_used: number;
  analyses_limit: number;
  regenerations_used: number;
  regenerations_limit: number;
  plan: string;
}

export const userService = {
  getProfile: () => apiClient<UserProfile>("/users/me"),

  updateProfile: (data: { full_name?: string }) =>
    apiClient<UserProfile>("/users/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getUsage: () => apiClient<UsageStats>("/users/me/usage"),
};
