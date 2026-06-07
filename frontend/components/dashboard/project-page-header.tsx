"use client";

import { AlertCircle, Loader2 } from "lucide-react";

import { useProject } from "@/contexts/project-context";
import { Card, CardContent } from "@/components/ui/card";

export function ProjectPageHeader({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  const { activeProject, loading, error } = useProject();

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading project...
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <h1 className="text-3xl font-bold">{title}</h1>
      <p className="text-muted-foreground">
        {description ?? "Project"} —{" "}
        <span className="font-medium text-foreground">{activeProject?.name ?? "No project selected"}</span>
      </p>
      {error && (
        <Card className="mt-4 border-destructive/50 bg-destructive/5">
          <CardContent className="flex items-center gap-2 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export function NoProjectSelected() {
  return (
    <Card className="border-dashed">
      <CardContent className="py-12 text-center text-muted-foreground">
        Select or create a project from the Overview page to get started.
      </CardContent>
    </Card>
  );
}
