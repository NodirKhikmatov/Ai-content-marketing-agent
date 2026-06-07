import Link from "next/link";
import { ArrowRight, Calendar, Search, Sparkles, Target, Zap } from "lucide-react";

import { Button } from "@/components/ui/button";
import { APP_NAME } from "@/lib/constants";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-accent/20">
      <header className="container mx-auto flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <Sparkles className="h-7 w-7 text-primary" />
          <span className="text-lg font-bold">{APP_NAME}</span>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" asChild>
            <Link href="/login">Log in</Link>
          </Button>
          <Button asChild>
            <Link href="/signup">Get Started</Link>
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            Your AI Marketing Team,{" "}
            <span className="text-primary">Powered by Your Website</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground">
            Enter your URL. Get a 30-day content calendar, SEO strategy, competitor analysis,
            and ready-to-publish content for every channel — in minutes.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Button size="lg" asChild>
              <Link href="/signup">
                Start Free <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">View Demo</Link>
            </Button>
          </div>
        </div>

        <div className="mx-auto mt-24 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Target, title: "Business Analysis", desc: "AI extracts your UVP, audience, and products" },
            { icon: Search, title: "Competitor Intel", desc: "Discover gaps and opportunities in your market" },
            { icon: Calendar, title: "30-Day Calendar", desc: "Multi-channel content plan ready to execute" },
            { icon: Zap, title: "Ready Content", desc: "Captions, scripts, outlines, and image prompts" },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="rounded-xl border bg-card p-6 shadow-sm">
              <Icon className="h-8 w-8 text-primary" />
              <h3 className="mt-4 font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
