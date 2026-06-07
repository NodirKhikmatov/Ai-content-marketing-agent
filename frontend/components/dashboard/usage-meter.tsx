"use client";

import Link from "next/link";

import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { UsageStats } from "@/services/user";

interface UsageMeterProps {
  usage: UsageStats;
  className?: string;
  compact?: boolean;
}

function usagePercent(used: number, limit: number): number {
  if (limit <= 0) return 100;
  return Math.min(100, Math.round((used / limit) * 100));
}

function MeterRow({
  label,
  used,
  limit,
  compact,
}: {
  label: string;
  used: number;
  limit: number;
  compact?: boolean;
}) {
  const atLimit = used >= limit;
  const pct = usagePercent(used, limit);

  return (
    <div className={cn("space-y-2", compact && "space-y-1")}>
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("font-medium", atLimit && "text-destructive")}>
          {used} / {limit}
        </span>
      </div>
      <Progress value={pct} className={cn("h-2", atLimit && "[&>div]:bg-destructive")} />
    </div>
  );
}

export function UsageMeter({ usage, className, compact }: UsageMeterProps) {
  const analysesAtLimit = usage.analyses_used >= usage.analyses_limit;
  const regenAtLimit = usage.regenerations_used >= usage.regenerations_limit;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium capitalize">{usage.plan} plan</p>
        {(analysesAtLimit || regenAtLimit) && (
          <Link href="/dashboard/settings" className="text-xs text-primary hover:underline">
            View limits
          </Link>
        )}
      </div>
      <MeterRow
        label="Analyses this month"
        used={usage.analyses_used}
        limit={usage.analyses_limit}
        compact={compact}
      />
      <MeterRow
        label="Regenerations this month"
        used={usage.regenerations_used}
        limit={usage.regenerations_limit}
        compact={compact}
      />
    </div>
  );
}

export function isAnalysisAllowed(usage: UsageStats): boolean {
  return usage.analyses_used < usage.analyses_limit;
}

export function isRegenerationAllowed(usage: UsageStats): boolean {
  return usage.regenerations_used < usage.regenerations_limit;
}
