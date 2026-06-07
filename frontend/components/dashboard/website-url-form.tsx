"use client";

import { useState } from "react";
import { CheckCircle2, Globe, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { validateWebsiteUrl } from "@/lib/validation/url";
import { ApiError } from "@/services/api-client";
import { websitesService, type Website } from "@/services/websites";

interface WebsiteUrlFormProps {
  projectId: string;
  onSubmitted: (website: Website) => void;
}

export function WebsiteUrlForm({ projectId, onSubmitted }: WebsiteUrlFormProps) {
  const [url, setUrl] = useState("");
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleUrlChange = (value: string) => {
    setUrl(value);
    setFieldError(null);
    setSubmitError(null);

    if (value.trim()) {
      const result = validateWebsiteUrl(value);
      setPreview(result.valid ? result.normalized : null);
      if (!result.valid && value.includes(".")) {
        setFieldError(result.error ?? null);
      }
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    const validation = validateWebsiteUrl(url);
    if (!validation.valid) {
      setFieldError(validation.error ?? "Invalid URL");
      return;
    }

    setLoading(true);
    try {
      const website = await websitesService.submit(projectId, validation.normalized);
      onSubmitted(website);
      setUrl("");
      setPreview(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setSubmitError(err.message);
      } else {
        setSubmitError(err instanceof Error ? err.message : "Failed to submit URL");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5 text-primary" />
          Submit Your Website
        </CardTitle>
        <CardDescription>
          Enter your website URL. We&apos;ll analyze it to build your marketing strategy and content
          plan.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="website-url">Website URL</Label>
            <Input
              id="website-url"
              type="text"
              inputMode="url"
              autoComplete="url"
              placeholder="yourcompany.com or https://yourcompany.com"
              value={url}
              onChange={(e) => handleUrlChange(e.target.value)}
              aria-invalid={!!fieldError}
              aria-describedby={fieldError ? "url-error" : preview ? "url-preview" : undefined}
            />
            {preview && !fieldError && (
              <p id="url-preview" className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                Will submit as: <span className="font-medium text-foreground">{preview}</span>
              </p>
            )}
            {fieldError && (
              <p id="url-error" className="text-sm text-destructive">
                {fieldError}
              </p>
            )}
          </div>

          {submitError && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {submitError}
            </p>
          )}

          <Button type="submit" disabled={loading || !url.trim()} className="w-full">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Submitting...
              </>
            ) : (
              "Submit Website URL"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
