"use client";

import { ExternalLink, Globe, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import type { Website } from "@/services/websites";

const STATUS_LABELS: Record<Website["status"], string> = {
  pending: "Ready for analysis",
  crawling: "Crawling website",
  analyzed: "Analysis complete",
  failed: "Analysis failed",
};

const STATUS_VARIANT: Record<Website["status"], "draft" | "analyzing" | "active" | "archived"> = {
  pending: "draft",
  crawling: "analyzing",
  analyzed: "active",
  failed: "archived",
};

interface WebsiteCardProps {
  website: Website;
  onChangeUrl?: () => void;
}

export function WebsiteCard({ website, onChangeUrl }: WebsiteCardProps) {
  const showAnalysisResults = website.status === "analyzed";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Globe className="h-5 w-5 text-primary" />
              Website Submitted
            </CardTitle>
            <CardDescription>
              Submitted {formatDate(website.created_at)}
            </CardDescription>
          </div>
          <Badge variant={STATUS_VARIANT[website.status]} className="shrink-0">
            {STATUS_LABELS[website.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between rounded-lg border bg-muted/50 px-4 py-3">
          <a
            href={website.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm font-medium hover:text-primary"
          >
            {website.url}
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          {onChangeUrl && website.status === "pending" && (
            <Button variant="ghost" size="sm" onClick={onChangeUrl}>
              <RefreshCw className="h-3.5 w-3.5" />
              Change
            </Button>
          )}
        </div>

        {showAnalysisResults && (
          <div className="grid gap-3 sm:grid-cols-2 text-sm">
            {website.business_type && (
              <div>
                <p className="text-muted-foreground">Business type</p>
                <p className="font-medium">{website.business_type}</p>
              </div>
            )}
            {website.target_audience && (
              <div>
                <p className="text-muted-foreground">Target audience</p>
                <p className="font-medium">{website.target_audience}</p>
              </div>
            )}
            {website.unique_value_proposition && (
              <div className="sm:col-span-2">
                <p className="text-muted-foreground">Unique value proposition</p>
                <p className="font-medium">{website.unique_value_proposition}</p>
              </div>
            )}
          </div>
        )}

        {website.status === "pending" && (
          <p className="text-sm text-muted-foreground">
            URL saved. Start AI analysis to generate your marketing strategy.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
