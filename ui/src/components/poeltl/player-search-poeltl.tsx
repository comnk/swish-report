"use client";

import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { NBAPlayer } from "@/types/player";

interface PlayerSearchProps {
  level: "high-school" | "college" | "nba";
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  allPlayers: NBAPlayer[];
  onSelectPlayer?: (player: string) => void;
  disabled?: boolean; // disables input when game ends
}

export default function PlayerSearchPoeltl({
  level,
  searchTerm,
  setSearchTerm,
  allPlayers,
  onSelectPlayer,
  disabled = false,
}: PlayerSearchProps) {
  const [filteredPlayers, setFilteredPlayers] = useState<NBAPlayer[]>([]);
  const [highlightIndex, setHighlightIndex] = useState(0);

  // Autocomplete filter logic
  useEffect(() => {
    if (!searchTerm.trim() || disabled) {
      setFilteredPlayers([]);
      return;
    }

    const results = allPlayers
      .filter((p: NBAPlayer) =>
        p.full_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .slice(0, 8);

    setFilteredPlayers(results);
    setHighlightIndex(0);
  }, [searchTerm, allPlayers, disabled]);

  const handleSelectPlayer = (player: NBAPlayer) => {
    if (disabled) return;
    setSearchTerm(player.full_name);
    setFilteredPlayers([]);
    onSelectPlayer?.(player.full_name);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled || filteredPlayers.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIndex((i) => (i + 1) % filteredPlayers.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIndex((i) => (i === 0 ? filteredPlayers.length - 1 : i - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      handleSelectPlayer(filteredPlayers[highlightIndex]);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8">
      <div className="relative flex-1 max-w-xl mx-auto">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-black h-5 w-5" />
        <input
          type="text"
          placeholder={`Search ${
            level === "high-school" ? "high school" : level
          } players...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className={`w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg shadow-sm
            focus:ring-2 focus:ring-orange-500 focus:border-transparent
            text-black placeholder-slate-400
            ${
              disabled
                ? "bg-gray-100 cursor-not-allowed"
                : "bg-white cursor-text"
            }`}
        />

        {filteredPlayers.length > 0 && !disabled && (
          <ul className="absolute z-10 bg-white border border-slate-200 mt-1 w-full rounded-lg shadow-lg max-h-64 overflow-y-auto">
            {filteredPlayers.map((player, idx) => (
              <li
                key={player.id}
                className={`px-4 py-2 cursor-pointer transition-colors ${
                  idx === highlightIndex
                    ? "bg-orange-100 text-orange-900"
                    : "hover:bg-slate-100 text-black"
                }`}
                onMouseDown={() => handleSelectPlayer(player)}
              >
                {player.full_name}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
