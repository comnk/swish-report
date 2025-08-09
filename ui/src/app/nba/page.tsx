"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/navigation";
import PlayerGrid from "@/components/player-grid";
import PlayerSearch from "@/components/player-search";
import { NBAPlayer } from "@/types/player";

function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export default function NBAPage() {
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(12);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string>>({});

  useEffect(() => {
    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/players/nba");
        if (!res.ok) throw new Error(`Error fetching NBA players: ${res.status}`);
        const data: { full_name: string }[] = await res.json();

        const mappedPlayers: NBAPlayer[] = data.map((p, i) => ({
          id: `nba-${i}`,
          name: p.full_name,
          position: "SG",
          height: "6'5\"",
          weight: "210 lbs",
          school: "N/A",
          experience: "Veteran",
          stars: 5,
          overallRating: 90,
          stats: {
            points: 15 + i,
            rebounds: 5 + i,
            assists: 4 + i,
            fieldGoalPercentage: 0.45,
            threePointPercentage: 0.38,
            per: 15 + i,
            winShares: 3 + i * 0.1,
          },
          strengths: ["shooting", "defense", "athleticism"],
          weaknesses: ["turnovers", "free throws"],
          aiAnalysis: `Detailed AI analysis for ${p.full_name}.`,
          salary: "$15M",
        }));

        setPlayers(shuffleArray(mappedPlayers));
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchNBAPlayers();
  }, []);

  // Filtering logic based on searchTerm and selectedFilters
  const filteredPlayers = players.filter((player) => {
    // Search filter: name includes search term (case-insensitive)
    const matchesSearch =
      searchTerm === "" ||
      player.name.toLowerCase().includes(searchTerm.toLowerCase());

    // Filters: match all selected filters (if any)
    const matchesFilters = Object.entries(selectedFilters).every(([key, value]) => {
      if (!value) return true; // empty filter means ignore

      // For stars filter which is numeric but stored as string in filters (e.g. "5")
      if (key === "stars") {
        return player.stars.toString() === value;
      }

      // For salary filter, do a simple includes for ranges
      if (key === "salary") {
        return player.salary?.toLowerCase().includes(value.toLowerCase());
      }

      // For other keys, just compare lowercase strings
      const playerValue = (player as any)[key];
      if (!playerValue) return false;

      return playerValue.toString().toLowerCase() === value.toLowerCase();
    });

    return matchesSearch && matchesFilters;
  });

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            NBA <span className="gradient-text">Analysis</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Advanced analytics and career evaluations for current NBA players,
            including performance trends, trade value, and future projections.
          </p>
        </div>

        {/* League Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-purple-600">450+</div>
            <div className="text-slate-600">Active Players</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-red-600">30</div>
            <div className="text-slate-600">NBA Teams</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-orange-600">82</div>
            <div className="text-slate-600">Games/Season</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-green-600">$4.2B</div>
            <div className="text-slate-600">Total Salaries</div>
          </div>
        </div>

        {/* Player Search + Filters */}
        <PlayerSearch
          level="nba"
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
            <PlayerGrid players={filteredPlayers.slice(0, visibleCount)} level="nba" />

            {/* Show More Button */}
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