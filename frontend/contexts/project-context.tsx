"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { ApiError } from "@/services/api-client";
import { projectsService, type Project } from "@/services/projects";

const STORAGE_KEY = "active_project_id";

interface ProjectContextValue {
  projects: Project[];
  activeProject: Project | null;
  loading: boolean;
  error: string | null;
  selectProject: (id: string) => Promise<void>;
  createProject: (name: string, description?: string) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
  refreshProjects: () => Promise<void>;
  refreshActiveProject: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextValue | undefined>(undefined);

export function ProjectProvider({ children }: { children: React.ReactNode }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshActiveProject = useCallback(async () => {
    const storedId = localStorage.getItem(STORAGE_KEY);
    const projectId = storedId || projects[0]?.id;
    if (!projectId) {
      setActiveProject(null);
      return;
    }
    try {
      const detail = await projectsService.get(projectId);
      setActiveProject(detail);
      localStorage.setItem(STORAGE_KEY, projectId);
    } catch {
      if (projects[0]) {
        const detail = await projectsService.get(projects[0].id);
        setActiveProject(detail);
        localStorage.setItem(STORAGE_KEY, projects[0].id);
      }
    }
  }, [projects]);

  const refreshProjects = useCallback(async (): Promise<void> => {
    setError(null);
    try {
      const data = await projectsService.list();
      setProjects(data.items);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to load projects";
      setError(message);
    }
  }, []);

  useEffect(() => {
    async function init() {
      setLoading(true);
      setError(null);
      try {
        const data = await projectsService.list();
        setProjects(data.items);
        if (data.items.length > 0) {
          const storedId = localStorage.getItem(STORAGE_KEY);
          const targetId =
            storedId && data.items.some((p) => p.id === storedId) ? storedId : data.items[0].id;
          const detail = await projectsService.get(targetId);
          setActiveProject(detail);
          localStorage.setItem(STORAGE_KEY, targetId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load projects");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const selectProject = useCallback(async (id: string) => {
    const detail = await projectsService.get(id);
    setActiveProject(detail);
    localStorage.setItem(STORAGE_KEY, id);
  }, []);

  const createProject = useCallback(
    async (name: string, description?: string) => {
      setError(null);
      const project = await projectsService.create({ name, description });
      setProjects((prev) => [project, ...prev]);
      setActiveProject(project);
      localStorage.setItem(STORAGE_KEY, project.id);
      return project;
    },
    []
  );

  const deleteProject = useCallback(
    async (id: string) => {
      setError(null);
      await projectsService.delete(id);
      const remaining = projects.filter((p) => p.id !== id);
      setProjects(remaining);

      if (activeProject?.id === id) {
        if (remaining.length > 0) {
          await selectProject(remaining[0].id);
        } else {
          setActiveProject(null);
          localStorage.removeItem(STORAGE_KEY);
        }
      }
    },
    [projects, activeProject, selectProject]
  );

  const value = useMemo(
    () => ({
      projects,
      activeProject,
      loading,
      error,
      selectProject,
      createProject,
      deleteProject,
      refreshProjects,
      refreshActiveProject,
    }),
    [
      projects,
      activeProject,
      loading,
      error,
      selectProject,
      createProject,
      deleteProject,
      refreshProjects,
      refreshActiveProject,
    ]
  );

  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>;
}

export function useProject() {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProject must be used within ProjectProvider");
  }
  return context;
}
