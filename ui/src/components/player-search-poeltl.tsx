"use client";

import { useState, useEffect } from "react";
import { Search } from "lucide-react";

interface PlayerSearchProps {
  level: "high-school" | "college" | "nba";
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  allPlayers: string[];
  onSelectPlayer?: (player: string) => void; // optional callback (for guesses)
}

export default function PlayerSearchPoeltl({
  level,
  searchTerm,
  setSearchTerm,
  allPlayers,
  onSelectPlayer,
}: PlayerSearchProps) {
  const [filteredPlayers, setFilteredPlayers] = useState<string[]>([]);
  const [highlightIndex, setHighlightIndex] = useState(0);

  // Autocomplete filter logic
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredPlayers([]);
      return;
    }
    const results = allPlayers
      .filter((p) => p.toLowerCase().includes(searchTerm.toLowerCase()))
      .slice(0, 8);
    setFilteredPlayers(results);
    setHighlightIndex(0);
  }, [searchTerm, allPlayers]);

  const handleSelectPlayer = (player: string) => {
    setSearchTerm(player);
    setFilteredPlayers([]);
    onSelectPlayer?.(player);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (filteredPlayers.length === 0) return;

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
      {/* Search Input */}
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
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg shadow-sm
                        focus:ring-2 focus:ring-orange-500 focus:border-transparent
                        text-black placeholder-slate-400"
        />

        {/* Dropdown */}
        {filteredPlayers.length > 0 && (
          <ul
            className="absolute z-10 bg-white border border-slate-200 mt-1 w-full
                            rounded-lg shadow-lg max-h-64 overflow-y-auto"
          >
            {filteredPlayers.map((player, idx) => (
              <li
                key={player}
                className={`px-4 py-2 cursor-pointer transition-colors ${
                  idx === highlightIndex
                    ? "bg-orange-100 text-orange-900"
                    : "hover:bg-slate-100 text-black"
                }`}
                onMouseDown={() => handleSelectPlayer(player)}
              >
                {player}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
