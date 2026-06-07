"""Backward-compatible import — prefer database.supabase.get_supabase()."""

from database.supabase import SupabaseService, get_supabase

__all__ = ["SupabaseService", "get_supabase", "get_supabase_client"]


def get_supabase_client():
    return get_supabase().client
