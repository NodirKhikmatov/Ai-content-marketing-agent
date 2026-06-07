import { CHANNELS, CONTENT_STATUSES } from "@/lib/constants";
import type { ContentItem } from "@/services/projects";

export function getChannelLabel(channel: string): string {
  return CHANNELS.find((c) => c.value === channel)?.label || channel;
}

export function getChannelIcon(channel: string): string {
  return CHANNELS.find((c) => c.value === channel)?.icon || "📄";
}

export function getStatusStyle(status: string): string {
  return CONTENT_STATUSES.find((s) => s.value === status)?.color || "bg-gray-100 text-gray-700";
}

export function getStatusLabel(status: string): string {
  return CONTENT_STATUSES.find((s) => s.value === status)?.label || status;
}

export interface WeekGroup {
  label: string;
  startDate: string;
  items: ContentItem[];
}

export function groupItemsByWeek(items: ContentItem[]): WeekGroup[] {
  const sorted = [...items].sort((a, b) => {
    const da = a.scheduled_date ? new Date(a.scheduled_date).getTime() : 0;
    const db = b.scheduled_date ? new Date(b.scheduled_date).getTime() : 0;
    return da - db;
  });

  const groups = new Map<string, WeekGroup>();

  for (const item of sorted) {
    const date = item.scheduled_date ? new Date(item.scheduled_date) : new Date();
    const weekStart = startOfWeek(date);
    const key = weekStart.toISOString().slice(0, 10);
    const label = `Week of ${weekStart.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;

    if (!groups.has(key)) {
      groups.set(key, { label, startDate: key, items: [] });
    }
    groups.get(key)!.items.push(item);
  }

  return Array.from(groups.values());
}

function startOfWeek(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function countByChannel(items: ContentItem[]): Record<string, number> {
  return items.reduce<Record<string, number>>((acc, item) => {
    acc[item.channel] = (acc[item.channel] || 0) + 1;
    return acc;
  }, {});
}
