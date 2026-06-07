import { apiClient } from "./api-client";

export interface AnalysisJob {
  id: string;
  project_id: string;
  website_id: string | null;
  status: "queued" | "processing" | "completed" | "failed" | "cancelled";
  progress: number;
  current_step?: string | null;
  steps_completed: string[];
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface AnalysisOptions {
  calendar_days?: number;
  competitor_count?: number;
  keyword_count?: number;
  generate_assets?: boolean;
  /** Max items to generate AI assets for; 0 = all calendar items */
  sample_asset_count?: number;
}

/** Startup-friendly defaults (~$0.15–0.30 per run). */
export const DEFAULT_ANALYSIS_OPTIONS: AnalysisOptions = {
  calendar_days: 7,
  competitor_count: 4,
  keyword_count: 10,
  generate_assets: true,
  sample_asset_count: 3,
};

export const PIPELINE_STEPS = [
  "website_analysis",
  "competitor_research",
  "audience_research",
  "seo_strategy",
  "content_planning",
  "asset_generation",
] as const;

export const STEP_LABELS: Record<string, string> = {
  website_analysis: "Analyzing website",
  competitor_research: "Researching competitors",
  audience_research: "Building audience personas",
  seo_strategy: "Creating SEO strategy",
  content_planning: "Planning content calendar",
  asset_generation: "Generating content assets",
};

export const analysisService = {
  start: (projectId: string, websiteId: string, options?: AnalysisOptions) =>
    apiClient<AnalysisJob>(`/projects/${projectId}/analysis`, {
      method: "POST",
      body: JSON.stringify({ website_id: websiteId, options }),
    }),

  getActiveJob: (projectId: string) =>
    apiClient<AnalysisJob>(`/projects/${projectId}/analysis/active`),

  getJob: (jobId: string) => apiClient<AnalysisJob>(`/jobs/${jobId}`),

  getSteps: (projectId: string) =>
    apiClient<{ steps: string[]; labels: Record<string, string> }>(
      `/projects/${projectId}/analysis/steps`
    ),
};
