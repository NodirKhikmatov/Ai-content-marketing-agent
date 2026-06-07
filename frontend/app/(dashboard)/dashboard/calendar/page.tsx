"use client";

import { useEffect, useState } from "react";
import { Download, Loader2 } from "lucide-react";

import { ContentCalendarView } from "@/components/dashboard/content-calendar-view";
import { ContentItemDetailPanel } from "@/components/dashboard/content-item-detail";
import { ContentPlanSummary } from "@/components/dashboard/content-plan-summary";
import {
  NoProjectSelected,
  ProjectPageHeader,
} from "@/components/dashboard/project-page-header";
import { useProject } from "@/contexts/project-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { contentItemsToCsv, downloadCsv, exportFilename } from "@/lib/export";
import { projectsService, type ContentItem, type ContentPlan } from "@/services/projects";

export default function CalendarPage() {
  const { activeProject } = useProject();
  const [items, setItems] = useState<ContentItem[]>([]);
  const [plan, setPlan] = useState<ContentPlan | null>(null);
  const [selected, setSelected] = useState<ContentItem | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeProject) return;
    async function load() {
      setLoading(true);
      try {
        const [itemsData, plansData] = await Promise.all([
          projectsService.getContentItems(activeProject!.id, { limit: 50 }),
          projectsService.getContentPlans(activeProject!.id),
        ]);
        setItems(itemsData.items);
        setPlan(plansData.items[0] ?? null);
        if (itemsData.items.length > 0) {
          setSelected((prev) =>
            prev && itemsData.items.some((i) => i.id === prev.id)
              ? prev
              : itemsData.items[0]
          );
        } else {
          setSelected(null);
        }
      } catch {
        setItems([]);
        setPlan(null);
        setSelected(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeProject]);

  const handleItemUpdated = (detail: ContentItem) => {
    setItems((prev) => prev.map((i) => (i.id === detail.id ? { ...i, ...detail } : i)));
    setSelected((prev) => (prev?.id === detail.id ? { ...prev, ...detail } : prev));
  };

  const handleExport = () => {
    if (!activeProject || items.length === 0) return;
    const csv = contentItemsToCsv(items);
    downloadCsv(exportFilename(activeProject.name), csv);
  };

  return (
    <div className="space-y-8">
      <ProjectPageHeader title="Content Calendar" description="30-day plan for" />

      {!activeProject ? (
        <NoProjectSelected />
      ) : loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Complete a website analysis to generate your content calendar.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4" /> Export CSV
            </Button>
          </div>

          {plan && <ContentPlanSummary plan={plan} itemCount={items.length} />}

          <div className="grid gap-6 lg:grid-cols-2">
            <ContentCalendarView
              items={items}
              selectedId={selected?.id}
              onSelect={setSelected}
            />
            {selected && activeProject && (
              <ContentItemDetailPanel
                projectId={activeProject.id}
                itemId={selected.id}
                onUpdated={handleItemUpdated}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
