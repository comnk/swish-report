import Navigation from "@/components/navigation";
import PlayerGrid from "@/components/player-grid";
import PlayerSearch from "@/components/player-search";
import { mockNBAPlayers } from "@/data/mock-players";

export default function NBAPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            NBA <span className="gradient-text">Analysis</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Advanced analytics and career evaluations for current NBA players, 
            including performance trends, trade value, and future projections.
          </p>
        </div>

        {/* Search and Filters */}
        <PlayerSearch level="nba" />

        {/* League Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-purple-600">450+</div>
            <div className="text-slate-600">Active Players</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-red-600">30</div>
            <div className="text-slate-600">NBA Teams</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-orange-600">82</div>
            <div className="text-slate-600">Games/Season</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-green-600">$4.2B</div>
            <div className="text-slate-600">Total Salaries</div>
          </div>
        </div>

        {/* Player Grid */}
        <PlayerGrid players={mockNBAPlayers} level="nba" />
      </div>
    </main>
  );
}