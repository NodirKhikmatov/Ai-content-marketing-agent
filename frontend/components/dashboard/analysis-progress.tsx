"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  analysisService,
  PIPELINE_STEPS,
  STEP_LABELS,
  type AnalysisJob,
} from "@/services/analysis";
import { cn } from "@/lib/utils";

interface AnalysisProgressProps {
  jobId: string;
  onComplete?: () => void;
  onFailed?: () => void;
  onRetry?: () => void;
}

export function AnalysisProgress({ jobId, onComplete, onFailed, onRetry }: AnalysisProgressProps) {
  const [job, setJob] = useState<AnalysisJob | null>(null);

  const poll = useCallback(async () => {
    try {
      const status = await analysisService.getJob(jobId);
      setJob(status);
      return status;
    } catch {
      return null;
    }
  }, [jobId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    let cancelled = false;

    const run = async () => {
      const status = await poll();
      if (cancelled || !status) return;

      if (status.status === "completed") {
        onComplete?.();
        return;
      }
      if (status.status === "failed") {
        onFailed?.();
        return;
      }

      interval = setInterval(async () => {
        const latest = await poll();
        if (!latest) return;
        if (latest.status === "completed") {
          clearInterval(interval);
          onComplete?.();
        } else if (latest.status === "failed") {
          clearInterval(interval);
          onFailed?.();
        }
      }, 2500);
    };

    run();
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [jobId, poll, onComplete, onFailed]);

  if (!job) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center gap-2 py-12 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          Starting analysis...
        </CardContent>
      </Card>
    );
  }

  if (job.status === "failed") {
    return (
      <Card className="border-destructive/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <XCircle className="h-5 w-5" />
            Analysis Failed
          </CardTitle>
          <CardDescription>{job.error_message || "An unexpected error occurred."}</CardDescription>
        </CardHeader>
        {onRetry && (
          <CardContent className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Failed runs no longer count against your monthly analysis limit.
            </p>
            <Button variant="outline" onClick={onRetry}>
              Try Again
            </Button>
          </CardContent>
        )}
      </Card>
    );
  }

  if (job.status === "completed") {
    return (
      <Card className="border-green-200 bg-green-50/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-700">
            <CheckCircle2 className="h-5 w-5" />
            Analysis Complete
          </CardTitle>
          <CardDescription>
            Your marketing strategy and content plan are ready to review.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const completedSet = new Set(job.steps_completed || []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          AI Analysis in Progress
        </CardTitle>
        <CardDescription>
          {job.current_step
            ? STEP_LABELS[job.current_step] || job.current_step
            : "Initializing pipeline..."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Progress value={job.progress} />
          <p className="text-sm text-muted-foreground">{job.progress}% complete</p>
        </div>

        <ul className="space-y-2">
          {PIPELINE_STEPS.map((step) => {
            const done = completedSet.has(step);
            const active = job.current_step === step;
            return (
              <li
                key={step}
                className={cn(
                  "flex items-center gap-2 text-sm",
                  done && "text-green-700",
                  active && !done && "font-medium text-primary",
                  !done && !active && "text-muted-foreground"
                )}
              >
                {done ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
                ) : (
                  <Circle className="h-4 w-4 shrink-0" />
                )}
                {STEP_LABELS[step]}
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
