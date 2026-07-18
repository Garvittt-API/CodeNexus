"use client";

import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useStore } from "@/lib/store";

const LANGUAGE_MAP: Record<string, string> = {
  python: "python",
  javascript: "javascript",
  typescript: "typescript",
  java: "java",
  cpp: "cpp",
  c: "c",
  go: "go",
  rust: "rust",
  ruby: "ruby",
  php: "php",
  swift: "swift",
  kotlin: "kotlin",
  scala: "scala",
  bash: "bash",
  html: "html",
  css: "css",
  json: "json",
  yaml: "yaml",
  toml: "toml",
  sql: "sql",
};

export default function SearchResults() {
  const { searchResults } = useStore();

  if (!searchResults || searchResults.results.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">No results found</h3>
        <p className="mt-2 text-gray-500 dark:text-gray-400">Try a different query or check your repository selection.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Results ({searchResults.total_results} found in {searchResults.search_time_ms.toFixed(0)}ms)
        </h2>
      </div>

      <div className="space-y-4">
        {searchResults.results.map((result) => (
          <ResultCard key={result.chunk_id} result={result} />
        ))}
      </div>
    </div>
  );
}

interface ResultCardProps {
  result: {
    chunk_id: string;
    file_path: string;
    language: string;
    content: string;
    start_line: number;
    end_line: number;
    chunk_type: string;
    name?: string;
    score: number;
    rank: number;
  };
}

function ResultCard({ result }: ResultCardProps) {
  const [expanded, setExpanded] = useState(false);
  const syntaxLang = LANGUAGE_MAP[result.language] || "text";

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden hover:border-gray-300 dark:hover:border-gray-700 transition-colors">
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900/50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">
            #{result.rank}
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">{result.file_path}</span>
              {result.name && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  &gt; {result.name}()
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                {result.language}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                lines {result.start_line}-{result.end_line}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {result.chunk_type}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Score: {result.score.toFixed(4)}
          </span>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-200 dark:border-gray-800">
          <SyntaxHighlighter
            language={syntaxLang}
            style={oneDark}
            showLineNumbers
            startingLine={result.start_line}
            customStyle={{
              margin: 0,
              borderRadius: 0,
              fontSize: "0.875rem",
              maxHeight: "400px",
            }}
          >
            {result.content}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  );
}
