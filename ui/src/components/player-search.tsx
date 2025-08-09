"use client";

import { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";

interface PlayerSearchProps {
    level: "high-school" | "college" | "nba";
    searchTerm: string;
    setSearchTerm: (term: string) => void;
    selectedFilters: Record<string, string>;
    setSelectedFilters: (filters: Record<string, string>) => void;
}

type HighSchoolFilters = {
    position: string[];
    class: string[];
    stars: string[];
    state: string[];
};

type CollegeFilters = {
    position: string[];
    conferences: string[];
    years: string[];
    draftStatus: string[];
};

type NBAFilters = {
    position: string[];
    teams: string[];
    experience: string[];
    salary: string[];
};

type Filters = HighSchoolFilters | CollegeFilters | NBAFilters;

export default function PlayerSearch({
    level,
    searchTerm,
    setSearchTerm,
    selectedFilters,
    setSelectedFilters
}: PlayerSearchProps) {
    const [showFilters, setShowFilters] = useState(false);

    const getFilters = (): Filters => {
        switch (level) {
            case "high-school":
                return {
                    position: ["PG", "SG", "SF", "PF", "C"],
                    class: ["2025", "2026", "2027"],
                    stars: ["5-Star", "4-Star", "3-Star", "2-Star"],
                    state: ["CA", "TX", "FL", "NY", "GA", "NC", "IL", "OH"],
                };
            case "college":
                return {
                    position: ["PG", "SG", "SF", "PF", "C"],
                    conferences: ["ACC", "Big Ten", "Big 12", "SEC", "Pac-12", "Big East"],
                    years: ["Freshman", "Sophomore", "Junior", "Senior"],
                    draftStatus: ["Lottery", "First Round", "Second Round", "Undrafted"],
                };
            case "nba":
                return {
                    position: ["PG", "SG", "SF", "PF", "C"],
                    teams: ["LAL", "GSW", "BOS", "MIA", "NYK", "CHI", "DAL", "PHX"],
                    experience: ["Rookie", "2-5 Years", "6-10 Years", "Veteran"],
                    salary: ["Under $5M", "$5M-$15M", "$15M-$30M", "Over $30M"],
                };
        }
    };

    const filters = getFilters();

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8">
            {/* Search Bar */}
            <div className="flex flex-col lg:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-5 w-5" />
                    <input
                        type="text"
                        placeholder={`Search ${level === "high-school" ? "high school" : level} players...`}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
                    />
                </div>
                <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="flex items-center px-6 py-3 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors text-slate-700"
                >
                    <SlidersHorizontal className="h-5 w-5 mr-2 text-slate-500" />
                    Filters
                </button>
            </div>

            {/* Filters */}
            {showFilters && (
                <div className="border-t border-slate-200 pt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {Object.entries(filters).map(([key, values]) => (
                            <div key={key}>
                                <label className="block text-sm font-medium text-slate-700 mb-2 capitalize">
                                    {key === "draftStatus" ? "Draft Status" : key}
                                </label>
                                <select
                                    value={selectedFilters[key] || ""}
                                    onChange={(e) =>
                                        setSelectedFilters({
                                            ...selectedFilters,
                                            [key]: e.target.value
                                        })
                                    }
                                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
                                >
                                    <option value="" className="text-slate-500">
                                        All {key}
                                    </option>
                                    {values.map((value) => (
                                        <option key={value} value={value} className="text-slate-800">
                                            {value}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}