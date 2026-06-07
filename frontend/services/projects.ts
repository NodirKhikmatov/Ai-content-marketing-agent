import { apiClient } from "./api-client";

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  stats?: {
    content_items: number;
    approved_items: number;
    keywords: number;
    competitors: number;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export const projectsService = {
  list: (page = 1, limit = 20) =>
    apiClient<PaginatedResponse<Project>>(`/projects?page=${page}&limit=${limit}`),

  get: (id: string) => apiClient<Project>(`/projects/${id}`),

  create: (data: { name: string; description?: string }) =>
    apiClient<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Partial<{ name: string; description: string; status: string }>) =>
    apiClient<Project>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiClient<void>(`/projects/${id}`, { method: "DELETE" }),

  getCompetitors: (projectId: string) =>
    apiClient<{ items: Competitor[] }>(`/projects/${projectId}/competitors`),

  getContentItems: (
    projectId: string,
    params?: { channel?: string; status?: string; page?: number; limit?: number }
  ) => {
    const search = new URLSearchParams();
    if (params?.channel) search.set("channel", params.channel);
    if (params?.status) search.set("status", params.status);
    if (params?.page) search.set("page", String(params.page));
    if (params?.limit) search.set("limit", String(params.limit));
    const qs = search.toString();
    return apiClient<PaginatedResponse<ContentItem>>(
      `/projects/${projectId}/content-items${qs ? `?${qs}` : ""}`
    );
  },

  getContentItem: (projectId: string, itemId: string) =>
    apiClient<ContentItemDetail>(`/projects/${projectId}/content-items/${itemId}`),

  updateContentItem: (
    projectId: string,
    itemId: string,
    data: Partial<{
      title: string;
      description: string;
      body: string;
      status: string;
      scheduled_date: string;
    }>
  ) =>
    apiClient<ContentItem>(`/projects/${projectId}/content-items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  regenerateContentItem: (
    projectId: string,
    itemId: string,
    data?: { instructions?: string }
  ) =>
    apiClient<ContentItemDetail>(`/projects/${projectId}/content-items/${itemId}/regenerate`, {
      method: "POST",
      body: JSON.stringify(data ?? {}),
    }),

  getContentPlans: (projectId: string) =>
    apiClient<{ items: ContentPlan[] }>(`/projects/${projectId}/content-plans`),

  getSEOKeywords: (projectId: string) =>
    apiClient<{ items: SEOKeyword[]; clusters: string[]; summary: Record<string, number> }>(
      `/projects/${projectId}/seo-keywords`
    ),
};

export interface Competitor {
  id: string;
  name: string;
  url: string;
  strengths: string[];
  weaknesses: string[];
  content_gaps: string[];
  positioning_summary?: string;
}

export interface ContentItem {
  id: string;
  title: string;
  description?: string;
  channel: string;
  format: string;
  scheduled_date?: string;
  status: string;
  body?: string;
  keyword_targets: string[];
}

export interface GeneratedAsset {
  id: string;
  asset_type: string;
  platform?: string;
  content: string;
  version: number;
}

export interface ContentItemDetail extends ContentItem {
  assets: GeneratedAsset[];
}

export interface ContentPlan {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
  pillars: string[];
  channel_mix: Record<string, number>;
}

export interface SEOKeyword {
  id: string;
  keyword: string;
  search_volume?: number;
  difficulty?: number;
  intent?: string;
  cluster?: string;
  priority: string;
  content_suggestions: string[];
}

export const jobsService = {
  getStatus: (jobId: string) =>
    apiClient<{
      id: string;
      status: string;
      progress: number;
      current_step?: string | null;
      steps_completed: string[];
      error_message?: string | null;
    }>(`/jobs/${jobId}`),
};
