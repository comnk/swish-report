"use client";

import { useState } from "react";
import Court from "@/components/lineup-builder-court";
import Navigation from "@/components/navigation";
import { NBAPlayer } from "@/types/player";

export default function LineupBuilderGame() {
  const [lineup, setLineup] = useState<Record<string, string | null>>({
    PG: null,
    SG: null,
    SF: null,
    PF: null,
    C: null,
  });

  const handleSubmit = () => {
    console.log("Submitted lineup:", lineup);
    // TODO: call AI analysis endpoint
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="flex flex-col items-center p-6 space-y-6">
        <Court lineup={lineup} setLineup={setLineup} />

        <button
          onClick={handleSubmit}
          className="rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold shadow-md hover:bg-blue-700 transition-colors"
        >
          Submit Lineup for AI Analysis
        </button>
      </div>
    </main>
  );
}
