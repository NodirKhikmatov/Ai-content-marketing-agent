"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Loader2 } from "lucide-react";

import { AnalysisProgress } from "@/components/dashboard/analysis-progress";
import { WebsiteAnalyzer } from "@/components/dashboard/website-analyzer";
import { WebsiteCard } from "@/components/dashboard/website-card";
import { WebsiteUrlForm } from "@/components/dashboard/website-url-form";
import { useProject } from "@/contexts/project-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { analysisService } from "@/services/analysis";
import { ApiError } from "@/services/api-client";
import { websitesService, type Website } from "@/services/websites";

interface WebsiteSectionProps {
  projectId: string;
}

export function WebsiteSection({ projectId }: WebsiteSectionProps) {
  const { refreshActiveProject } = useProject();
  const [website, setWebsite] = useState<Website | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const site = await websitesService.getPrimary(projectId);
      setWebsite(site);
      setShowForm(false);

      try {
        const job = await analysisService.getActiveJob(projectId);
        setActiveJobId(job.id);
      } catch (err) {
        if (!(err instanceof ApiError && err.status === 404)) {
          throw err;
        }
        setActiveJobId(null);
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setWebsite(null);
        setShowForm(true);
        setActiveJobId(null);
      } else {
        setError(err instanceof Error ? err.message : "Failed to load");
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAnalysisComplete = async () => {
    await load();
    await refreshActiveProject();
  };

  const handleSubmitted = (submitted: Website) => {
    setWebsite(submitted);
    setShowForm(false);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center gap-2 py-12 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading...
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50">
        <CardContent className="py-4 text-sm text-destructive">{error}</CardContent>
      </Card>
    );
  }

  if (showForm || !website) {
    return <WebsiteUrlForm projectId={projectId} onSubmitted={handleSubmitted} />;
  }

  const isAnalyzed = website.status === "analyzed";
  const isRunning = !!activeJobId || website.status === "crawling";

  return (
    <div className="space-y-4">
      <WebsiteCard
        website={website}
        onChangeUrl={website.status === "pending" && !isRunning ? () => setShowForm(true) : undefined}
      />

      {isRunning && activeJobId && (
        <AnalysisProgress
          jobId={activeJobId}
          onComplete={handleAnalysisComplete}
          onFailed={handleAnalysisComplete}
          onRetry={() => {
            setActiveJobId(null);
            load();
          }}
        />
      )}

      {!isRunning && website.status === "pending" && (
        <WebsiteAnalyzer
          projectId={projectId}
          websiteId={website.id}
          onStarted={setActiveJobId}
          onComplete={handleAnalysisComplete}
        />
      )}

      {!isRunning && website.status === "failed" && (
        <WebsiteAnalyzer
          projectId={projectId}
          websiteId={website.id}
          onStarted={setActiveJobId}
          onComplete={handleAnalysisComplete}
        />
      )}

      {isAnalyzed && (
        <Card className="border-green-200 bg-green-50/50">
          <CardContent className="flex flex-col gap-4 py-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-medium">Strategy and content plan ready</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/calendar">Calendar</Link>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/seo">SEO</Link>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/library">Library</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
