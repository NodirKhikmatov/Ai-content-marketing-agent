"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2, Plus, Trash2 } from "lucide-react";

import { CreateProjectDialog } from "@/components/dashboard/create-project-dialog";
import { EmptyProjects } from "@/components/dashboard/empty-projects";
import { ProjectCard } from "@/components/dashboard/project-card";
import { ProjectStats } from "@/components/dashboard/project-stats";
import { WebsiteSection } from "@/components/dashboard/website-section";
import { useProject } from "@/contexts/project-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function DashboardPage() {
  const {
    projects,
    activeProject,
    loading,
    error,
    selectProject,
    deleteProject,
  } = useProject();

  const [createOpen, setCreateOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const hasCompletedAnalysis =
    activeProject?.status === "active" ||
    (activeProject?.stats && activeProject.stats.content_items > 0);

  const showWebsiteSection = activeProject && !hasCompletedAnalysis;

  const handleDelete = async () => {
    if (!activeProject) return;
    if (!confirm(`Delete "${activeProject.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteProject(activeProject.id);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Overview</h1>
          <p className="text-muted-foreground">Manage your marketing projects</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> New Project
        </Button>
      </div>

      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="py-3 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center gap-2 py-12 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading projects...
        </div>
      ) : projects.length === 0 ? (
        <EmptyProjects onCreateClick={() => setCreateOpen(true)} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                selected={activeProject?.id === project.id}
                onSelect={() => selectProject(project.id)}
              />
            ))}
          </div>

          {activeProject && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">{activeProject.name}</h2>
                  {activeProject.description && (
                    <p className="text-sm text-muted-foreground">{activeProject.description}</p>
                  )}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-destructive hover:text-destructive"
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  {deleting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                  Delete
                </Button>
              </div>

              {showWebsiteSection && <WebsiteSection projectId={activeProject.id} />}

              {activeProject.stats && activeProject.stats.content_items > 0 && hasCompletedAnalysis && (
                <>
                  <ProjectStats stats={activeProject.stats} />
                  <div className="flex flex-wrap gap-3">
                    <Button variant="outline" asChild>
                      <Link href="/dashboard/calendar">View Calendar</Link>
                    </Button>
                    <Button variant="outline" asChild>
                      <Link href="/dashboard/library">Content Library</Link>
                    </Button>
                    <Button variant="outline" asChild>
                      <Link href="/dashboard/competitors">Competitors</Link>
                    </Button>
                    <Button variant="outline" asChild>
                      <Link href="/dashboard/seo">SEO Dashboard</Link>
                    </Button>
                  </div>
                </>
              )}
            </div>
          )}
        </>
      )}

      <CreateProjectDialog open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  );
}
