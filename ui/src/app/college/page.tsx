import Navigation from "@/components/navigation";
import PlayerSearch from "@/components/player-search";
import PlayerGrid from "@/components/player-grid";
import { mockCollegePlayers } from "@/data/mock-players";

export default function CollegePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-green-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            College <span className="gradient-text">Basketball</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Comprehensive analysis of college basketball players with draft projections, 
            performance metrics, and professional potential assessments.
          </p>
        </div>

        {/* Search and Filters */}
        <PlayerSearch level="college" />

        {/* Conference Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-green-600">4,521</div>
            <div className="text-slate-600">D1 Players</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-blue-600">68</div>
            <div className="text-slate-600">Draft Prospects</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-orange-600">32</div>
            <div className="text-slate-600">Conferences</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="text-2xl font-bold text-purple-600">358</div>
            <div className="text-slate-600">D1 Schools</div>
          </div>
        </div>

        {/* Player Grid */}
        <PlayerGrid players={mockCollegePlayers} level="college" />
      </div>
    </main>
  );
}