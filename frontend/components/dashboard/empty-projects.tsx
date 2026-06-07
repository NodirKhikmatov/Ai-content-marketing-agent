"use client";

import { FolderOpen, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface EmptyProjectsProps {
  onCreateClick: () => void;
}

export function EmptyProjects({ onCreateClick }: EmptyProjectsProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center py-16 text-center">
        <div className="rounded-full bg-accent p-4">
          <FolderOpen className="h-10 w-10 text-primary" />
        </div>
        <h3 className="mt-6 text-lg font-semibold">No projects yet</h3>
        <p className="mt-2 max-w-sm text-sm text-muted-foreground">
          Create your first project to analyze a website and generate a complete marketing strategy.
        </p>
        <Button className="mt-6" onClick={onCreateClick}>
          <Plus className="h-4 w-4" />
          Create your first project
        </Button>
      </CardContent>
    </Card>
  );
}
