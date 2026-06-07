"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import Link from "next/link";

import { AnalysisProgress } from "@/components/dashboard/analysis-progress";
import {
  isAnalysisAllowed,
  UsageMeter,
} from "@/components/dashboard/usage-meter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { analysisService, DEFAULT_ANALYSIS_OPTIONS } from "@/services/analysis";
import { ApiError } from "@/services/api-client";
import { userService, type UsageStats } from "@/services/user";

interface WebsiteAnalyzerProps {
  projectId: string;
  websiteId: string;
  onStarted?: (jobId: string) => void;
  onComplete?: () => void;
}

export function WebsiteAnalyzer({
  projectId,
  websiteId,
  onStarted,
  onComplete,
}: WebsiteAnalyzerProps) {
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);

  useEffect(() => {
    userService
      .getUsage()
      .then(setUsage)
      .catch(() => setUsage(null));
  }, []);

  const handleStart = async () => {
    setError(null);
    setLoading(true);
    try {
      const job = await analysisService.start(projectId, websiteId, DEFAULT_ANALYSIS_OPTIONS);
      setJobId(job.id);
      onStarted?.(job.id);
      if (usage) {
        setUsage({
          ...usage,
          analyses_used: usage.analyses_used + 1,
        });
      }
    } catch (err) {
      if (err instanceof ApiError && err.code === "QUOTA_EXCEEDED") {
        setError(err.message);
        userService.getUsage().then(setUsage).catch(() => undefined);
      } else {
        setError(err instanceof ApiError ? err.message : "Failed to start analysis");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setJobId(null);
    setError(null);
  };

  if (jobId) {
    return (
      <AnalysisProgress
        jobId={jobId}
        onComplete={onComplete}
        onFailed={() => userService.getUsage().then(setUsage).catch(() => undefined)}
        onRetry={handleRetry}
      />
    );
  }

  const limitReached = usage ? !isAnalysisAllowed(usage) : false;

  return (
    <Card className="border-primary/30 bg-primary/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Ready for AI Analysis
        </CardTitle>
        <CardDescription>
          AI analyzes your site, maps competitors, builds personas, and creates a 7-day content
          preview with 3 ready-to-use posts (captions or video scripts).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {usage && (
          <div className="rounded-lg border bg-background p-4">
            <UsageMeter usage={usage} compact />
          </div>
        )}

        {limitReached && (
          <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
            You&apos;ve used all analyses for this month on the {usage?.plan} plan.{" "}
            <Link href="/dashboard/settings" className="font-medium underline">
              View usage in Settings
            </Link>
          </p>
        )}

        {error && !limitReached && (
          <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <Button onClick={handleStart} disabled={loading || limitReached} className="w-full">
          <Sparkles className="h-4 w-4" />
          {loading ? "Starting..." : limitReached ? "Analysis limit reached" : "Start AI Analysis"}
        </Button>
        <p className="text-center text-xs text-muted-foreground">
          Usually 2–3 minutes · 3 sample posts with copy-ready text (not auto-posted)
        </p>
      </CardContent>
    </Card>
  );
}
