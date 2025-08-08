"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/navigation";
import PlayerSearch from "@/components/player-search";
import PlayerGrid from "@/components/player-grid";
import { HighSchoolPlayer } from "@/types/player";

export default function HighSchoolPage() {
  const [players, setPlayers] = useState<HighSchoolPlayer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const res = await fetch("http://localhost:8000/prospects/highschool"); // Adjust API URL if needed
        if (!res.ok) {
          throw new Error(`Error ${res.status}`);
        }
        const data = await res.json();

        console.log(data[0]);

        // Map backend data → HighSchoolPlayer structure
        const mapped: HighSchoolPlayer[] = data.map((p: any) => ({
          id: String(p.player_uid),
          name: p.full_name,
          position: p.position,
          school: p.school_name,
          class: p.class_year?.toString() ?? "",
          height: p.height,

          // Hardcoded for now as your backend does not provide these
          overallRating: 85,
          strengths: ["Scoring", "Athleticism", "Court Vision"],
          weaknesses: ["Defense", "Consistency"],
          aiAnalysis:
            "A highly talented high school prospect with excellent scoring ability and strong athletic traits.",
          draftProjection: "Projected late first-round pick",

          // Provide empty strings for any other required fields to avoid undefined
          weight: "",
        }));

        setPlayers(mapped);
      } catch (error) {
        console.error("Failed to fetch high school prospects:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            High School <span className="gradient-text">Prospects</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Discover the next generation of basketball talent with comprehensive
            AI-powered evaluations of high school players across the nation.
          </p>
        </div>

        {/* Search and Filters */}
        <PlayerSearch level="high-school" />

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-blue-600">2,847</div>
            <div className="text-slate-600">Active Prospects</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-green-600">156</div>
            <div className="text-slate-600">5-Star Recruits</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-orange-600">89%</div>
            <div className="text-slate-600">College Bound</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-purple-600">24</div>
            <div className="text-slate-600">NBA Prospects</div>
          </div>
        </div>

        {/* Player Grid */}
        {loading ? (
          <p className="text-center">Loading...</p>
        ) : (
          <PlayerGrid players={players} level="high-school" />
        )}
      </div>
    </main>
  );
}
