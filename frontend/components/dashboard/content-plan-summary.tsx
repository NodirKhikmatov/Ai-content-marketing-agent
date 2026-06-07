"use client";

import { Calendar, Layers } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getChannelIcon, getChannelLabel } from "@/lib/content-utils";
import { formatDate } from "@/lib/utils";
import type { ContentPlan } from "@/services/projects";

interface ContentPlanSummaryProps {
  plan: ContentPlan;
  itemCount?: number;
}

export function ContentPlanSummary({ plan, itemCount }: ContentPlanSummaryProps) {
  const channelEntries = Object.entries(plan.channel_mix || {}).sort((a, b) => b[1] - a[1]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calendar className="h-5 w-5 text-primary" />
              {plan.name}
            </CardTitle>
            <CardDescription>
              {formatDate(plan.start_date)} – {formatDate(plan.end_date)}
              {itemCount != null && ` · ${itemCount} content items`}
            </CardDescription>
          </div>
          <Badge variant="active">{plan.status}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {plan.pillars.length > 0 && (
          <div>
            <p className="mb-2 flex items-center gap-1.5 text-sm font-medium">
              <Layers className="h-4 w-4 text-muted-foreground" />
              Content pillars
            </p>
            <div className="flex flex-wrap gap-2">
              {plan.pillars.map((pillar) => (
                <Badge key={pillar} variant="draft">
                  {pillar}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {channelEntries.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-medium">Channel mix</p>
            <div className="flex flex-wrap gap-2">
              {channelEntries.map(([channel, count]) => (
                <span
                  key={channel}
                  className="inline-flex items-center gap-1.5 rounded-full bg-muted px-3 py-1 text-xs font-medium"
                >
                  <span>{getChannelIcon(channel)}</span>
                  {getChannelLabel(channel)}
                  <span className="text-muted-foreground">({count})</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
