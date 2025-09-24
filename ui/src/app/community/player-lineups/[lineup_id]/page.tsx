"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Navigation from "@/components/ui/navigation";
import CommentsSection from "@/components/comments/threaded-comments";

interface Lineup {
  lineup_id: number;
  user_id: number;
  mode: string;
  players: Record<string, string>;
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

export default function PlayerLineupPage() {
  const pathname = usePathname(); // e.g., /community/lineups/12
  const lineup_id = pathname.split("/").pop();

  const [lineup, setLineup] = useState<Lineup | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user_email = localStorage.getItem("user_email");

    if (!token || !user_email) {
      setError("You must be signed in to view and comment.");
      setLoading(false);
      return;
    }

    const fetchLineup = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/community/lineups/${lineup_id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) throw new Error("Lineup not found.");
        const data: Lineup = await res.json();
        setLineup(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    const fetchUsername = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/user/get-username/${user_email}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) throw new Error("Failed to fetch username.");
        const data = await res.json();
        setUsername(data.username);
      } catch (err) {
        console.error("Failed to fetch username:", err);
      }
    };

    if (lineup_id) {
      fetchLineup();
      fetchUsername();
    }
  }, [lineup_id]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {loading && <p>Loading lineup...</p>}
        {error && <p className="text-red-600">{error}</p>}

        {lineup && (
          <>
            <header className="space-y-1">
              <h1 className="text-3xl font-bold text-gray-900">
                Lineup #{lineup.lineup_id}
              </h1>
              <p className="text-gray-600 font-medium">Mode: {lineup.mode}</p>
            </header>

            {/* Players */}
            <section className="bg-white shadow rounded-lg p-6 text-black">
              <h2 className="text-2xl font-semibold mb-4">Players</h2>
              <ul className="grid grid-cols-2 gap-2">
                {Object.entries(lineup.players).map(([pos, playerName]) => (
                  <li
                    key={pos}
                    className="flex justify-between bg-gray-50 p-2 rounded"
                  >
                    <span className="font-semibold">{pos}</span>
                    <span>{playerName}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* Scouting Report */}
            <section className="bg-white shadow rounded-lg p-6 space-y-4 text-black">
              <h2 className="text-2xl font-semibold text-black">
                Scouting Report
              </h2>
              <p>
                <strong>Overall Score:</strong>{" "}
                <span className="text-blue-600">
                  {lineup.scouting_report.overallScore}
                </span>
              </p>
              <p>
                <strong>Synergy Notes:</strong>{" "}
                {lineup.scouting_report.synergyNotes}
              </p>
              <p>
                <strong>Floor:</strong> {lineup.scouting_report.floor}
              </p>
              <p>
                <strong>Ceiling:</strong> {lineup.scouting_report.ceiling}
              </p>
              <p>
                <strong>Overall Analysis:</strong>{" "}
                {lineup.scouting_report.overallAnalysis}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                {/* Strengths */}
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-green-600">
                    Strengths
                  </h3>
                  <div className="space-y-2">
                    {lineup.scouting_report.strengths.map((s, i) => (
                      <div
                        key={i}
                        className="bg-green-100 text-green-800 p-3 rounded-lg shadow-sm"
                      >
                        {s}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Weaknesses */}
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-red-600">
                    Weaknesses
                  </h3>
                  <div className="space-y-2">
                    {lineup.scouting_report.weaknesses.map((w, i) => (
                      <div
                        key={i}
                        className="bg-red-100 text-red-800 p-3 rounded-lg shadow-sm"
                      >
                        {w}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Community Discussion */}
            <section className="bg-white shadow rounded-lg p-6 space-y-4">
              <h2 className="text-2xl font-semibold text-black">
                Community Discussion
              </h2>
              {username ? (
                <CommentsSection
                  parentId={lineup.lineup_id}
                  contextType="lineup"
                  username={username}
                />
              ) : (
                <p className="text-gray-500 mt-4">
                  Sign in to participate in the discussion.
                </p>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
