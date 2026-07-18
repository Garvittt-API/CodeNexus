"use client";

import { useState, useEffect, useCallback } from "react";
import { useStore } from "@/lib/store";
import {
  listRepos,
  importRepo,
  deleteRepo,
  indexRepo,
  getIndexingStatus,
} from "@/lib/api";

interface Repository {
  id: string;
  name: string;
  source: string;
  source_type: string;
  status: string;
  total_files: number;
  total_lines: number;
  total_chunks: number;
  languages: Record<string, number>;
  functions: number;
  classes: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
}

export default function RepositoryManager() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [importSource, setImportSource] = useState("");
  const [importType, setImportType] = useState<"local" | "github" | "git">("local");
  const [importing, setImporting] = useState(false);
  const [indexingTasks, setIndexingTasks] = useState<Record<string, any>>({});
  const { setSelectedRepo, selectedRepo } = useStore();

  const fetchRepos = useCallback(async () => {
    try {
      const data = await listRepos();
      setRepos(data);
    } catch (error) {
      console.error("Failed to fetch repos:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRepos();
  }, [fetchRepos]);

  const handleImport = async () => {
    if (!importSource.trim()) return;
    setImporting(true);
    try {
      await importRepo(importSource, importType);
      setImportSource("");
      await fetchRepos();
    } catch (error) {
      console.error("Import failed:", error);
    } finally {
      setImporting(false);
    }
  };

  const handleIndex = async (repoId: string) => {
    try {
      const result = await indexRepo(repoId);
      setIndexingTasks((prev) => ({
        ...prev,
        [repoId]: { task_id: result.task_id, progress: 0 },
      }));
      pollIndexingStatus(repoId, result.task_id);
      await fetchRepos();
    } catch (error) {
      console.error("Indexing failed:", error);
    }
  };

  const pollIndexingStatus = async (repoId: string, taskId: string) => {
    const poll = async () => {
      try {
        const status = await getIndexingStatus(taskId);
        setIndexingTasks((prev) => ({
          ...prev,
          [repoId]: status,
        }));
        if (status.status === "running" || status.status === "pending") {
          setTimeout(poll, 1000);
        } else {
          await fetchRepos();
        }
      } catch (error) {
        console.error("Status poll failed:", error);
      }
    };
    poll();
  };

  const handleDelete = async (repoId: string) => {
    if (!confirm("Are you sure you want to delete this repository?")) return;
    try {
      await deleteRepo(repoId);
      if (selectedRepo === repoId) {
        setSelectedRepo(null);
      }
      await fetchRepos();
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    const path = e.dataTransfer.getData("text/plain");
    if (path) {
      setImportSource(path);
      setImportType("local");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Import Repository</h2>
        <div
          className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center hover:border-blue-400 dark:hover:border-blue-600 transition-colors"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Drag and drop a folder here, or use the form below
          </p>
        </div>

        <div className="mt-4 flex gap-4">
          <select
            value={importType}
            onChange={(e) => setImportType(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900"
          >
            <option value="local">Local Path</option>
            <option value="github">GitHub URL</option>
            <option value="git">Git URL</option>
          </select>
          <input
            type="text"
            value={importSource}
            onChange={(e) => setImportSource(e.target.value)}
            placeholder={
              importType === "local"
                ? "/path/to/repository"
                : "https://github.com/user/repo"
            }
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900"
          />
          <button
            onClick={handleImport}
            disabled={importing || !importSource.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg font-medium transition-colors"
          >
            {importing ? "Importing..." : "Import"}
          </button>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-4">Indexed Repositories</h2>
        {repos.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            No repositories imported yet. Import one above to get started.
          </div>
        ) : (
          <div className="space-y-4">
            {repos.map((repo) => (
              <RepoCard
                key={repo.id}
                repo={repo}
                isSelected={selectedRepo === repo.id}
                indexingTask={indexingTasks[repo.id]}
                onSelect={() => setSelectedRepo(repo.id === selectedRepo ? null : repo.id)}
                onIndex={() => handleIndex(repo.id)}
                onDelete={() => handleDelete(repo.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface RepoCardProps {
  repo: Repository;
  isSelected: boolean;
  indexingTask?: any;
  onSelect: () => void;
  onIndex: () => void;
  onDelete: () => void;
}

function RepoCard({ repo, isSelected, indexingTask, onSelect, onIndex, onDelete }: RepoCardProps) {
  const statusColors: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    indexing: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    completed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };

  return (
    <div
      className={`border rounded-xl p-4 transition-all ${
        isSelected
          ? "border-blue-500 bg-blue-50 dark:bg-blue-950/20"
          : "border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="cursor-pointer" onClick={onSelect}>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">{repo.name}</h3>
            <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[repo.status] || ""}`}>
              {repo.status}
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{repo.source}</p>
          {repo.status === "completed" && (
            <div className="flex gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span>{repo.total_files} files</span>
              <span>{repo.total_lines.toLocaleString()} lines</span>
              <span>{repo.total_chunks} chunks</span>
              <span>{repo.functions} functions</span>
              <span>{repo.classes} classes</span>
            </div>
          )}
          {repo.languages && Object.keys(repo.languages).length > 0 && (
            <div className="flex gap-2 mt-2 flex-wrap">
              {Object.entries(repo.languages)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([lang, count]) => (
                  <span key={lang} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">
                    {lang} ({count})
                  </span>
                ))}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {repo.status !== "indexing" && (
            <button
              onClick={onIndex}
              className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              {repo.status === "completed" ? "Re-index" : "Index"}
            </button>
          )}
          <button
            onClick={onDelete}
            className="px-3 py-1.5 text-xs bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Delete
          </button>
        </div>
      </div>

      {indexingTask && indexingTask.status === "running" && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>{indexingTask.current_file || "Processing..."}</span>
            <span>{Math.round((indexingTask.progress || 0) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(indexingTask.progress || 0) * 100}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {indexingTask.processed_files || 0} / {indexingTask.total_files || 0} files
          </div>
        </div>
      )}

      {repo.error_message && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-400">
          {repo.error_message}
        </div>
      )}
    </div>
  );
}
