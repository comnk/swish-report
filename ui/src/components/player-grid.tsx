"use client";

import { HighSchoolPlayer, NBAPlayer } from "@/types/player";
import { Star } from "lucide-react";
import Link from "next/link";

interface PlayerGridProps {
    players: HighSchoolPlayer[] | NBAPlayer[];
    level: "high-school" | "college" | "nba";
}

function shuffleArray<T>(array: T[]): T[] {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

export default function PlayerGrid({ players, level }: PlayerGridProps) {
    const getRatingColor = (rating: number) => {
        if (rating >= 93) return "text-green-600 bg-green-100";
        if (rating >= 90) return "text-blue-600 bg-blue-100";
        if (rating >= 80) return "text-orange-600 bg-orange-100";
        return "text-slate-600 bg-slate-100";
    };

    const shuffledPlayers = shuffleArray<typeof players[0]>(players);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {shuffledPlayers.map((player) => {
            const displayName =
            level === "high-school" ? (player as HighSchoolPlayer).full_name : (player as NBAPlayer).name;

            const initials = (displayName ?? "")
            .split(" ")
            .map((n) => n[0])
            .join("");

            const stars = player.stars ?? 0;
            const strengths = player.strengths ?? [];

            return (
            <div
                key={player.id}
                className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 card-hover cursor-pointer"
            >
                {/* Player Header */}
                <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">{initials}</span>
                    </div>
                    <div>
                    <h3 className="font-semibold text-slate-900 text-lg">{displayName}</h3>
                    <p className="text-slate-600 text-sm">
                        {player.position} | {player.height} |{" "}
                        {level === "high-school"
                        ? (player as HighSchoolPlayer).school ?? "-"
                        : (player as NBAPlayer).team_names?.slice(-1)[0] ?? "-"}
                    </p>
                    <div className="flex items-center mt-1">
                        {Array.from({ length: stars }).map((_, i) => (
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
                    {strengths.slice(0, 3).map((strength: string, index: number) => (
                    <span
                        key={`${player.id}-strength-${index}`}
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
                <p className="text-sm text-slate-600 line-clamp-2">{player.aiAnalysis}</p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                <Link
                    href={
                    level === "high-school"
                        ? `/scouting-reports/high-school/${player.id}`
                        : level === "nba"
                        ? `/nba/${player.id}`
                        : "#"
                    }
                    className="flex-1 bg-orange-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-orange-700 transition-colors text-center block"
                >
                    View Report
                </Link>
                </div>
            </div>
            );
        })}
        </div>
    );
}
