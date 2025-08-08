"use client";

import { Player } from "@/types/player";
import { Star, TrendingUp, Award } from "lucide-react";

interface PlayerGridProps {
    players: Player[];
    level: "high-school" | "college" | "nba";
}

export default function PlayerGrid({ players, level }: PlayerGridProps) {
    const getPlayerStats = (player: Player) => {
        switch (level) {
        case "high-school":
            return [
            { label: "PPG", value: player.stats.points },
            { label: "RPG", value: player.stats.rebounds },
            { label: "APG", value: player.stats.assists }
            ];
        case "college":
            return [
            { label: "PPG", value: player.stats.points },
            { label: "FG%", value: `${player.stats.fieldGoalPercentage}%` },
            { label: "3P%", value: `${player.stats.threePointPercentage}%` }
            ];
        case "nba":
            return [
            { label: "PPG", value: player.stats.points },
            { label: "PER", value: player.stats.per },
            { label: "WS", value: player.stats.winShares }
            ];
        }
    };

    const getRatingColor = (rating: number) => {
        if (rating >= 90) return "text-green-600 bg-green-100";
        if (rating >= 80) return "text-blue-600 bg-blue-100";
        if (rating >= 70) return "text-orange-600 bg-orange-100";
        return "text-slate-600 bg-slate-100";
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {players.map((player) => (
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
                </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getRatingColor(player.overallRating)}`}>
                {player.overallRating}
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-4">
                {getPlayerStats(player).map((stat, index) => (
                <div key={index} className="text-center">
                    <div className="text-lg font-bold text-slate-900">{stat.value}</div>
                    <div className="text-xs text-slate-600">{stat.label}</div>
                </div>
                ))}
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
                <button className="flex-1 bg-orange-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-orange-700 transition-colors">
                View Report
                </button>
                <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                <TrendingUp className="h-4 w-4" />
                </button>
            </div>
            </div>
        ))}
        </div>
    );
}