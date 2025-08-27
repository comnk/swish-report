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
  const [selectedFilters, setSelectedFilters] = useState<
    Record<string, string>
  >({});

  useEffect(() => {
    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok)
          throw new Error(`Error fetching NBA players: ${res.status}`);

        // Expecting localhost to return all the DB fields you listed
        const data = await res.json();

        const mappedPlayers: NBAPlayer[] = data.map(
          (p: Record<string, unknown>) => {
            const player = p as unknown as Record<string, unknown>; // Treat as generic object temporarily
            return {
              id: String(player["player_uid"] ?? ""), // fallback if missing
              full_name: String(player["full_name"] ?? ""),
              position: String(player["position"] ?? ""),
              height: String(player["height"] ?? ""),
              weight: String(player["weight"] ?? ""),
              team_names: (player["team_names"] as string[]) ?? [],
              college: player["colleges"]
                ? (player["colleges"] as string[]).join(", ")
                : undefined,
              years_pro: player["years_pro"]
                ? `${player["years_pro"]}`
                : "Rookie",
              draft_year: player["draft_year"] as number | undefined,
              draft_round: player["draft_round"] as number | undefined,
              draft_pick: player["draft_pick"] as number | undefined,
              stars: (player["stars"] as number) ?? 4,
              overallRating: (player["overallRating"] as number) ?? 85,
              strengths: (player["strengths"] as string[]) ?? [
                "athleticism",
                "defense",
              ],
              weaknesses: (player["weaknesses"] as string[]) ?? ["turnovers"],
              aiAnalysis: String(
                player["aiAnalysis"] ??
                  `AI scouting report for ${player["full_name"] ?? ""}.`
              ),
              stats: (player["stats"] as NBAPlayer["stats"]) ?? {
                points: 0,
                rebounds: 0,
                assists: 0,
                fieldGoalPercentage: 0,
                threePointPercentage: 0,
                per: 0,
                winShares: 0,
              },
            } as NBAPlayer;
          }
        );

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
    const matchesSearch =
      searchTerm === "" ||
      player.full_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilters = (
      Object.entries(selectedFilters) as [keyof NBAPlayer, string][]
    ).every(([key, value]) => {
      if (!value) return true;

      // For stars filter which is numeric but stored as string
      if (key === "stars") {
        return player.stars.toString() === value;
      }

      const playerValue = player[key];

      if (playerValue === undefined || playerValue === null) return false;

      // If it's a primitive, compare as string
      if (typeof playerValue === "string" || typeof playerValue === "number") {
        return playerValue.toString().toLowerCase() === value.toLowerCase();
      }

      // If it's an array (like team_names), check inclusion
      if (Array.isArray(playerValue)) {
        return playerValue
          .map(String)
          .map((v) => v.toLowerCase())
          .includes(value.toLowerCase());
      }

      // Otherwise, cannot compare
      return false;
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
            <PlayerGrid
              players={filteredPlayers.slice(0, visibleCount)}
              level="nba"
            />

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
