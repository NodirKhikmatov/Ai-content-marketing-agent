-- Refund usage credits when a paid action fails (e.g. analysis pipeline error)

CREATE OR REPLACE FUNCTION public.refund_analysis(user_uuid UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    UPDATE public.profiles
    SET analyses_used = GREATEST(analyses_used - 1, 0)
    WHERE id = user_uuid;
END;
$$;

CREATE OR REPLACE FUNCTION public.refund_regeneration(user_uuid UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    UPDATE public.profiles
    SET regenerations_used = GREATEST(regenerations_used - 1, 0)
    WHERE id = user_uuid;
END;
$$;
