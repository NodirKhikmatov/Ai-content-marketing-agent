import type { AuthError } from "@supabase/supabase-js";

const RATE_LIMIT_CODES = new Set([
  "over_request_rate_limit",
  "over_email_send_rate_limit",
  "over_sms_send_rate_limit",
]);

export function getAuthErrorMessage(error: AuthError | Error | null): string {
  if (!error) return "Something went wrong. Please try again.";

  const authError = error as AuthError;
  const status = authError.status;
  const code = authError.code ?? "";
  const message = error.message ?? "";

  if (
    status === 429 ||
    RATE_LIMIT_CODES.has(code) ||
    /rate limit/i.test(message)
  ) {
    return "Too many attempts. Supabase temporarily blocked requests — wait 15–60 minutes, then try again. For local dev, you can disable email confirmation in Supabase → Authentication → Providers → Email.";
  }

  if (status === 422 && code === "email_address_invalid") {
    return "That email address is not allowed. Use a real email address (Supabase blocks some test domains like example.com).";
  }

  if (code === "user_already_registered") {
    return "An account with this email already exists. Try signing in instead.";
  }

  return message || "Authentication failed. Please try again.";
}
