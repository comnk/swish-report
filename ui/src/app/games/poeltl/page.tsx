"use client";

import Navigation from "@/components/navigation";
import PlayerSearch from "@/components/player-search";
import { useState } from "react";

export default function Poeltl() {
    const [guesses, setGuesses] = useState<string[]>([]);
    const [targetPlayer, setTargetPlayer] = useState("");
    const [gameOver, setGameOver] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedFilters, setSelectedFilters] = useState<Record<string, string>>({});

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <Navigation />
            <PlayerSearch level="nba"
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                selectedFilters={selectedFilters}
                setSelectedFilters={setSelectedFilters}
            />
            <div>Hello World!</div>
        </main>
    );
}