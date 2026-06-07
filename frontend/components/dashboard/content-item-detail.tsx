"use client";

import { useEffect, useState } from "react";
import { Check, Loader2, RefreshCw, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { isRegenerationAllowed } from "@/components/dashboard/usage-meter";
import { getChannelLabel, getStatusLabel, getStatusStyle } from "@/lib/content-utils";
import { formatDate } from "@/lib/utils";
import { ApiError } from "@/services/api-client";
import { projectsService, type ContentItemDetail } from "@/services/projects";
import { userService, type UsageStats } from "@/services/user";

interface ContentItemDetailPanelProps {
  projectId: string;
  itemId: string;
  onUpdated?: (item: ContentItemDetail) => void;
}

const ASSET_LABELS: Record<string, string> = {
  caption: "Caption",
  script: "Script",
  blog_outline: "Blog outline",
  image_prompt: "Image prompt",
  hashtags: "Hashtags",
  hook: "Hook",
  cta: "CTA",
};

export function ContentItemDetailPanel({
  projectId,
  itemId,
  onUpdated,
}: ContentItemDetailPanelProps) {
  const [item, setItem] = useState<ContentItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editBody, setEditBody] = useState("");
  const [regenInstructions, setRegenInstructions] = useState("");
  const [usage, setUsage] = useState<UsageStats | null>(null);

  useEffect(() => {
    userService
      .getUsage()
      .then(setUsage)
      .catch(() => setUsage(null));
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await projectsService.getContentItem(projectId, itemId);
        if (!cancelled) {
          setItem(data);
          setEditBody(data.body || "");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load content");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [projectId, itemId]);

  const handleSaveBody = async () => {
    if (!item) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await projectsService.updateContentItem(projectId, itemId, {
        body: editBody,
      });
      const detail = { ...item, ...updated };
      setItem(detail);
      onUpdated?.(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleStatus = async (status: string) => {
    if (!item) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await projectsService.updateContentItem(projectId, itemId, { status });
      const detail = { ...item, ...updated };
      setItem(detail);
      onUpdated?.(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    } finally {
      setSaving(false);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    setError(null);
    try {
      const detail = await projectsService.regenerateContentItem(projectId, itemId, {
        instructions: regenInstructions || undefined,
      });
      setItem(detail);
      setEditBody(detail.body || "");
      onUpdated?.(detail);
      if (usage) {
        setUsage({ ...usage, regenerations_used: usage.regenerations_used + 1 });
      }
    } catch (err) {
      if (err instanceof ApiError && err.code === "QUOTA_EXCEEDED") {
        setError(err.message);
        userService.getUsage().then(setUsage).catch(() => undefined);
      } else {
        setError(err instanceof Error ? err.message : "Regeneration failed");
      }
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <Card className="sticky top-8">
        <CardContent className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  if (!item) {
    return (
      <Card className="sticky top-8">
        <CardContent className="py-12 text-center text-muted-foreground">
          {error || "Content not found"}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="sticky top-8 h-fit">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>{item.title}</CardTitle>
            <CardDescription className="mt-1 capitalize">
              {getChannelLabel(item.channel)} · {item.format}
              {item.scheduled_date && ` · ${formatDate(item.scheduled_date)}`}
            </CardDescription>
          </div>
          <span
            className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${getStatusStyle(item.status)}`}
          >
            {getStatusLabel(item.status)}
          </span>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {item.description && (
          <p className="text-sm text-muted-foreground">{item.description}</p>
        )}

        {item.keyword_targets.length > 0 && (
          <div>
            <p className="mb-1 text-sm font-medium">Target keywords</p>
            <div className="flex flex-wrap gap-1">
              {item.keyword_targets.map((kw) => (
                <Badge key={kw} variant="draft">
                  {kw}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-2">
          <p className="text-sm font-medium">Content body</p>
          <Textarea
            value={editBody}
            onChange={(e) => setEditBody(e.target.value)}
            rows={8}
            placeholder="Generated caption or script will appear here..."
            className="font-mono text-sm"
          />
          <Button size="sm" onClick={handleSaveBody} disabled={saving || editBody === item.body}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save edits"}
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleStatus("approved")}
            disabled={saving || item.status === "approved"}
          >
            <Check className="h-4 w-4" />
            Approve
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleStatus("rejected")}
            disabled={saving || item.status === "rejected"}
          >
            <X className="h-4 w-4" />
            Reject
          </Button>
        </div>

        <div className="space-y-2 rounded-lg border p-3">
          <p className="text-sm font-medium">Regenerate assets</p>
          {usage && !isRegenerationAllowed(usage) && (
            <p className="text-sm text-destructive">
              Regeneration limit reached ({usage.regenerations_used}/{usage.regenerations_limit}{" "}
              this month).
            </p>
          )}
          <Textarea
            value={regenInstructions}
            onChange={(e) => setRegenInstructions(e.target.value)}
            rows={2}
            placeholder="Optional: e.g. Make it more casual with a strong CTA"
            className="text-sm"
          />
          <Button
            size="sm"
            variant="secondary"
            onClick={handleRegenerate}
            disabled={
              regenerating ||
              item.status === "generating" ||
              (usage != null && !isRegenerationAllowed(usage))
            }
          >
            {regenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Regenerate
          </Button>
        </div>

        {item.assets.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm font-medium">Generated assets</p>
            {item.assets.map((asset) => (
              <div key={asset.id} className="rounded-lg bg-muted p-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {ASSET_LABELS[asset.asset_type] || asset.asset_type}
                </p>
                <p className="whitespace-pre-wrap text-sm">{asset.content}</p>
              </div>
            ))}
          </div>
        )}

        {error && <p className="text-sm text-destructive">{error}</p>}
      </CardContent>
    </Card>
  );
}
