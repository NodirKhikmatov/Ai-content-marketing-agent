"use client";

import { ChevronDown, FolderKanban } from "lucide-react";

import { useProject } from "@/contexts/project-context";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function ProjectSwitcher() {
  const { projects, activeProject, loading, selectProject } = useProject();

  if (loading || projects.length === 0) {
    return null;
  }

  return (
    <div className="border-b px-4 py-3">
      <label htmlFor="project-switcher" className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <FolderKanban className="h-3.5 w-3.5" />
        Active project
      </label>
      <div className="relative">
        <select
          id="project-switcher"
          value={activeProject?.id ?? ""}
          onChange={(e) => selectProject(e.target.value)}
          className={cn(
            "w-full appearance-none rounded-md border border-input bg-background px-3 py-2 pr-8 text-sm",
            "focus:outline-none focus:ring-2 focus:ring-ring"
          )}
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
      </div>
      {activeProject && (
        <Badge
          variant={activeProject.status as "draft" | "analyzing" | "active" | "archived"}
          className="mt-2 capitalize"
        >
          {activeProject.status}
        </Badge>
      )}
    </div>
  );
}
