export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          email: string;
          full_name: string | null;
          avatar_url: string | null;
          plan: "free" | "pro" | "team" | "agency";
          analyses_used: number;
          analyses_limit: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          email: string;
          full_name?: string | null;
          avatar_url?: string | null;
          plan?: "free" | "pro" | "team" | "agency";
          analyses_used?: number;
          analyses_limit?: number;
        };
        Update: Partial<Database["public"]["Tables"]["profiles"]["Insert"]>;
      };
      projects: {
        Row: {
          id: string;
          user_id: string;
          name: string;
          description: string | null;
          status: "draft" | "analyzing" | "active" | "archived";
          metadata: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          name: string;
          description?: string | null;
          status?: "draft" | "analyzing" | "active" | "archived";
          metadata?: Json;
        };
        Update: Partial<Database["public"]["Tables"]["projects"]["Insert"]>;
      };
      websites: {
        Row: {
          id: string;
          project_id: string;
          url: string;
          status: "pending" | "crawling" | "analyzed" | "failed";
          business_type: string | null;
          products_services: Json;
          target_audience: string | null;
          unique_value_proposition: string | null;
          brand_tone: string | null;
          raw_crawl_data: Json | null;
          analysis_result: Json | null;
          analyzed_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          project_id: string;
          url: string;
          status?: "pending" | "crawling" | "analyzed" | "failed";
          business_type?: string | null;
          products_services?: Json;
          target_audience?: string | null;
          unique_value_proposition?: string | null;
          brand_tone?: string | null;
        };
        Update: Partial<Database["public"]["Tables"]["websites"]["Insert"]>;
      };
      content_plans: {
        Row: {
          id: string;
          project_id: string;
          name: string;
          start_date: string;
          end_date: string;
          status: "draft" | "active" | "completed" | "archived";
          pillars: Json;
          channel_mix: Json;
          metadata: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          project_id: string;
          name?: string;
          start_date: string;
          end_date: string;
          status?: "draft" | "active" | "completed" | "archived";
          pillars?: Json;
          channel_mix?: Json;
          metadata?: Json;
        };
        Update: Partial<Database["public"]["Tables"]["content_plans"]["Insert"]>;
      };
      content_items: {
        Row: {
          id: string;
          project_id: string;
          content_plan_id: string | null;
          title: string;
          description: string | null;
          channel: string;
          format: string;
          scheduled_date: string | null;
          status: string;
          body: string | null;
          keyword_targets: Json;
          metadata: Json;
          sort_order: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          project_id: string;
          content_plan_id?: string | null;
          title: string;
          description?: string | null;
          channel: string;
          format: string;
          scheduled_date?: string | null;
          status?: string;
          body?: string | null;
          keyword_targets?: Json;
          metadata?: Json;
          sort_order?: number;
        };
        Update: Partial<Database["public"]["Tables"]["content_items"]["Insert"]>;
      };
      analysis_jobs: {
        Row: {
          id: string;
          project_id: string;
          website_id: string | null;
          status: "queued" | "processing" | "completed" | "failed" | "cancelled";
          progress: number;
          current_step: string | null;
          steps_completed: Json;
          options: Json;
          error_message: string | null;
          started_at: string | null;
          completed_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          project_id: string;
          website_id?: string | null;
          status?: "queued" | "processing" | "completed" | "failed" | "cancelled";
          progress?: number;
          current_step?: string | null;
          steps_completed?: Json;
          options?: Json;
        };
        Update: Partial<Database["public"]["Tables"]["analysis_jobs"]["Insert"]>;
      };
    };
    Views: Record<string, never>;
    Functions: {
      user_owns_project: { Args: { project_uuid: string }; Returns: boolean };
      increment_analyses_used: { Args: { user_uuid: string }; Returns: undefined };
    };
  };
};

export type Profile = Database["public"]["Tables"]["profiles"]["Row"];
export type Project = Database["public"]["Tables"]["projects"]["Row"];
export type Website = Database["public"]["Tables"]["websites"]["Row"];
export type ContentPlan = Database["public"]["Tables"]["content_plans"]["Row"];
export type ContentItem = Database["public"]["Tables"]["content_items"]["Row"];
export type AnalysisJob = Database["public"]["Tables"]["analysis_jobs"]["Row"];
