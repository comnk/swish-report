"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/navigation";

interface Lineup {
  lineup_id: number;
  user_id: number;
  mode: string;
  players: Record<string, number>;
  scouting_report: {
    overallScore: number;
    strengths: string[];
    weaknesses: string[];
    synergyNotes: string;
    floor: string;
    ceiling: string;
    overallAnalysis: string;
  };
}

export default function PlayersLineupPage() {
  const [lineups, setLineups] = useState<Lineup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLineups() {
      try {
        const res = await fetch(`http://localhost:8000/community/lineups`);
        if (!res.ok)
          throw new Error(`Failed to fetch lineups: ${res.statusText}`);
        const data = await res.json();
        setLineups(data);
      } catch (err) {
        if (err instanceof Error) setError(err.message);
        else setError(String(err));
      } finally {
        setLoading(false);
      }
    }
    fetchLineups();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />

      <div className="max-w-7xl mx-auto p-6">
        <h1 className="text-4xl font-bold mb-8 text-gray-900 text-center">
          Community Lineups
        </h1>

        {loading && (
          <p className="text-center text-gray-600">Loading lineups...</p>
        )}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && lineups.length === 0 && (
          <p className="text-center text-gray-600">No lineups found.</p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {lineups.map((lineup) => (
            <div
              key={lineup.lineup_id}
              className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 p-6 flex flex-col justify-between"
            >
              {/* Header */}
              <div className="mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Lineup #{lineup.lineup_id}
                </h2>
                <p className="text-sm text-gray-500">Mode: {lineup.mode}</p>
              </div>

              {/* Score */}
              <div className="mb-4">
                <span className="text-sm font-semibold text-gray-600">
                  Score:
                </span>{" "}
                <span className="text-lg font-bold text-blue-600">
                  {lineup.scouting_report.overallScore}
                </span>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-green-700 mb-2">
                    Strengths
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {lineup.scouting_report.strengths
                      .slice(0, 3)
                      .map((s, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 rounded-full bg-green-100 text-green-800 text-xs font-medium"
                        >
                          {s}
                        </span>
                      ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-red-700 mb-2">
                    Weaknesses
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {lineup.scouting_report.weaknesses
                      .slice(0, 3)
                      .map((w, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 rounded-full bg-red-100 text-red-800 text-xs font-medium"
                        >
                          {w}
                        </span>
                      ))}
                  </div>
                </div>
              </div>

              {/* Analysis */}
              <p className="text-gray-700 text-sm line-clamp-3 mb-4 italic">
                &ldquo;{lineup.scouting_report.overallAnalysis}&rdquo;
              </p>

              {/* Link */}
              <a
                href={`/community/player-lineups/${lineup.lineup_id}`}
                className="self-start inline-flex items-center text-blue-600 font-semibold hover:text-blue-800 transition-colors"
              >
                View Full Analysis
                <span className="ml-1">→</span>
              </a>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
