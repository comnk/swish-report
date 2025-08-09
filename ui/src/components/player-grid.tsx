"use client";

import { HighSchoolPlayer, NBAPlayer } from "@/types/player";
import { Star } from "lucide-react";
import Link from "next/link";

interface PlayerGridProps {
    players: NBAPlayer[] | HighSchoolPlayer[];
    level: "high-school" | "college" | "nba";
}

function shuffleArray<T>(array: T[]): T[] {
    const arr = [...array]; // clone to avoid mutating original
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

export default function PlayerGrid({ players, level }: PlayerGridProps) {
    const getPlayerStats = (player: NBAPlayer, level: "college" | "nba") => {
        switch (level) {
            case "college":
            return [
                { label: "PPG", value: player.stats?.points ?? "-" },
                { label: "FG%", value: player.stats?.fieldGoalPercentage != null ? `${(player.stats.fieldGoalPercentage * 100).toFixed(1)}%` : "-" },
                { label: "3P%", value: player.stats?.threePointPercentage != null ? `${(player.stats.threePointPercentage * 100).toFixed(1)}%` : "-" },
            ];
            case "nba":
            return [
                { label: "PPG", value: player.stats?.points ?? "-" },
                { label: "PER", value: player.stats?.per ?? "-" },
                { label: "WS", value: player.stats?.winShares ?? "-" },
            ];
            default:
            return [];
        }
    };

    const getRatingColor = (rating: number) => {
        if (rating >= 93) return "text-green-600 bg-green-100";
        if (rating >= 90 && rating < 93) return "text-blue-600 bg-blue-100";
        if (rating >= 80 && rating < 90) return "text-orange-600 bg-orange-100";
        return "text-slate-600 bg-slate-100";
    };

    // Shuffle players before rendering
    const shuffledPlayers = shuffleArray(players);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {shuffledPlayers.map((player) => (
            <div
            key={player.id}
            className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 card-hover cursor-pointer"
            >
            {/* Player Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">
                    {player.name.split(' ').map(n => n[0]).join('')}
                    </span>
                </div>
                <div>
                    <h3 className="font-semibold text-slate-900 text-lg">{player.name}</h3>
                    <p className="text-slate-600 text-sm">
                    {player.position} | {player.height} | {player.school}
                    </p>
                    <div className="flex items-center mt-1">
                        {Array.from({ length: player.stars }).map((_, i) => (
                            <Star key={i} className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                        ))}
                    </div>
                </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getRatingColor(player.overallRating)}`}>
                {player.overallRating}
                </div>
            </div>

            {/* Strengths */}
            <div className="mb-4">
                <h4 className="text-sm font-medium text-slate-700 mb-2">Key Strengths</h4>
                <div className="flex flex-wrap gap-1">
                {player.strengths.slice(0, 3).map((strength: any, index: any) => (
                    <span
                    key={index}
                    className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full"
                    >
                    {strength}
                    </span>
                ))}
                </div>
            </div>

            {/* AI Analysis Preview */}
            <div className="bg-slate-50 rounded-lg p-3 mb-4">
                <div className="flex items-center mb-2">
                <Star className="h-4 w-4 text-orange-500 mr-1" />
                <span className="text-sm font-medium text-slate-700">AI Analysis</span>
                </div>
                <p className="text-sm text-slate-600 line-clamp-2">
                {player.aiAnalysis}
                </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
                <Link
                    href={`/high-school/${player.id}`}
                    className="flex-1 bg-orange-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-orange-700 transition-colors text-center block"
                >
                    View Report
                </Link>
            </div>
            </div>
        ))}
        </div>
    );
}
