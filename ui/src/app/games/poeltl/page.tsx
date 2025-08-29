"use client";

import Navigation from "@/components/navigation";
import PlayerSearchPoeltl from "@/components/player-search-poeltl";
import { NBAPlayer } from "@/types/player";
import { useEffect, useState } from "react";

export default function Poeltl() {
  //   const [guesses, setGuesses] = useState<string[]>([]);
  //   const [targetPlayer, setTargetPlayer] = useState("");
  //   const [gameOver, setGameOver] = useState(false);
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

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

        setPlayers(mappedPlayers);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchNBAPlayers();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <PlayerSearchPoeltl
        level="nba"
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        allPlayers={players}
      />
      <div>Hello World!</div>
    </main>
  );
}
