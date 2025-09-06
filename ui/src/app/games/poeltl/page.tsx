"use client";

import Navigation from "@/components/navigation";
import PlayerSearchPoeltl from "@/components/player-search-poeltl";
import { NBAPlayer } from "@/types/player";
import { useEffect, useState } from "react";

export default function Poeltl() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [targetPlayer, setTargetPlayer] = useState<NBAPlayer | null>(null);
  const [guesses, setGuesses] = useState<NBAPlayer[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [gameEnded, setGameEnded] = useState(false);

  const MAX_GUESSES = 8;

  // Authentication states
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkedAuth, setCheckedAuth] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
    setCheckedAuth(true); // finished checking auth
  }, []);

  // Fetch players and target only if logged in
  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false); // stop loading if not logged in
      return;
    }

    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok)
          throw new Error(`Error fetching NBA players: ${res.status}`);

        const data = await res.json();
        const mappedPlayers: NBAPlayer[] = data.map(
          (p: Record<string, unknown>) => ({
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
            stats: (p["stats"] as NBAPlayer["stats"]) ?? {
              points: 0,
              rebounds: 0,
              assists: 0,
              fieldGoalPercentage: 0,
              threePointPercentage: 0,
              per: 0,
              winShares: 0,
            },
          })
        );
        setPlayers(mappedPlayers);
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
          weight: data.weight,
          years_pro: `${data.years_pro}`,
          team_names: JSON.parse(data.teams || "[]"),
          college: "",
          draft_year: undefined,
          draft_round: undefined,
          draft_pick: undefined,
          stats: {
            points: 0,
            rebounds: 0,
            assists: 0,
            fieldGoalPercentage: 0,
            threePointPercentage: 0,
            per: 0,
            winShares: 0,
          },
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
  }, [isAuthenticated]);

  const handleGuess = (playerName: string) => {
    if (!isAuthenticated) return; // block if not logged in
    if (!targetPlayer || gameEnded) return;

    const guessedPlayer = players.find((p) => p.full_name === playerName);
    if (!guessedPlayer) return;

    setGuesses((prev) => {
      const newGuesses = [...prev, guessedPlayer];
      if (
        guessedPlayer.full_name === targetPlayer.full_name ||
        newGuesses.length >= MAX_GUESSES
      ) {
        setShowModal(true);
      }
      return newGuesses;
    });
  };

  const compareGuess = (guess: NBAPlayer, target: NBAPlayer) => ({
    position: guess.position === target.position,
    height:
      guess.height === target.height
        ? "equal"
        : guess.height > target.height
        ? "lower"
        : "higher",
    weight:
      guess.weight === target.weight
        ? "equal"
        : guess.weight > target.weight
        ? "lower"
        : "higher",
    years_pro:
      guess.years_pro === target.years_pro
        ? "equal"
        : Number(guess.years_pro) > Number(target.years_pro)
        ? "lower"
        : "higher",
    team: guess.team_names.some((t) => target.team_names.includes(t)),
  });

  if (!checkedAuth) return <p className="p-6">Checking login...</p>;

  if (!isAuthenticated)
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Navigation />
        <div className="flex flex-col items-center justify-center p-6 mt-8">
          <p className="text-red-600 text-lg font-medium mb-4">
            You must be signed in to play Poeltl.
          </p>
          <a
            href="/login"
            className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 transition"
          >
            Go to Login
          </a>
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
                        <td
                          className={`p-2 ${
                            result.position ? "bg-green-300" : "bg-red-300"
                          }`}
                        >
                          {g.position}
                        </td>
                        <td className="p-2">
                          {g.height}{" "}
                          {result.height === "higher"
                            ? "⬆️"
                            : result.height === "lower"
                            ? "⬇️"
                            : "✅"}
                        </td>
                        <td className="p-2">
                          {g.weight}{" "}
                          {result.weight === "higher"
                            ? "⬆️"
                            : result.weight === "lower"
                            ? "⬇️"
                            : "✅"}
                        </td>
                        <td className="p-2">
                          {g.years_pro}{" "}
                          {result.years_pro === "higher"
                            ? "⬆️"
                            : result.years_pro === "lower"
                            ? "⬇️"
                            : "✅"}
                        </td>
                        <td
                          className={`p-2 ${
                            result.team ? "bg-green-300" : "bg-red-300"
                          }`}
                        >
                          {g.team_names.join(", ")}
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
            <button
              onClick={() => window.location.reload()}
              className="bg-orange-500 text-white px-6 py-3 rounded-xl text-lg font-semibold hover:bg-orange-600 transition"
            >
              Play Again
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
