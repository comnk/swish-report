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
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok) throw new Error(`Error fetching NBA players: ${res.status}`);
        
        // Expecting backend to return all the DB fields you listed
        const data: {
          player_uid: number;
          full_name: string;
          position: string;
          height: string;
          weight: string;
          yearMin: number;
          yearMax: number;
          team_names: string[];
          draft_round: number | null;
          draft_pick: number | null;
          draft_year: number | null;
          years_pro: number;
          colleges: string[];
          high_schools: string[];
          is_active: boolean;
          accolades: string[];
        }[] = await res.json();

        const mappedPlayers: NBAPlayer[] = data.map((p) => ({
          id: String(p.player_uid),
          name: p.full_name,
          position: p.position,
          height: p.height,
          weight: p.weight,
          team_names: p.team_names,
          school: (p.colleges?.length ? p.colleges.join(", ") : (p.high_schools || []).join(", ")),
          experience: p.years_pro > 0 ? `${p.years_pro} years pro` : "Rookie",
          draftInfo: p.draft_year
            ? `Draft ${p.draft_year} • R${p.draft_round} P${p.draft_pick}`
            : "Undrafted",
          isActive: p.is_active,
          accolades: p.accolades,
          stats: {
            // These are placeholders unless you join game stats table later
            points: 0,
            rebounds: 0,
            assists: 0,
            fieldGoalPercentage: 0,
            threePointPercentage: 0,
            per: 0,
            winShares: 0,
          },
          strengths: ["athleticism", "defense"], // placeholder until you add evals
          weaknesses: ["turnovers"], // placeholder
          aiAnalysis: `AI scouting report for ${p.full_name}.`,
          overallRating: 85, // could be computed later from stats/AI
          stars: 4,
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