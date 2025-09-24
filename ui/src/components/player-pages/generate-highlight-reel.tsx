"use client"; // THIS IS REQUIRED

import React from "react";
import { HighSchoolPlayer, NBAPlayer } from "@/types/player";

interface Props {
  player: HighSchoolPlayer | NBAPlayer;
}

export default function GenerateHighlightButton({ player }: Props) {
  const handleClick = async () => {
    try {
      const endpoint =
        "school" in player
          ? `http://localhost:8000/high-school/prospects/${player.id}/reel`
          : `http://localhost:8000/nba/players/${player.id}/reel`;

      const res = await fetch(endpoint, { method: "GET" });
      if (!res.ok) throw new Error("Failed to generate reel");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `${player.full_name.replace(" ", "_")}_highlight.mp4`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to generate highlight reel. Try again later.");
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 flex flex-col items-center mb-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
        Generate Highlights Reel
      </h2>
      <button
        onClick={handleClick}
        className="px-6 py-3 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition"
      >
        Generate Highlight Reel
      </button>
    </div>
  );
}
