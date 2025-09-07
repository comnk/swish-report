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
              className="bg-white rounded-3xl shadow-lg p-6 hover:shadow-2xl transition-shadow duration-300"
            >
              <h2 className="text-2xl font-semibold mb-2 text-gray-800">
                Lineup #{lineup.lineup_id}
              </h2>
              <p className="text-sm text-gray-500 mb-2">Mode: {lineup.mode}</p>
              <p className="font-medium text-gray-700 mb-4">
                Score: {lineup.scouting_report.overallScore}
              </p>

              <div className="mb-3">
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Strengths:
                </h3>
                <ul className="list-disc ml-5 text-sm text-green-600">
                  {lineup.scouting_report.strengths.slice(0, 3).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="mb-3">
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Weaknesses:
                </h3>
                <ul className="list-disc ml-5 text-sm text-red-600">
                  {lineup.scouting_report.weaknesses.slice(0, 3).map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>

              <p className="text-gray-700 text-sm line-clamp-4 mb-4">
                {lineup.scouting_report.overallAnalysis}
              </p>

              <a
                href={`/community/player-lineups/${lineup.lineup_id}`}
                className="inline-block mt-2 text-blue-600 font-semibold hover:text-blue-800 hover:underline transition-colors"
              >
                View Full Analysis →
              </a>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
