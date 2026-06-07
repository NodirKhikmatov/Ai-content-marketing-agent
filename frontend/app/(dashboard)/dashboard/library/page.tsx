"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { ContentItemDetailPanel } from "@/components/dashboard/content-item-detail";
import {
  NoProjectSelected,
  ProjectPageHeader,
} from "@/components/dashboard/project-page-header";
import { useProject } from "@/contexts/project-context";
import { getChannelIcon, getStatusLabel, getStatusStyle } from "@/lib/content-utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CHANNELS } from "@/lib/constants";
import { projectsService, type ContentItem } from "@/services/projects";

export default function LibraryPage() {
  const { activeProject } = useProject();
  const [items, setItems] = useState<ContentItem[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selected, setSelected] = useState<ContentItem | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeProject) return;
    async function load() {
      setLoading(true);
      try {
        const params: { channel?: string; status?: string; limit: number } = { limit: 50 };
        if (filter !== "all") params.channel = filter;
        if (statusFilter !== "all") params.status = statusFilter;
        const data = await projectsService.getContentItems(activeProject!.id, params);
        setItems(data.items);
        setSelected((prev) =>
          prev && data.items.some((i) => i.id === prev.id) ? prev : data.items[0] ?? null
        );
      } catch {
        setItems([]);
        setSelected(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeProject, filter, statusFilter]);

  const handleItemUpdated = (detail: ContentItem) => {
    setItems((prev) => prev.map((i) => (i.id === detail.id ? { ...i, ...detail } : i)));
    setSelected((prev) => (prev?.id === detail.id ? { ...prev, ...detail } : prev));
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4">
        <ProjectPageHeader title="Content Library" description="Generated content for" />
        {activeProject && (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap gap-2">
              <Button
                variant={filter === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter("all")}
              >
                All channels
              </Button>
              {CHANNELS.map((ch) => (
                <Button
                  key={ch.value}
                  variant={filter === ch.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilter(ch.value)}
                >
                  {ch.icon} {ch.label}
                </Button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {(["all", "ready", "approved", "draft"] as const).map((s) => (
                <Button
                  key={s}
                  variant={statusFilter === s ? "default" : "outline"}
                  size="sm"
                  onClick={() => setStatusFilter(s)}
                >
                  {s === "all" ? "All statuses" : s.charAt(0).toUpperCase() + s.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>

      {!activeProject ? (
        <NoProjectSelected />
      ) : loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-3">
            {items.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  No content items match your filters.
                </CardContent>
              </Card>
            ) : (
              items.map((item) => (
                <Card
                  key={item.id}
                  className={`cursor-pointer transition-shadow hover:shadow-md ${
                    selected?.id === item.id ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => setSelected(item)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <CardTitle className="text-base">{item.title}</CardTitle>
                        <CardDescription className="capitalize">
                          {getChannelIcon(item.channel)} {item.channel} · {item.format}
                        </CardDescription>
                      </div>
                      <span
                        className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${getStatusStyle(item.status)}`}
                      >
                        {getStatusLabel(item.status)}
                      </span>
                    </div>
                  </CardHeader>
                  {item.body && (
                    <CardContent className="pt-0">
                      <p className="line-clamp-2 text-sm text-muted-foreground">{item.body}</p>
                    </CardContent>
                  )}
                </Card>
              ))
            )}
          </div>

          {selected && activeProject && (
            <ContentItemDetailPanel
              projectId={activeProject.id}
              itemId={selected.id}
              onUpdated={handleItemUpdated}
            />
          )}
        </div>
      )}
    </div>
  );
}
