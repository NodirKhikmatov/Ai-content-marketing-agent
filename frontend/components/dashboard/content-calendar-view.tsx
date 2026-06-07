"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getChannelIcon,
  getChannelLabel,
  getStatusLabel,
  getStatusStyle,
  groupItemsByWeek,
} from "@/lib/content-utils";
import { formatDate } from "@/lib/utils";
import type { ContentItem } from "@/services/projects";

interface ContentCalendarViewProps {
  items: ContentItem[];
  selectedId?: string;
  onSelect?: (item: ContentItem) => void;
}

export function ContentCalendarView({ items, selectedId, onSelect }: ContentCalendarViewProps) {
  const weeks = groupItemsByWeek(items);
  const [expandedWeeks, setExpandedWeeks] = useState<Set<string>>(
    () => new Set(weeks.map((w) => w.startDate))
  );

  const toggleWeek = (startDate: string) => {
    setExpandedWeeks((prev) => {
      const next = new Set(prev);
      if (next.has(startDate)) {
        next.delete(startDate);
      } else {
        next.add(startDate);
      }
      return next;
    });
  };

  return (
    <div className="space-y-4">
      {weeks.map((week) => {
        const isExpanded = expandedWeeks.has(week.startDate);
        return (
          <div key={week.startDate} className="space-y-2">
            <button
              type="button"
              onClick={() => toggleWeek(week.startDate)}
              className="flex w-full items-center gap-2 rounded-lg px-1 py-1 text-left text-sm font-semibold hover:text-primary"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 shrink-0" />
              ) : (
                <ChevronRight className="h-4 w-4 shrink-0" />
              )}
              {week.label}
              <span className="font-normal text-muted-foreground">({week.items.length} items)</span>
            </button>

            {isExpanded && (
              <div className="space-y-2 pl-2">
                {week.items.map((item) => (
                  <Card
                    key={item.id}
                    className={`cursor-pointer transition-shadow hover:shadow-md ${
                      selectedId === item.id ? "ring-2 ring-primary" : ""
                    }`}
                    onClick={() => onSelect?.(item)}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <CardTitle className="text-base leading-snug">{item.title}</CardTitle>
                          <CardDescription className="mt-1">
                            {item.scheduled_date ? formatDate(item.scheduled_date) : "Unscheduled"}
                            {" · "}
                            {getChannelIcon(item.channel)} {getChannelLabel(item.channel)}
                            {" · "}
                            <span className="capitalize">{item.format}</span>
                          </CardDescription>
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${getStatusStyle(item.status)}`}
                        >
                          {getStatusLabel(item.status)}
                        </span>
                      </div>
                    </CardHeader>
                    {item.description && (
                      <CardContent className="pt-0">
                        <p className="line-clamp-2 text-sm text-muted-foreground">
                          {item.description}
                        </p>
                        {item.keyword_targets.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {item.keyword_targets.slice(0, 3).map((kw) => (
                              <Badge key={kw} variant="draft" className="text-xs">
                                {kw}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
