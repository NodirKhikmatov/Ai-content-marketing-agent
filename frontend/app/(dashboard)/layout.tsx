import { AuthGuard } from "@/components/auth/auth-guard";
import { AuthProvider } from "@/components/auth/auth-provider";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ProjectProvider } from "@/contexts/project-context";
import { requireUser } from "@/lib/auth/session";

export const dynamic = "force-dynamic";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  await requireUser();

  return (
    <AuthProvider>
      <ProjectProvider>
        <AuthGuard>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-background">
              <div className="container mx-auto p-8">{children}</div>
            </main>
          </div>
        </AuthGuard>
      </ProjectProvider>
    </AuthProvider>
  );
}
