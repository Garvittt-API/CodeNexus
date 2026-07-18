"use client";

import { useState, useCallback } from "react";
import { useStore } from "@/lib/store";
import { searchCode, searchAndExplain } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "How does authentication work in this codebase?",
  "Find the main data processing pipeline",
  "Where is error handling implemented?",
  "Show me the database connection logic",
  "Find all API endpoint definitions",
  "How is caching implemented?",
  "Where are the tests located?",
  "Find the configuration management code",
];

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [withExplanation, setWithExplanation] = useState(true);
  const { setSearchResults, setExplanation, setIsSearching, selectedRepo } = useStore();

  const handleSearch = useCallback(
    async (searchQuery?: string) => {
      const q = searchQuery || query;
      if (!q.trim()) return;

      setIsSearching(true);
      setExplanation(null);
      setSearchResults(null);

      try {
        if (withExplanation) {
          const response = await searchAndExplain(q, selectedRepo || undefined);
          setExplanation(response.explanation);
          setSearchResults(response);
        } else {
          const response = await searchCode(q, selectedRepo || undefined);
          setSearchResults(response);
        }
      } catch (error) {
        console.error("Search failed:", error);
      } finally {
        setIsSearching(false);
      }
    },
    [query, withExplanation, selectedRepo, setSearchResults, setExplanation, setIsSearching]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the codebase..."
          className="w-full pl-12 pr-32 py-4 border border-gray-300 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          rows={2}
        />
        <div className="absolute inset-y-0 right-0 flex items-center gap-2 pr-3">
          <label className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={withExplanation}
              onChange={(e) => setWithExplanation(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            AI Explain
          </label>
          <button
            onClick={() => handleSearch()}
            disabled={!query.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.slice(0, 4).map((example) => (
          <button
            key={example}
            onClick={() => {
              setQuery(example);
              handleSearch(example);
            }}
            className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
