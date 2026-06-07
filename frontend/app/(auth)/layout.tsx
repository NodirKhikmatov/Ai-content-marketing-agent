import Link from "next/link";
import { Sparkles } from "lucide-react";

import { APP_NAME } from "@/lib/constants";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-accent/20">
      <header className="container mx-auto flex items-center justify-center px-6 py-8">
        <Link href="/" className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="font-bold">{APP_NAME}</span>
        </Link>
      </header>
      <main className="container mx-auto flex justify-center px-4 pb-16">{children}</main>
    </div>
  );
}
