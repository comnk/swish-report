"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/ui/navigation";
import PlayerSearch from "@/components/player-pages/player-search";
import PlayerGrid from "@/components/player-pages/player-grid";
import { HighSchoolPlayer } from "@/types/player";

// Fisher-Yates shuffle
function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export default function HighSchoolPage() {
  const [players, setPlayers] = useState<HighSchoolPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(12);

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilters, setSelectedFilters] = useState<
    Record<string, string>
  >({});

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const res = await fetch("http://localhost:8000/high-school/prospects");
        if (!res.ok) throw new Error(`Error ${res.status}`);

        const data = await res.json();

        const mapped: HighSchoolPlayer[] = data.map(
          (
            p: Partial<HighSchoolPlayer> & {
              school_name?: string;
              class_year?: string | number;
            }
          ) => ({
            id: String(p.id),
            full_name: p.full_name,
            position: p.position,
            school: p.school_name,
            class: p.class_year?.toString() ?? "",
            height: p.height,
            stars: p.stars ?? 4,
            overallRating: p.overallRating ?? 85,
            strengths: p.strengths ?? [
              "Scoring",
              "Athleticism",
              "Court Vision",
            ],
            weaknesses: p.weaknesses ?? ["Defense", "Consistency"],
            aiAnalysis:
              p.aiAnalysis ??
              "A highly talented high school prospect with excellent scoring ability and strong athletic traits.",
            weight: "",
          })
        );

        setPlayers(shuffleArray(mapped));
      } catch (error) {
        console.error("Failed to fetch high school prospects:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  // Filter logic
  const filteredPlayers = players.filter((player) => {
    const matchesSearch =
      searchTerm === "" ||
      player.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      player.school?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilters = (
      Object.entries(selectedFilters) as [keyof HighSchoolPlayer, string][]
    ).every(([key, value]) => {
      if (!value) return true;

      if (value.includes(",")) {
        const selectedValues = value
          .split(",")
          .map((v) => v.trim().toLowerCase());
        return selectedValues.includes(String(player[key]).toLowerCase());
      }

      return String(player[key]).toLowerCase() === value.toLowerCase();
    });

    return matchesSearch && matchesFilters;
  });

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            High School <span className="gradient-text">Prospects</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Discover the next generation of basketball talent with comprehensive
            AI-powered evaluations of high school players across the nation.
          </p>
        </div>

        {/* Search and Filters */}
        <PlayerSearch
          level="high-school"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedFilters={selectedFilters}
          setSelectedFilters={setSelectedFilters}
        />

        {/* Player Grid */}
        {loading ? (
          <p className="text-center">Loading...</p>
        ) : (
          <>
            <PlayerGrid
              players={filteredPlayers.slice(0, visibleCount)}
              level="high-school"
            />
            {visibleCount < filteredPlayers.length && (
              <div className="text-center mt-8">
                <button
                  onClick={() => setVisibleCount((count) => count + 12)}
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                >
                  Show More
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
