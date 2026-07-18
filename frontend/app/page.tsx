"use client";

import { useState } from "react";
import Header from "@/components/Header";
import SearchBar from "@/components/SearchBar";
import SearchResults from "@/components/SearchResults";
import RepositoryManager from "@/components/RepositoryManager";
import ExplainView from "@/components/ExplainView";
import { useStore } from "@/lib/store";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"search" | "repos">("search");
  const { searchResults, explanation, isSearching } = useStore();

  return (
    <div className="min-h-screen">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "search" && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                CodeNexus
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Ask natural language questions about any codebase. Get relevant code snippets with AI-powered explanations.
              </p>
            </div>

            <SearchBar />

            {isSearching && (
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            )}

            {explanation && <ExplainView />}

            {searchResults && !explanation && <SearchResults />}
          </div>
        )}

        {activeTab === "repos" && <RepositoryManager />}
      </main>
    </div>
  );
}
