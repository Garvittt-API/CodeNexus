"use client";

import { useStore } from "@/lib/store";
import SearchResults from "./SearchResults";

export default function ExplainView() {
  const { explanation, searchResults } = useStore();

  return (
    <div className="space-y-6">
      {explanation && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">AI</span>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">AI Explanation</h3>
          </div>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300 leading-relaxed">
              {explanation}
            </div>
          </div>
        </div>
      )}

      {searchResults && searchResults.results.length > 0 && (
        <SearchResults />
      )}
    </div>
  );
}
