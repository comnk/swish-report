import Navigation from "@/components/navigation";
import PlayerSearch from "@/components/player-search";
import PlayerGrid from "@/components/player-grid";
import { mockHighSchoolPlayers } from "@/data/mock-players";

export default function HighSchoolPage() {
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
        <PlayerGrid players={mockHighSchoolPlayers} level="high-school" />
      </div>
    </main>
  );
}