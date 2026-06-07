-- Step 9: Usage limits — regenerations tracking + atomic quota RPCs

ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS regenerations_used INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS regenerations_limit INTEGER NOT NULL DEFAULT 10,
    ADD COLUMN IF NOT EXISTS usage_period_start DATE NOT NULL DEFAULT date_trunc('month', NOW())::DATE;

-- Reset counters when a new billing month starts
CREATE OR REPLACE FUNCTION public._reset_usage_if_needed(user_uuid UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    month_start DATE := date_trunc('month', NOW())::DATE;
BEGIN
    UPDATE public.profiles
    SET
        analyses_used = 0,
        regenerations_used = 0,
        usage_period_start = month_start
    WHERE id = user_uuid
      AND usage_period_start < month_start;
END;
$$;

-- Returns current usage after applying monthly reset if needed
CREATE OR REPLACE FUNCTION public.get_usage_stats(user_uuid UUID)
RETURNS TABLE (
    analyses_used INTEGER,
    analyses_limit INTEGER,
    regenerations_used INTEGER,
    regenerations_limit INTEGER,
    plan TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    PERFORM public._reset_usage_if_needed(user_uuid);

    RETURN QUERY
    SELECT
        p.analyses_used,
        p.analyses_limit,
        p.regenerations_used,
        p.regenerations_limit,
        p.plan
    FROM public.profiles p
    WHERE p.id = user_uuid;
END;
$$;

-- Atomically consume one analysis credit; returns TRUE if allowed
CREATE OR REPLACE FUNCTION public.try_consume_analysis(user_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    updated INTEGER;
BEGIN
    PERFORM public._reset_usage_if_needed(user_uuid);

    UPDATE public.profiles
    SET analyses_used = analyses_used + 1
    WHERE id = user_uuid
      AND analyses_used < analyses_limit;

    GET DIAGNOSTICS updated = ROW_COUNT;
    RETURN updated > 0;
END;
$$;

-- Atomically consume one regeneration credit; returns TRUE if allowed
CREATE OR REPLACE FUNCTION public.try_consume_regeneration(user_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    updated INTEGER;
BEGIN
    PERFORM public._reset_usage_if_needed(user_uuid);

    UPDATE public.profiles
    SET regenerations_used = regenerations_used + 1
    WHERE id = user_uuid
      AND regenerations_used < regenerations_limit;

    GET DIAGNOSTICS updated = ROW_COUNT;
    RETURN updated > 0;
END;
$$;

-- Keep legacy RPC for backwards compatibility (no limit check)
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
