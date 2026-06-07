"use client";

import { Card, CardContent } from "@/components/ui/card";

interface ProjectStatsProps {
  stats: {
    content_items: number;
    approved_items: number;
    keywords: number;
    competitors: number;
  };
}

export function ProjectStats({ stats }: ProjectStatsProps) {
  const items = [
    { label: "Content Items", value: stats.content_items },
    { label: "Approved", value: stats.approved_items },
    { label: "Keywords", value: stats.keywords },
    { label: "Competitors", value: stats.competitors },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <Card key={item.label}>
          <CardContent className="pt-6">
            <p className="text-3xl font-bold">{item.value}</p>
            <p className="text-sm text-muted-foreground">{item.label}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
