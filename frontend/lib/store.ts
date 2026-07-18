import { create } from "zustand";

interface SearchItem {
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
}

interface SearchResults {
  query: string;
  repo_id?: string;
  results: SearchItem[];
  total_results: number;
  search_time_ms: number;
}

interface StoreState {
  searchResults: SearchResults | null;
  explanation: string | null;
  isSearching: boolean;
  selectedRepo: string | null;
  searchHistory: string[];

  setSearchResults: (results: SearchResults | null) => void;
  setExplanation: (explanation: string | null) => void;
  setIsSearching: (isSearching: boolean) => void;
  setSelectedRepo: (repoId: string | null) => void;
  addToHistory: (query: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  searchResults: null,
  explanation: null,
  isSearching: false,
  selectedRepo: null,
  searchHistory: typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("searchHistory") || "[]")
    : [],

  setSearchResults: (results) => set({ searchResults: results }),
  setExplanation: (explanation) => set({ explanation }),
  setIsSearching: (isSearching) => set({ isSearching }),
  setSelectedRepo: (repoId) => set({ selectedRepo: repoId }),
  addToHistory: (query) =>
    set((state) => {
      const history = [query, ...state.searchHistory.filter((q) => q !== query)].slice(0, 20);
      if (typeof window !== "undefined") {
        localStorage.setItem("searchHistory", JSON.stringify(history));
      }
      return { searchHistory: history };
    }),
}));
