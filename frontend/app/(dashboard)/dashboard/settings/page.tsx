"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { UsageMeter } from "@/components/dashboard/usage-meter";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { userService, type UsageStats, type UserProfile } from "@/services/user";

const PLAN_LIMITS: Record<string, { analyses: number; regenerations: number }> = {
  free: { analyses: 1, regenerations: 10 },
  pro: { analyses: 10, regenerations: 100 },
  team: { analyses: 50, regenerations: 500 },
  agency: { analyses: 200, regenerations: 2000 },
};

export default function SettingsPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [profileData, usageData] = await Promise.all([
          userService.getProfile(),
          userService.getUsage(),
        ]);
        setProfile(profileData);
        setUsage(usageData);
        setFullName(profileData.full_name || "");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const updated = await userService.updateProfile({ full_name: fullName });
      setProfile(updated);
      setMessage("Profile updated successfully");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const planLimits = PLAN_LIMITS[usage?.plan || "free"] ?? PLAN_LIMITS.free;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full name</Label>
              <Input id="name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={profile?.email || user?.email || ""}
                disabled
              />
            </div>
            {message && <p className="text-sm text-green-600">{message}</p>}
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save changes"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Usage &amp; billing</CardTitle>
          <CardDescription>Monthly limits reset on the 1st of each month</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {usage && <UsageMeter usage={usage} />}

          <div className="rounded-lg border bg-muted/40 p-4 text-sm">
            <p className="font-medium">Plan comparison</p>
            <ul className="mt-2 space-y-1 text-muted-foreground">
              <li>
                <span className="font-medium text-foreground">Free</span> —{" "}
                {PLAN_LIMITS.free.analyses} analysis/month, {PLAN_LIMITS.free.regenerations}{" "}
                regenerations/month
              </li>
              <li>
                <span className="font-medium text-foreground">Pro</span> —{" "}
                {PLAN_LIMITS.pro.analyses} analyses/month, {PLAN_LIMITS.pro.regenerations}{" "}
                regenerations/month
              </li>
            </ul>
            <p className="mt-3 text-xs">
              Your current plan includes up to {planLimits.analyses} analyses and{" "}
              {planLimits.regenerations} regenerations per month.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
