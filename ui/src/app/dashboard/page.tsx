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

interface HotTake {
  take_id: number;
  content: string;
  truthfulness_score: number;
}

export default function Dashboard() {
  const [lineups, setLineups] = useState<Lineup[]>([]);
  const [hotTakes, setHotTakes] = useState<HotTake[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      const user_email = localStorage.getItem("user_email");

      if (!token || !user_email) {
        setError("You must be signed in to view your dashboard.");
        setLoading(false);
        return;
      }

      // Decode JWT to check expiration
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const exp = payload.exp * 1000; // convert to milliseconds
        if (Date.now() > exp) {
          setError("Session expired. Please log in again.");
          localStorage.clear();
          window.location.href = "/login";
          return;
        }
      } catch (err) {
        console.error("Invalid token:", err);
        setError("Invalid session. Please log in again.");
        localStorage.clear();
        window.location.href = "/login";
        return;
      }

      try {
        // Fetch lineups
        const lineupRes = await fetch(
          `http://localhost:8000/user/lineup-builder/${user_email}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (!lineupRes.ok) {
          const errorData = await lineupRes.json();
          throw new Error(errorData.detail || "Failed to fetch lineups.");
        }

        const lineupData = await lineupRes.json();
        const parsedLineups = lineupData.map((lineup: Lineup) => ({
          ...lineup,
          scouting_report:
            typeof lineup.scouting_report === "string"
              ? JSON.parse(lineup.scouting_report)
              : lineup.scouting_report,
        }));
        setLineups(parsedLineups);

        // Fetch hot takes
        const hotTakeRes = await fetch(
          `http://localhost:8000/user/hot-takes/${user_email}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (!hotTakeRes.ok) {
          const errorData = await hotTakeRes.json();
          throw new Error(errorData.detail || "Failed to fetch hot takes.");
        }

        const hotTakeData: HotTake[] = await hotTakeRes.json();
        setHotTakes(hotTakeData);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />

      <div className="max-w-4xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">My Dashboard</h1>

        {loading ? (
          <p className="text-gray-500">Loading your data...</p>
        ) : error ? (
          <p className="text-red-600 font-medium">{error}</p>
        ) : (
          <>
            {/* Lineups Section */}
            <section className="mb-10">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                My Lineups
              </h2>
              {lineups.length === 0 ? (
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
                        <h3 className="text-lg font-semibold text-gray-900">
                          Lineup #{lineup.lineup_id}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Mode: {lineup.mode}
                        </p>
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
            </section>

            {/* Hot Takes Section */}
            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                My Hot Takes
              </h2>
              {hotTakes.length === 0 ? (
                <p className="text-gray-500">
                  You haven’t posted any hot takes yet.
                </p>
              ) : (
                <ul className="divide-y divide-gray-200 border border-gray-200 rounded-lg bg-white shadow">
                  {hotTakes.map((take) => (
                    <li
                      key={take.take_id}
                      className="p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between hover:bg-slate-50 transition"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-900 font-medium break-words line-clamp-3">
                          {take.content}
                        </p>
                        <p className="text-sm text-gray-600 mt-2">
                          Truthfulness Score:{" "}
                          <span className="font-semibold text-blue-600">
                            {take.truthfulness_score}%
                          </span>
                        </p>
                      </div>

                      <a
                        href={`/community/hot-takes/${take.take_id}`}
                        className="mt-3 sm:mt-0 sm:ml-4 inline-block shrink-0 text-blue-600 font-semibold hover:text-blue-800 transition"
                      >
                        View →
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
