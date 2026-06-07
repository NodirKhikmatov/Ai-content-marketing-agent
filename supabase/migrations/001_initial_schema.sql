-- AI Content Marketing Agent — MVP Database Schema
-- Apply via Supabase Dashboard → SQL Editor, or: supabase db push

-- ---------------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- profiles (extends auth.users)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    plan TEXT NOT NULL DEFAULT 'free'
        CHECK (plan IN ('free', 'pro', 'team', 'agency')),
    analyses_used INTEGER NOT NULL DEFAULT 0,
    analyses_limit INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- projects
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'analyzing', 'active', 'archived')),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON public.projects(status);

-- ---------------------------------------------------------------------------
-- websites
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'crawling', 'analyzed', 'failed')),
    business_type TEXT,
    products_services JSONB NOT NULL DEFAULT '[]',
    target_audience TEXT,
    unique_value_proposition TEXT,
    brand_tone TEXT,
    raw_crawl_data JSONB,
    analysis_result JSONB,
    analyzed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT websites_url_unique_per_project UNIQUE (project_id, url)
);

CREATE INDEX IF NOT EXISTS idx_websites_project_id ON public.websites(project_id);

-- ---------------------------------------------------------------------------
-- competitors
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    strengths JSONB NOT NULL DEFAULT '[]',
    weaknesses JSONB NOT NULL DEFAULT '[]',
    content_gaps JSONB NOT NULL DEFAULT '[]',
    positioning_summary TEXT,
    social_presence JSONB NOT NULL DEFAULT '{}',
    analysis_result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competitors_project_id ON public.competitors(project_id);

-- ---------------------------------------------------------------------------
-- content_plans
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.content_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT '30-Day Content Plan',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'completed', 'archived')),
    pillars JSONB NOT NULL DEFAULT '[]',
    channel_mix JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_plans_project_id ON public.content_plans(project_id);

-- ---------------------------------------------------------------------------
-- content_items
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.content_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_plan_id UUID REFERENCES public.content_plans(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    channel TEXT NOT NULL
        CHECK (channel IN ('blog', 'linkedin', 'instagram', 'tiktok', 'youtube', 'twitter', 'facebook')),
    format TEXT NOT NULL
        CHECK (format IN ('post', 'article', 'video', 'reel', 'story', 'carousel', 'thread')),
    scheduled_date DATE,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'generating', 'ready', 'approved', 'rejected', 'published', 'scheduled')),
    body TEXT,
    keyword_targets JSONB NOT NULL DEFAULT '[]',
    metadata JSONB NOT NULL DEFAULT '{}',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_items_project_id ON public.content_items(project_id);
CREATE INDEX IF NOT EXISTS idx_content_items_plan_id ON public.content_items(content_plan_id);
CREATE INDEX IF NOT EXISTS idx_content_items_scheduled_date ON public.content_items(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_content_items_channel ON public.content_items(channel);
CREATE INDEX IF NOT EXISTS idx_content_items_status ON public.content_items(status);

-- ---------------------------------------------------------------------------
-- seo_keywords
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.seo_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    search_volume INTEGER,
    difficulty INTEGER CHECK (difficulty >= 0 AND difficulty <= 100),
    intent TEXT CHECK (intent IN ('informational', 'commercial', 'transactional', 'navigational')),
    cluster TEXT,
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    content_suggestions JSONB NOT NULL DEFAULT '[]',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT seo_keywords_unique_per_project UNIQUE (project_id, keyword)
);

CREATE INDEX IF NOT EXISTS idx_seo_keywords_project_id ON public.seo_keywords(project_id);
CREATE INDEX IF NOT EXISTS idx_seo_keywords_cluster ON public.seo_keywords(cluster);
CREATE INDEX IF NOT EXISTS idx_seo_keywords_priority ON public.seo_keywords(priority);

-- ---------------------------------------------------------------------------
-- generated_assets
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.generated_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_item_id UUID REFERENCES public.content_items(id) ON DELETE CASCADE,
    asset_type TEXT NOT NULL
        CHECK (asset_type IN ('caption', 'script', 'blog_outline', 'image_prompt', 'hashtags', 'hook', 'cta')),
    platform TEXT,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_assets_project_id ON public.generated_assets(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_assets_content_item_id ON public.generated_assets(content_item_id);
CREATE INDEX IF NOT EXISTS idx_generated_assets_type ON public.generated_assets(asset_type);

-- ---------------------------------------------------------------------------
-- analysis_jobs
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    website_id UUID REFERENCES public.websites(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    progress INTEGER NOT NULL DEFAULT 0
        CHECK (progress >= 0 AND progress <= 100),
    current_step TEXT,
    steps_completed JSONB NOT NULL DEFAULT '[]',
    options JSONB NOT NULL DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_project_id ON public.analysis_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status ON public.analysis_jobs(status);

-- ---------------------------------------------------------------------------
-- updated_at trigger
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'profiles', 'projects', 'websites', 'competitors',
        'content_plans', 'content_items', 'seo_keywords',
        'generated_assets', 'analysis_jobs'
    ]
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_%I_updated_at ON public.%I;
             CREATE TRIGGER set_%I_updated_at
             BEFORE UPDATE ON public.%I
             FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();',
            t, t, t, t
        );
    END LOOP;
END;
$$;

-- ---------------------------------------------------------------------------
-- auto-create profile on signup
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.raw_user_meta_data->>'avatar_url'
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ---------------------------------------------------------------------------
-- project ownership helper (used by RLS)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.user_owns_project(project_uuid UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.projects
        WHERE id = project_uuid AND user_id = auth.uid()
    );
$$;

-- increment analysis usage (called by backend service role)
CREATE OR REPLACE FUNCTION public.increment_analyses_used(user_uuid UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    UPDATE public.profiles
    SET analyses_used = analyses_used + 1
    WHERE id = user_uuid;
END;
$$;

-- ---------------------------------------------------------------------------
-- row level security
-- ---------------------------------------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.websites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seo_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_jobs ENABLE ROW LEVEL SECURITY;

-- profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- projects
DROP POLICY IF EXISTS "Users can view own projects" ON public.projects;
CREATE POLICY "Users can view own projects"
    ON public.projects FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create projects" ON public.projects;
CREATE POLICY "Users can create projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own projects" ON public.projects;
CREATE POLICY "Users can update own projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own projects" ON public.projects;
CREATE POLICY "Users can delete own projects"
    ON public.projects FOR DELETE
    USING (auth.uid() = user_id);

-- child tables (explicit USING + WITH CHECK for INSERT safety)
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'websites', 'competitors', 'content_plans', 'content_items',
        'seo_keywords', 'generated_assets', 'analysis_jobs'
    ]
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "Users manage own project rows" ON public.%I;', tbl);
        EXECUTE format(
            'CREATE POLICY "Users manage own project rows"
             ON public.%I
             FOR ALL
             USING (public.user_owns_project(project_id))
             WITH CHECK (public.user_owns_project(project_id));',
            tbl
        );
    END LOOP;
END;
$$;

-- ---------------------------------------------------------------------------
-- realtime (optional — enable project status updates in dashboard)
-- ---------------------------------------------------------------------------
ALTER PUBLICATION supabase_realtime ADD TABLE public.analysis_jobs;
