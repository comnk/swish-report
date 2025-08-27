"use client";

import Navigation from "@/components/navigation";
import PlayerSearchPoeltl from "@/components/player-search-poeltl";
import { useState } from "react";

export default function Poeltl() {
  //   const [guesses, setGuesses] = useState<string[]>([]);
  //   const [targetPlayer, setTargetPlayer] = useState("");
  //   const [gameOver, setGameOver] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const nbaPlayers = [
    "LeBron James",
    "Stephen Curry",
    "Kevin Durant",
    "Luka Doncic",
    "Jayson Tatum",
    "Giannis Antetokounmpo",
    "Nikola Jokic",
    "Jimmy Butler",
    "Ja Morant",
    "Anthony Davis",
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <PlayerSearchPoeltl
        level="nba"
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        allPlayers={nbaPlayers}
      />
      <div>Hello World!</div>
    </main>
  );
}
