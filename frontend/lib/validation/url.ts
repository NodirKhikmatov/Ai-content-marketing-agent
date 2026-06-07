export interface UrlValidationResult {
  valid: boolean;
  normalized: string;
  error?: string;
}

/**
 * Normalize user input to a canonical URL (adds https:// if missing).
 */
export function normalizeUrl(raw: string): string {
  let value = raw.trim();
  if (!value) return "";

  if (!/^https?:\/\//i.test(value)) {
    value = `https://${value}`;
  }

  try {
    const parsed = new URL(value);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      throw new Error("URL must use http or https");
    }
    if (!parsed.hostname) {
      throw new Error("Invalid domain");
    }
    return parsed.origin;
  } catch {
    throw new Error("Invalid URL format");
  }
}

const BLOCKED_HOSTS = new Set(["localhost", "0.0.0.0"]);

/**
 * Validate a website URL before submission.
 */
export function validateWebsiteUrl(raw: string): UrlValidationResult {
  if (!raw.trim()) {
    return { valid: false, normalized: "", error: "URL is required" };
  }

  try {
    const normalized = normalizeUrl(raw);
    const parsed = new URL(normalized);
    const host = parsed.hostname.toLowerCase();

    if (BLOCKED_HOSTS.has(host)) {
      return { valid: false, normalized: "", error: "This URL is not allowed" };
    }

    if (host.endsWith(".local")) {
      return { valid: false, normalized: "", error: "Local URLs are not allowed" };
    }

    // Basic domain check — must contain a dot (e.g. example.com)
    if (!host.includes(".") && host !== "localhost") {
      return { valid: false, normalized: "", error: "Enter a valid domain (e.g. yourcompany.com)" };
    }

    return { valid: true, normalized };
  } catch (err) {
    return {
      valid: false,
      normalized: "",
      error: err instanceof Error ? err.message : "Invalid URL",
    };
  }
}
