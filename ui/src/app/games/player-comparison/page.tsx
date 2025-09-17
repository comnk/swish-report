"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/navigation";
import ComparisonBoard from "@/components/comparison-board";

interface SeasonStats {
  season: string;
  team: string;
  gp: number;
  ppg: number;
  apg: number;
  rpg: number;
  spg?: number;
  bpg?: number;
  topg?: number;
  fpg?: number;
  pts?: number;
  fga?: number;
  fgm?: number;
  three_pa?: number;
  three_pm?: number;
  fta?: number;
  ftm?: number;
  ts_pct?: number;
  fg?: number;
  efg?: number;
  three_p?: number;
  ft?: number;
  [key: string]: string | number | undefined;
}

interface PlayerStats {
  full_name: string;
  ppg: number;
  apg: number;
  rpg: number;
  all_seasons: SeasonStats[];
}

interface ComparisonData {
  player1: PlayerStats;
  player2: PlayerStats;
  ai_analysis?: string;
}

interface PlayerResponse {
  full_name: string;
  latest: {
    ppg: number | string;
    apg: number | string;
    rpg: number | string;
  };
  all_seasons: SeasonStats[];
  [key: string]: unknown;
}

export default function PlayerComparisonPage() {
  const [comparison, setComparison] = useState<
    Record<"Player1" | "Player2", string | null>
  >({ Player1: null, Player2: null });

  const [stats, setStats] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!comparison.Player1 || !comparison.Player2) return;

    const fetchStats = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(
          "http://localhost:8000/games/player-comparison/get-comparison",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              player1_id: comparison.Player1,
              player2_id: comparison.Player2,
            }),
          }
        );

        if (!res.ok) throw new Error("Failed to fetch comparison");

        const data: {
          player1: PlayerResponse;
          player2: PlayerResponse;
          ai_analysis?: string;
        } = await res.json();

        const parseStats = (p: PlayerResponse): PlayerStats => ({
          full_name: p.full_name,
          ppg: Number(p.latest.ppg),
          apg: Number(p.latest.apg),
          rpg: Number(p.latest.rpg),
          all_seasons: p.all_seasons,
        });

        setStats({
          player1: parseStats(data.player1),
          player2: parseStats(data.player2),
          ai_analysis: data.ai_analysis,
        });
      } catch (err: unknown) {
        if (err instanceof Error) {
          console.error("Error fetching comparison:", err);
          setError(err.message);
        } else {
          console.error("Unknown error:", err);
          setError("Unknown error");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [comparison]);

  const renderSeasonTable = (player: PlayerStats) => (
    <div className="mt-4 overflow-x-auto">
      <table className="table-auto w-full border border-gray-300 text-left text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="px-2 py-1">Season</th>
            <th className="px-2 py-1">Team</th>
            <th className="px-2 py-1">PPG</th>
            <th className="px-2 py-1">APG</th>
            <th className="px-2 py-1">RPG</th>
          </tr>
        </thead>
        <tbody>
          {player.all_seasons.map((s, idx) => (
            <tr key={idx} className="border-t border-gray-200">
              <td className="px-2 py-1">{s.season}</td>
              <td className="px-2 py-1">{s.team}</td>
              <td className="px-2 py-1">{s.ppg}</td>
              <td className="px-2 py-1">{s.apg}</td>
              <td className="px-2 py-1">{s.rpg}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="flex flex-col items-center p-6 w-full">
        <h2 className="text-3xl font-bold text-black mb-6">
          Compare Two NBA Players
        </h2>

        <ComparisonBoard
          comparison={comparison}
          setComparison={setComparison}
        />

        {loading && (
          <div className="mt-6 text-gray-700">Loading comparison...</div>
        )}
        {error && (
          <div className="mt-6 text-red-600 font-semibold">{error}</div>
        )}

        {!loading && !error && stats && (
          <div className="w-full max-w-5xl p-6 bg-white rounded-lg shadow-md mt-10 text-black">
            <h3 className="text-xl font-semibold mb-6 text-center">
              Comparison Stats
            </h3>

            <div className="grid grid-cols-2 gap-6 text-gray-700">
              {[stats.player1, stats.player2].map((player, idx) => (
                <div key={idx} className="text-center">
                  <h4 className="font-bold mb-2">{player.full_name}</h4>
                  {renderSeasonTable(player)}
                </div>
              ))}
            </div>

            {stats.ai_analysis && (
              <div className="mt-6 p-4 bg-slate-50 rounded-lg">
                <h4 className="font-bold text-center mb-2">AI Analysis</h4>
                <pre className="text-gray-800 whitespace-pre-wrap text-left">
                  {stats.ai_analysis}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
