"use client";

import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Project } from "@/services/projects";
import { cn } from "@/lib/utils";

const STATUS_VARIANT: Record<string, "draft" | "analyzing" | "active" | "archived"> = {
  draft: "draft",
  analyzing: "analyzing",
  active: "active",
  archived: "archived",
};

interface ProjectCardProps {
  project: Project;
  selected: boolean;
  onSelect: () => void;
}

export function ProjectCard({ project, selected, onSelect }: ProjectCardProps) {
  const statusVariant = STATUS_VARIANT[project.status] ?? "draft";

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:shadow-md",
        selected && "ring-2 ring-primary shadow-md"
      )}
      onClick={onSelect}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg leading-tight">{project.name}</CardTitle>
          <Badge variant={statusVariant} className="shrink-0 capitalize">
            {project.status}
          </Badge>
        </div>
        {project.description && (
          <CardDescription className="line-clamp-2">{project.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="text-xs text-muted-foreground">
        Created {formatDate(project.created_at)}
        {project.stats && project.stats.content_items > 0 && (
          <span className="ml-2">
            · {project.stats.content_items} items · {project.stats.keywords} keywords
          </span>
        )}
      </CardContent>
    </Card>
  );
}
