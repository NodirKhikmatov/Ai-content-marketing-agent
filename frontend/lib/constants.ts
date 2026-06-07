export const APP_NAME = "AI Content Marketing Agent";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const CHANNELS = [
  { value: "linkedin", label: "LinkedIn", icon: "💼" },
  { value: "blog", label: "Blog", icon: "📝" },
  { value: "tiktok", label: "TikTok", icon: "🎵" },
  { value: "youtube", label: "YouTube", icon: "▶️" },
  { value: "instagram", label: "Instagram", icon: "📸" },
  { value: "twitter", label: "Twitter/X", icon: "🐦" },
] as const;

export const CONTENT_STATUSES = [
  { value: "draft", label: "Draft", color: "bg-gray-100 text-gray-700" },
  { value: "ready", label: "Ready", color: "bg-blue-100 text-blue-700" },
  { value: "approved", label: "Approved", color: "bg-green-100 text-green-700" },
  { value: "rejected", label: "Rejected", color: "bg-red-100 text-red-700" },
  { value: "published", label: "Published", color: "bg-purple-100 text-purple-700" },
] as const;

export const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: "LayoutDashboard" },
  { href: "/dashboard/competitors", label: "Competitors", icon: "Users" },
  { href: "/dashboard/calendar", label: "Calendar", icon: "Calendar" },
  { href: "/dashboard/library", label: "Content Library", icon: "Library" },
  { href: "/dashboard/seo", label: "SEO", icon: "Search" },
  { href: "/dashboard/settings", label: "Settings", icon: "Settings" },
] as const;
