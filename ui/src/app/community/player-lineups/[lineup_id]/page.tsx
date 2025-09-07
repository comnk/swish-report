import Navigation from "@/components/navigation";
import { notFound } from "next/navigation";

interface Lineup {
  lineup_id: number;
  user_id: number;
  mode: string;
  players: Record<string, string>; // <-- now player names, not IDs
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

type Params = Promise<{ lineup_id: string }>;

async function fetchLineup(lineup_id: string): Promise<Lineup> {
  const res = await fetch(
    `http://fastapi-backend:8000/community/lineups/${lineup_id}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Lineup not found");
  return res.json();
}

export default async function PlayerLineupPage({ params }: { params: Params }) {
  const { lineup_id } = await params;
  let lineup: Lineup;

  try {
    lineup = await fetchLineup(lineup_id);
  } catch (err) {
    console.error(err);
    return notFound();
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        <header className="space-y-1">
          <h1 className="text-3xl font-bold text-gray-900">
            Lineup #{lineup.lineup_id}
          </h1>
          <p className="text-gray-600 font-medium">Mode: {lineup.mode}</p>
        </header>

        {/* Players Section */}
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
        <section className="bg-white shadow rounded-lg p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-black">Scouting Report</h2>

          <div className="space-y-2 text-black">
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
          </div>

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
      </div>
    </main>
  );
}
