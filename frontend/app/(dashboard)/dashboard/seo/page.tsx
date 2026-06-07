"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import {
  NoProjectSelected,
  ProjectPageHeader,
} from "@/components/dashboard/project-page-header";
import { useProject } from "@/contexts/project-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { projectsService, type SEOKeyword } from "@/services/projects";

export default function SEOPage() {
  const { activeProject } = useProject();
  const [keywords, setKeywords] = useState<SEOKeyword[]>([]);
  const [summary, setSummary] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeProject) return;
    async function load() {
      setLoading(true);
      try {
        const data = await projectsService.getSEOKeywords(activeProject!.id);
        setKeywords(data.items);
        setSummary(data.summary);
      } catch {
        setKeywords([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeProject]);

  const priorityColor = (p: string) => {
    if (p === "high") return "text-red-600 bg-red-50";
    if (p === "medium") return "text-yellow-600 bg-yellow-50";
    return "text-gray-600 bg-gray-50";
  };

  return (
    <div className="space-y-8">
      <ProjectPageHeader title="SEO Dashboard" description="Keyword strategy for" />

      {!activeProject ? (
        <NoProjectSelected />
      ) : loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {keywords.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-3">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-2xl font-bold">{summary.total_keywords}</p>
                  <p className="text-sm text-muted-foreground">Total Keywords</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-2xl font-bold">{summary.high_priority}</p>
                  <p className="text-sm text-muted-foreground">High Priority</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-2xl font-bold">{keywords.length}</p>
                  <p className="text-sm text-muted-foreground">Tracked</p>
                </CardContent>
              </Card>
            </div>
          )}

          {keywords.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                Run analysis to generate your SEO keyword strategy.
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Keywords</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-3 pr-4">Keyword</th>
                        <th className="pb-3 pr-4">Volume</th>
                        <th className="pb-3 pr-4">Difficulty</th>
                        <th className="pb-3 pr-4">Intent</th>
                        <th className="pb-3 pr-4">Cluster</th>
                        <th className="pb-3">Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      {keywords.map((kw) => (
                        <tr key={kw.id} className="border-b last:border-0">
                          <td className="py-3 pr-4 font-medium">{kw.keyword}</td>
                          <td className="py-3 pr-4">{kw.search_volume?.toLocaleString() ?? "—"}</td>
                          <td className="py-3 pr-4">{kw.difficulty ?? "—"}</td>
                          <td className="py-3 pr-4 capitalize">{kw.intent ?? "—"}</td>
                          <td className="py-3 pr-4">{kw.cluster ?? "—"}</td>
                          <td className="py-3">
                            <span
                              className={`rounded-full px-2 py-0.5 text-xs font-medium ${priorityColor(kw.priority)}`}
                            >
                              {kw.priority}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
