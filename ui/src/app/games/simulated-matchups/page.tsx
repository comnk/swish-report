"use client";

import { useState, useEffect } from "react";
import {
  DndContext,
  DragOverlay,
  DragEndEvent,
  DragStartEvent,
} from "@dnd-kit/core";
import Navigation from "@/components/navigation";
import LineupSlot from "@/components/lineup-builder-slot";
import PlayerCard from "@/components/lineup-builder-card";
import { NBAPlayer } from "@/types/player";

interface MatchupResult {
  scoreA: number;
  scoreB: number;
  mvp: {
    id: string;
    name: string;
    team: "A" | "B";
    reason: string;
  };
  keyStats: {
    teamA: Record<string, number>;
    teamB: Record<string, number>;
  };
  reasoning: string;
}

export default function SimulatedMatchup() {
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [search, setSearch] = useState("");

  const initialSlots = [
    "PG",
    "SG",
    "SF",
    "PF",
    "C",
    "Bench1",
    "Bench2",
    "Bench3",
    "Bench4",
    "Bench5",
  ];

  const [teamALineup, setTeamALineup] = useState<Record<string, string | null>>(
    Object.fromEntries(initialSlots.map((slot) => [slot, null]))
  );
  const [teamBLineup, setTeamBLineup] = useState<Record<string, string | null>>(
    Object.fromEntries(initialSlots.map((slot) => [slot, null]))
  );

  const [activeDragId, setActiveDragId] = useState<string | null>(null);
  const [result, setResult] = useState<MatchupResult | null>(null);

  const starters = ["PG", "SG", "SF", "PF", "C"];
  const bench = ["Bench1", "Bench2", "Bench3", "Bench4", "Bench5"];

  // --- Map slots to teams for correct drag assignment ---
  const slotTeamMap: Record<string, "A" | "B"> = {};
  initialSlots.forEach((slot) => (slotTeamMap[`A-${slot}`] = "A"));
  initialSlots.forEach((slot) => (slotTeamMap[`B-${slot}`] = "B"));

  // --- Fetch Players ---
  useEffect(() => {
    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok)
          throw new Error(`Error fetching NBA players: ${res.status}`);
        const data = (await res.json()) as Record<string, unknown>[];

        const mappedPlayers: NBAPlayer[] = data.map((p) => ({
          id: String(p["player_uid"] ?? ""),
          full_name: String(p["full_name"] ?? ""),
          position: String(p["position"] ?? ""),
          height: String(p["height"] ?? ""),
          weight: String(p["weight"] ?? ""),
          team_names: (p["team_names"] as string[]) ?? [],
          college: p["colleges"]
            ? (p["colleges"] as string[]).join(", ")
            : undefined,
          years_pro: p["years_pro"] ? `${p["years_pro"]}` : "Rookie",
          draft_year: p["draft_year"] as number | undefined,
          draft_round: p["draft_round"] as number | undefined,
          draft_pick: p["draft_pick"] as number | undefined,
          stars: (p["stars"] as number) ?? 4,
          overallRating: (p["overallRating"] as number) ?? 85,
          strengths: (p["strengths"] as string[]) ?? ["athleticism", "defense"],
          weaknesses: (p["weaknesses"] as string[]) ?? ["turnovers"],
          aiAnalysis: String(
            p["aiAnalysis"] ?? `AI scouting report for ${p["full_name"] ?? ""}.`
          ),
        }));

        setPlayers(mappedPlayers);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchNBAPlayers();
  }, []);

  const handleSubmit = async () => {
    const validateLineup = (lineup: Record<string, string | null>) => {
      return [...starters, ...bench].every((pos) => lineup[pos] !== null);
    };

    if (!validateLineup(teamALineup) || !validateLineup(teamBLineup)) {
      alert(
        "Both teams must have all starters and bench slots filled before submitting."
      );
      return;
    }

    try {
      setLoadingSubmit(true); // 🔥 start loading
      const submission = {
        lineup1: teamALineup,
        lineup2: teamBLineup,
      };

      const res = await fetch(
        "http://localhost:8000/games/simulated-matchups/submit-matchup",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(submission),
        }
      );

      if (!res.ok) {
        throw new Error(`Submission failed: ${res.status}`);
      }

      const data = (await res.json()) as MatchupResult;
      setResult(data);
    } catch (err) {
      console.error("Error submitting lineups:", err);
    } finally {
      setLoadingSubmit(false); // 🔥 stop loading
    }
  };

  const filteredPlayers = players.filter((p) =>
    p.full_name.toLowerCase().includes(search.toLowerCase())
  );

  const handleDragStart = (event: DragStartEvent) =>
    setActiveDragId(event.active.id.toString());

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveDragId(null);
    if (!over) return;

    const playerId = active.id.toString();
    const targetSlotId = over.id.toString();

    const [teamPrefix, slot] = targetSlotId.split("-");

    setTeamALineup((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((pos) => {
        if (updated[pos] === playerId) updated[pos] = null;
      });
      return updated;
    });
    setTeamBLineup((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((pos) => {
        if (updated[pos] === playerId) updated[pos] = null;
      });
      return updated;
    });

    if (teamPrefix === "A")
      setTeamALineup((prev) => ({ ...prev, [slot]: playerId }));
    else if (teamPrefix === "B")
      setTeamBLineup((prev) => ({ ...prev, [slot]: playerId }));
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <Navigation />
      <div className="max-w-6xl mx-auto mt-10 bg-white p-8 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold mb-6 text-center text-black">
          Simulated Matchup
        </h1>

        {loading ? (
          <p className="text-gray-600 text-lg text-center">
            Loading players...
          </p>
        ) : (
          <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <div className="flex flex-col md:flex-row gap-6">
              {/* Team A */}
              <div className="flex-1">
                <h2 className="font-bold mb-2 text-center text-black">
                  Team A
                </h2>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-4">
                  {starters.map((pos) => (
                    <LineupSlot
                      key={`A-${pos}`}
                      id={`A-${pos}`}
                      playerId={teamALineup[pos]}
                      players={players}
                    />
                  ))}
                </div>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-4">
                  {bench.map((pos) => (
                    <LineupSlot
                      key={`A-${pos}`}
                      id={`A-${pos}`}
                      playerId={teamALineup[pos]}
                      players={players}
                    />
                  ))}
                </div>
              </div>

              {/* Team B */}
              <div className="flex-1">
                <h2 className="font-bold mb-2 text-center text-black">
                  Team B
                </h2>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-4">
                  {starters.map((pos) => (
                    <LineupSlot
                      key={`B-${pos}`}
                      id={`B-${pos}`}
                      playerId={teamBLineup[pos]}
                      players={players}
                    />
                  ))}
                </div>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-4">
                  {bench.map((pos) => (
                    <LineupSlot
                      key={`B-${pos}`}
                      id={`B-${pos}`}
                      playerId={teamBLineup[pos]}
                      players={players}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Player Library */}
            <LineupSlot id="LIBRARY" playerId={null} players={[]} isLibrary>
              <div className="h-64 w-full overflow-y-scroll rounded-lg border p-2 mt-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
                  {filteredPlayers.map((p) =>
                    !Object.values(teamALineup).includes(p.id) &&
                    !Object.values(teamBLineup).includes(p.id) ? (
                      <PlayerCard
                        key={p.id}
                        id={p.id}
                        name={p.full_name}
                        position={p.position}
                        height={p.height}
                        weight={p.weight}
                        overallRating={p.overallRating}
                        stars={p.stars}
                      />
                    ) : null
                  )}
                </div>
              </div>
            </LineupSlot>

            {/* Drag Overlay */}
            <DragOverlay>
              {activeDragId &&
                (() => {
                  const player = players.find((p) => p.id === activeDragId);
                  return player ? (
                    <PlayerCard
                      id={player.id}
                      name={player.full_name}
                      position={player.position}
                      height={player.height}
                      weight={player.weight}
                      overallRating={player.overallRating}
                      stars={player.stars}
                      isOverlay
                    />
                  ) : null;
                })()}
            </DragOverlay>
          </DndContext>
        )}

        {/* Search */}
        <div className="flex justify-center mt-4">
          <input
            type="text"
            placeholder="Search players..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md rounded-lg border px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none text-black"
          />
        </div>

        {/* Simulate Button */}
        <button
          onClick={handleSubmit}
          className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Submit Lineup & Simulate
        </button>

        {/* Results */}
        {loadingSubmit && (
          <div className="mt-6 p-4 bg-gray-200 rounded-lg text-center font-medium text-black">
            <p>Simulating matchup... 🏀</p>
          </div>
        )}

        {!loadingSubmit && result && (
          <div className="mt-6 space-y-6">
            {/* Predicted Score */}
            <div className="p-4 bg-gray-100 rounded-lg text-center font-medium text-black">
              <h2 className="font-bold mb-2 text-black text-xl">
                Predicted Score
              </h2>
              <p className="text-black text-lg">
                Team A: <span className="font-semibold">{result.scoreA}</span> -
                Team B: <span className="font-semibold">{result.scoreB}</span>
              </p>
            </div>

            {/* MVP Card */}
            <div className="p-4 rounded-2xl shadow-lg bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-200 text-black">
              <h3 className="text-xl font-bold mb-2">MVP 🏆</h3>
              <p className="text-lg font-semibold">
                {result.mvp.name}{" "}
                <span className="font-normal">
                  ({`Team ${result.mvp.team}`})
                </span>
              </p>
              <p className="text-sm italic mt-1">{result.mvp.reason}</p>
            </div>

            {/* Key Stats Tables */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Team A Stats */}
              <div className="bg-white rounded-lg shadow p-4 text-black">
                <h4 className="font-bold mb-2 text-center">Team A Stats</h4>
                <table className="w-full text-left border border-gray-300 text-black">
                  <tbody>
                    {Object.entries(result.keyStats.teamA).map(
                      ([stat, value]) => (
                        <tr
                          key={stat}
                          className="border-b border-gray-300 last:border-b-0 text-black hover:bg-gray-50"
                        >
                          <td className="px-2 py-1 font-medium text-black">
                            {stat}
                          </td>
                          <td className="px-2 py-1 text-black">{value}</td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>

              {/* Team B Stats */}
              <div className="bg-white rounded-lg shadow p-4 text-black">
                <h4 className="font-bold mb-2 text-center">Team B Stats</h4>
                <table className="w-full text-left border border-gray-300 text-black">
                  <tbody>
                    {Object.entries(result.keyStats.teamB).map(
                      ([stat, value]) => (
                        <tr
                          key={stat}
                          className="border-b border-gray-300 last:border-b-0 text-black hover:bg-gray-50"
                        >
                          <td className="px-2 py-1 font-medium text-black">
                            {stat}
                          </td>
                          <td className="px-2 py-1 text-black">{value}</td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Matchup Reasoning */}
            <div className="p-4 bg-gray-100 rounded-lg text-left text-gray-800">
              <h4 className="font-semibold mb-2">Matchup Analysis</h4>
              <p className="italic">{result.reasoning}</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
