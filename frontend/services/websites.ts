import { apiClient } from "./api-client";

export interface Website {
  id: string;
  project_id: string;
  url: string;
  status: "pending" | "crawling" | "analyzed" | "failed";
  business_type?: string | null;
  products_services?: string[];
  target_audience?: string | null;
  unique_value_proposition?: string | null;
  brand_tone?: string | null;
  analyzed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export const websitesService = {
  list: (projectId: string) =>
    apiClient<{ items: Website[] }>(`/projects/${projectId}/websites`),

  getPrimary: (projectId: string) =>
    apiClient<Website>(`/projects/${projectId}/websites/primary`),

  get: (projectId: string, websiteId: string) =>
    apiClient<Website>(`/projects/${projectId}/websites/${websiteId}`),

  submit: (projectId: string, url: string) =>
    apiClient<Website>(`/projects/${projectId}/websites`, {
      method: "POST",
      body: JSON.stringify({ url }),
    }),
};
