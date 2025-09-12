"use client";

import Navigation from "@/components/navigation";
import PlayerSearchPoeltl from "@/components/player-search-poeltl";
import { NBAPlayer } from "@/types/player";
import { useEffect, useState } from "react";

function getLocalDateString(): string {
  return new Date().toLocaleDateString("en-CA");
}

function parseHeightToInches(height?: string | number): number {
  if (height === undefined || height === null) return -1;
  const s = String(height).trim();
  if (!s) return -1;

  if (/^\d+\-\d+$/.test(s)) {
    const [f, i] = s.split("-").map(Number);
    if (Number.isFinite(f) && Number.isFinite(i)) return f * 12 + i;
  }

  const ftInMatch = s.match(/(\d+)\s*'\s*(\d+)/);
  if (ftInMatch) {
    return Number(ftInMatch[1]) * 12 + Number(ftInMatch[2]);
  }

  const spaced = s.match(/^(\d+)\s+(\d+)$/);
  if (spaced) {
    return Number(spaced[1]) * 12 + Number(spaced[2]);
  }

  const nums = s.match(/\d+/g);
  if (nums && nums.length >= 2) {
    return Number(nums[0]) * 12 + Number(nums[1]);
  }

  if (/^\d+$/.test(s)) return Number(s);

  return -1;
}

function parseNumberLike(v?: string | number): number {
  if (v === undefined || v === null) return NaN;
  if (typeof v === "number") return v;
  const s = String(v).trim();
  if (!s) return NaN;
  if (/^\d+$/.test(s)) return Number(s);
  if (s.toLowerCase() === "rookie") return 0;
  // strip non-digits
  const cleaned = s.replace(/[^\d.-]/g, "");
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : NaN;
}

/** Normalize teams field to string[] */
function normalizeTeamsField(t: unknown): string[] {
  if (!t) return [];
  if (Array.isArray(t)) return t as string[];
  try {
    // if it's a JSON string like '["Boston Celtics"]'
    const parsed = JSON.parse(String(t));
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    // ignore
  }
  // fallback: comma-separated string
  return String(t)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function compareGuess(guess: NBAPlayer, target: NBAPlayer) {
  const guessH = parseHeightToInches(guess.height);
  const targetH = parseHeightToInches(target.height);

  const heightDir =
    guessH === targetH
      ? "equal"
      : !Number.isFinite(guessH) || !Number.isFinite(targetH)
      ? "equal"
      : guessH < targetH
      ? "up"
      : "down";

  const guessW = parseNumberLike(guess.weight);
  const targetW = parseNumberLike(target.weight);
  const weightDir =
    Number.isFinite(guessW) && Number.isFinite(targetW)
      ? guessW === targetW
        ? "equal"
        : guessW < targetW
        ? "up"
        : "down"
      : "equal";

  const guessY = parseNumberLike(guess.years_pro);
  const targetY = parseNumberLike(target.years_pro);
  const yearsDir =
    Number.isFinite(guessY) && Number.isFinite(targetY)
      ? guessY === targetY
        ? "equal"
        : guessY < targetY
        ? "up"
        : "down"
      : "equal";

  const posMatch =
    (guess.position || "").toLowerCase() ===
    (target.position || "").toLowerCase();

  const guessTeams = normalizeTeamsField(guess.team_names);
  const targetTeams = normalizeTeamsField(target.team_names);
  const matchingTeams = guessTeams.filter((t) => targetTeams.includes(t));

  return {
    position: posMatch,
    height: heightDir as "up" | "down" | "equal",
    weight: weightDir as "up" | "down" | "equal",
    years_pro: yearsDir as "up" | "down" | "equal",
    guessTeams,
    matchingTeams,
  };
}

export default function Poeltl() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [targetPlayer, setTargetPlayer] = useState<NBAPlayer | null>(null);
  const [guesses, setGuesses] = useState<NBAPlayer[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [gameEnded, setGameEnded] = useState(false);

  const [alreadyPlayedToday, setAlreadyPlayedToday] = useState(false);
  const MAX_GUESSES = 8;

  // Authentication states
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkedAuth, setCheckedAuth] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
    setCheckedAuth(true);

    const lastPlayed = localStorage.getItem("poeltl_last_played");
    const today = getLocalDateString();
    if (lastPlayed === today) {
      setAlreadyPlayedToday(true);
      setGameEnded(true);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    if (alreadyPlayedToday) {
      setLoading(false);
      return;
    }

    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok)
          throw new Error(`Error fetching NBA players: ${res.status}`);
        const data = await res.json();
        const mapped: NBAPlayer[] = data.map((p: Record<string, unknown>) => ({
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
        }));
        setPlayers(mapped);
      } catch (err) {
        console.error(err);
      }
    }

    async function fetchTargetPlayer() {
      try {
        const res = await fetch(
          "http://localhost:8000/games/poeltl/get-player"
        );
        if (!res.ok)
          throw new Error(`Error fetching target player: ${res.status}`);
        const data = await res.json();
        const target: NBAPlayer = {
          id: "target",
          full_name: data.full_name,
          position: data.position,
          height: data.height,
          weight: String(data.weight ?? ""),
          years_pro: `${data.years_pro}`,
          team_names: normalizeTeamsField(data.teams ?? data.team_names ?? []),
          college: "",
          draft_year: undefined,
          draft_round: undefined,
          draft_pick: undefined,
          stars: 0,
          strengths: [],
          weaknesses: [],
          aiAnalysis: "",
          overallRating: 0,
        };
        setTargetPlayer(target);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchNBAPlayers();
    fetchTargetPlayer();
  }, [isAuthenticated, alreadyPlayedToday]);

  const handleGuess = (playerName: string) => {
    if (!isAuthenticated || alreadyPlayedToday) return;
    if (!targetPlayer || gameEnded) return;

    const guessed = players.find((p) => p.full_name === playerName);
    if (!guessed) return;

    setGuesses((prev) => {
      const newGuesses = [...prev, guessed];
      if (
        guessed.full_name === targetPlayer.full_name ||
        newGuesses.length >= MAX_GUESSES
      ) {
        setShowModal(true);
        const today = getLocalDateString();
        localStorage.setItem("poeltl_last_played", today);
      }
      return newGuesses;
    });
  };

  if (!checkedAuth) return <p className="p-6">Checking login...</p>;

  if (!isAuthenticated)
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Navigation />
        <div className="flex flex-col items-center justify-center p-6 mt-8">
          <p className="p-6 text-red-600">
            You must be signed in to play Poeltl.
          </p>
        </div>
      </main>
    );

  if (alreadyPlayedToday)
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Navigation />
        <div className="flex flex-col items-center justify-center p-6 mt-8">
          <p className="text-lg font-medium text-black">
            ✅ You’ve already played Poeltl today! Come back tomorrow for the
            next round.
          </p>
        </div>
      </main>
    );

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="p-4">
        <PlayerSearchPoeltl
          level="nba"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          allPlayers={players}
          onSelectPlayer={handleGuess}
          disabled={gameEnded}
        />

        {loading ? (
          <p>Loading players...</p>
        ) : (
          targetPlayer && (
            <>
              <h2 className="text-xl font-bold my-4 text-black">Guesses</h2>
              <table className="min-w-full border border-gray-300 text-black">
                <thead className="bg-gray-200">
                  <tr>
                    <th className="p-2">Name</th>
                    <th className="p-2">Position</th>
                    <th className="p-2">Height</th>
                    <th className="p-2">Weight</th>
                    <th className="p-2">Years Pro</th>
                    <th className="p-2">Team</th>
                  </tr>
                </thead>
                <tbody>
                  {guesses.map((g, idx) => {
                    const result = compareGuess(g, targetPlayer);

                    return (
                      <tr key={idx} className="text-center border-t">
                        <td className="p-2">{g.full_name}</td>

                        {/* position */}
                        <td
                          className={`p-2 ${
                            result.position ? "bg-green-300" : "bg-red-300"
                          }`}
                        >
                          {g.position}
                        </td>

                        {/* height */}
                        <td className="p-2">
                          {g.height}{" "}
                          {result.height === "equal"
                            ? "✅"
                            : result.height === "up"
                            ? "⬆️"
                            : "⬇️"}
                        </td>

                        {/* weight */}
                        <td className="p-2">
                          {g.weight}{" "}
                          {result.weight === "equal"
                            ? "✅"
                            : result.weight === "up"
                            ? "⬆️"
                            : "⬇️"}
                        </td>

                        {/* years pro */}
                        <td className="p-2">
                          {g.years_pro}{" "}
                          {result.years_pro === "equal"
                            ? "✅"
                            : result.years_pro === "up"
                            ? "⬆️"
                            : "⬇️"}
                        </td>

                        {/* teams as badges, highlight only matching teams */}
                        <td className="p-2">
                          <div className="flex flex-wrap justify-center gap-2">
                            {result.guessTeams.length === 0 ? (
                              <span className="text-sm text-slate-600">—</span>
                            ) : (
                              result.guessTeams.map((team) => {
                                const isMatch =
                                  result.matchingTeams.includes(team);
                                return (
                                  <span
                                    key={team}
                                    className={`text-sm px-2 py-1 rounded-full border ${
                                      isMatch
                                        ? "bg-green-100 border-green-400 text-green-800"
                                        : "bg-slate-100 border-slate-200 text-slate-700"
                                    }`}
                                  >
                                    {team}
                                  </span>
                                );
                              })
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </>
          )
        )}
      </div>

      {showModal && targetPlayer && (
        <div className="fixed inset-0 flex items-center justify-center bg-gray-100/30 backdrop-blur-sm z-50">
          <div className="relative bg-white rounded-3xl shadow-xl p-8 max-w-sm w-full text-center">
            <button
              onClick={() => {
                setShowModal(false);
                setGameEnded(true);
              }}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-800 font-bold text-xl"
            >
              ✕
            </button>

            <h2 className="text-2xl font-bold text-black mb-6">
              {guesses.some((g) => g.full_name === targetPlayer.full_name)
                ? "🎉 Correct!"
                : "Game Over"}
            </h2>
            <div className="border-2 border-orange-500 rounded-xl p-4 mb-6 bg-orange-50">
              <p className="text-xl font-semibold text-orange-700">
                {targetPlayer.full_name}
              </p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
