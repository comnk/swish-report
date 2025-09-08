"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/navigation";

interface ScoutingReport {
  overallScore: number;
  overallAnalysis: string;
}

interface Lineup {
  lineup_id: number;
  mode: string;
  scouting_report: ScoutingReport;
}

export default function Dashboard() {
  const [lineups, setLineups] = useState<Lineup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserLineups = async () => {
      const token = localStorage.getItem("token");
      const user_email = localStorage.getItem("user_email");

      if (!token || !user_email) {
        setError("You must be signed in to view your lineups.");
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(
          `http://localhost:8000/user/lineup-builder/${user_email}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || "Failed to fetch lineups.");
        }

        const data = await res.json();

        const parsedData = data.map((lineup: Lineup) => ({
          ...lineup,
          scouting_report:
            typeof lineup.scouting_report === "string"
              ? JSON.parse(lineup.scouting_report)
              : lineup.scouting_report,
        }));

        setLineups(parsedData);
      } catch (err) {
        console.error("Error fetching user lineups:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchUserLineups();
  }, []);

  console.log(lineups);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />

      <div className="max-w-4xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">My Lineups</h1>

        {loading ? (
          <p className="text-gray-500">Loading your lineups...</p>
        ) : error ? (
          <p className="text-red-600 font-medium">{error}</p>
        ) : lineups.length === 0 ? (
          <p className="text-gray-500">
            You haven’t created any lineups yet. Try building one!
          </p>
        ) : (
          <ul className="divide-y divide-gray-200 border border-gray-200 rounded-lg bg-white shadow">
            {lineups.map((lineup) => (
              <li
                key={lineup.lineup_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between hover:bg-slate-50 transition"
              >
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Lineup #{lineup.lineup_id}
                  </h2>
                  <p className="text-sm text-gray-500">Mode: {lineup.mode}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    Score:{" "}
                    <span className="font-semibold text-blue-600">
                      {lineup.scouting_report.overallScore}
                    </span>
                  </p>
                  <p className="text-sm text-gray-700 mt-2 line-clamp-2 italic">
                    “{lineup.scouting_report.overallAnalysis}”
                  </p>
                </div>

                <a
                  href={`/community/player-lineups/${lineup.lineup_id}`}
                  className="mt-3 sm:mt-0 inline-block text-blue-600 font-semibold hover:text-blue-800 transition"
                >
                  View →
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
