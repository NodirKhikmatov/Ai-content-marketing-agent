import { createClient } from "@/lib/supabase/client";

export const authService = {
  signInWithPassword: async (email: string, password: string) => {
    const supabase = createClient();
    return supabase.auth.signInWithPassword({ email, password });
  },

  signUp: async (email: string, password: string, fullName: string) => {
    const supabase = createClient();
    return supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName },
        emailRedirectTo: `${window.location.origin}/auth/callback?next=/dashboard`,
      },
    });
  },

  signInWithGoogle: async () => {
    const supabase = createClient();
    return supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?next=/dashboard`,
      },
    });
  },

  resetPassword: async (email: string) => {
    const supabase = createClient();
    return supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=/dashboard/settings`,
    });
  },

  signOut: async () => {
    const supabase = createClient();
    return supabase.auth.signOut();
  },
};
