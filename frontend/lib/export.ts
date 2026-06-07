import type { ContentItem } from "@/services/projects";

/** Escape a single CSV cell per RFC 4180 (quote if it contains comma, quote, or newline). */
function csvCell(value: unknown): string {
  const str = value == null ? "" : String(value);
  if (/[",\n\r]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/** Convert content items into a CSV string suitable for Excel / Google Sheets. */
export function contentItemsToCsv(items: ContentItem[]): string {
  const headers = [
    "Date",
    "Title",
    "Channel",
    "Format",
    "Status",
    "Keywords",
    "Description",
  ];

  const rows = items.map((item) =>
    [
      item.scheduled_date ?? "",
      item.title ?? "",
      item.channel ?? "",
      item.format ?? "",
      item.status ?? "",
      (item.keyword_targets ?? []).join("; "),
      item.description ?? "",
    ]
      .map(csvCell)
      .join(",")
  );

  return [headers.join(","), ...rows].join("\r\n");
}

/** Trigger a browser download of the given text content. */
export function downloadCsv(filename: string, csv: string): void {
  // Prepend a UTF-8 BOM (U+FEFF) so Excel detects the encoding correctly.
  const bom = String.fromCharCode(0xfeff);
  const blob = new Blob([bom + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** Build a filesystem-safe filename like "my-project-content-calendar.csv". */
export function exportFilename(projectName: string): string {
  const slug = projectName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${slug || "project"}-content-calendar.csv`;
}
