"use client";

import { useEffect, useState } from "react";
import { ExternalLink, Loader2 } from "lucide-react";

import {
  NoProjectSelected,
  ProjectPageHeader,
} from "@/components/dashboard/project-page-header";
import { useProject } from "@/contexts/project-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { projectsService, type Competitor } from "@/services/projects";

export default function CompetitorsPage() {
  const { activeProject } = useProject();
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeProject) return;
    async function load() {
      setLoading(true);
      try {
        const data = await projectsService.getCompetitors(activeProject!.id);
        setCompetitors(data.items);
      } catch {
        setCompetitors([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeProject]);

  return (
    <div className="space-y-8">
      <ProjectPageHeader title="Competitors" description="AI-identified competitors for" />

      {!activeProject ? (
        <NoProjectSelected />
      ) : loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : competitors.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Run a website analysis to discover competitors.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {competitors.map((comp) => (
            <Card key={comp.id}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {comp.name}
                  <a href={comp.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 text-muted-foreground hover:text-primary" />
                  </a>
                </CardTitle>
                <CardDescription>{comp.positioning_summary}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div>
                  <p className="font-medium text-green-700">Strengths</p>
                  <ul className="mt-1 list-inside list-disc text-muted-foreground">
                    {comp.strengths.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-red-700">Weaknesses</p>
                  <ul className="mt-1 list-inside list-disc text-muted-foreground">
                    {comp.weaknesses.map((w) => (
                      <li key={w}>{w}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-primary">Content Gaps</p>
                  <ul className="mt-1 list-inside list-disc text-muted-foreground">
                    {comp.content_gaps.map((g) => (
                      <li key={g}>{g}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
