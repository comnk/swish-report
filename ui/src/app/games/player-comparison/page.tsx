"use client";

import { useState } from "react";
import Navigation from "@/components/navigation";
import ComparisonBoard from "@/components/comparison-board";

export default function PlayerComparisonPage() {
  const [comparison, setComparison] = useState<
    Record<"Player1" | "Player2", string | null>
  >({
    Player1: null,
    Player2: null,
  });

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="flex flex-col items-center p-6 w-full">
        <h2 className="text-3xl font-bold text-black mb-6">
          Compare Two NBA Players
        </h2>

        <ComparisonBoard
          comparison={comparison}
          setComparison={setComparison}
        />

        {comparison.Player1 && comparison.Player2 && (
          <div className="w-full max-w-4xl p-6 bg-white rounded-lg shadow-md mt-10 text-black">
            <h3 className="text-xl font-semibold mb-6 text-center">
              Comparison Stats
            </h3>
            <div className="grid grid-cols-2 gap-6 text-gray-700">
              <div className="text-left">
                <h4 className="font-bold mb-2 text-center">Player 1</h4>
                <ul className="list-disc list-inside">
                  <li>PPG: --</li>
                  <li>APG: --</li>
                  <li>RPG: --</li>
                </ul>
              </div>
              <div className="text-left">
                <h4 className="font-bold mb-2 text-center">Player 2</h4>
                <ul className="list-disc list-inside">
                  <li>PPG: --</li>
                  <li>APG: --</li>
                  <li>RPG: --</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
