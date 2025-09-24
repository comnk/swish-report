import { NBAPlayer } from "@/types/player";
import { NBAStatsResponse } from "@/types/general";
import { notFound } from "next/navigation";
import {
  Calendar,
  Ruler,
  Weight,
  TrendingUp,
  TrendingDown,
  Star,
  Target,
} from "lucide-react";
import Navigation from "@/components/ui/navigation";
import CommentsWrapper from "@/components/comments/comments-wrapper";
import GenerateHighlightButton from "@/components/player-pages/generate-highlight-reel";

type Params = Promise<{ id: string }>;

export default async function PlayerPage({ params }: { params: Params }) {
  const { id } = await params;

  // 🔹 Fetch player info
  const res = await fetch(`http://backend:8000/nba/players/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) notFound();
  const player: NBAPlayer = await res.json();

  // 🔹 Fetch highlight videos
  const videoRes = await fetch(`http://backend:8000/nba/players/${id}/videos`, {
    cache: "no-store",
  });
  const videos: string[] = videoRes.ok ? await videoRes.json() : [];

  // 🔹 Fetch NBA stats
  const statsRes = await fetch(`http://backend:8000/nba/players/${id}/stats`, {
    cache: "no-store",
  });
  const nbaStats: NBAStatsResponse = statsRes.ok
    ? await statsRes.json()
    : { season_stats: [] };

  const getGradeColor = (rating: number) => {
    if (rating >= 93) return "text-green-600 bg-green-50";
    if (rating >= 90) return "text-green-500 bg-green-50";
    if (rating >= 80) return "text-yellow-600 bg-yellow-50";
    if (rating >= 70) return "text-orange-600 bg-orange-50";
    return "text-red-600 bg-red-50";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Left: Avatar + Name + Teams/Draft */}
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6">
            <div className="flex flex-col sm:flex-row sm:items-start gap-4 sm:gap-6 w-full lg:w-auto">
              {/* Avatar */}
              <div className="flex-shrink-0 w-24 h-24 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {player.full_name
                  ? player.full_name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                  : "?"}
              </div>

              {/* Name + Teams */}
              <div className="flex-1 min-w-0">
                <h1 className="text-3xl font-bold text-gray-900 truncate">
                  {player.full_name}
                </h1>
                <div className="flex flex-wrap mt-2 gap-2">
                  {player.team_names?.length ? (
                    player.team_names.map((team, idx) => (
                      <span
                        key={idx}
                        className="bg-gray-200 text-gray-900 font-medium text-sm px-3 py-1 rounded-full"
                      >
                        {team}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-900 font-medium text-sm">
                      No Team
                    </span>
                  )}

                  {player.draft_year && (
                    <span className="flex items-center bg-gray-100 text-gray-900 font-medium text-sm px-3 py-1 rounded-full">
                      <Calendar className="w-4 h-4 mr-1" />
                      Draft {player.draft_year}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Rating + Stars */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
              <div
                className={`inline-block px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap ${getGradeColor(
                  player.overallRating
                )}`}
              >
                Overall Rating: {player.overallRating}
              </div>
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < player.stars
                        ? "text-yellow-400 fill-current"
                        : "text-gray-300"
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex justify-center py-8 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-5xl space-y-8">
          {/* Physical Attributes */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
              Physical Attributes
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Ruler className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {player.height}
                </div>
                <div className="text-sm text-gray-600">Height</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Weight className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {player.weight}
                </div>
                <div className="text-sm text-gray-600">Weight</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Target className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {player.position}
                </div>
                <div className="text-sm text-gray-600">Position</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Calendar className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {player.years_pro}
                </div>
                <div className="text-sm text-gray-600">Years in NBA</div>
              </div>
            </div>
          </div>

          {/* Highlight Reel Button */}
          <GenerateHighlightButton player={player} />

          {/* Highlight Videos */}
          {videos.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
                Highlight Videos
              </h2>
              <div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0">
                {videos.map((url, idx) => (
                  <div key={idx} className="flex-1 aspect-video">
                    <iframe
                      src={url.replace("watch?v=", "embed/")}
                      title={`Highlight Video ${idx + 1}`}
                      className="w-full h-full rounded-lg"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* NBA Season Stats Table */}
          {nbaStats.season_stats.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6 overflow-x-auto text-black">
              <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
                NBA Season Stats
              </h2>
              <table className="min-w-full divide-y divide-gray-200 text-sm text-center">
                <thead className="bg-gray-50">
                  <tr>
                    <th>Season</th>
                    <th>Team</th>
                    <th>GP</th>
                    <th>PPG</th>
                    <th>RPG</th>
                    <th>APG</th>
                    <th>SPG</th>
                    <th>BPG</th>
                    <th>TOPG</th>
                    <th>FPG</th>
                    <th>FG%</th>
                    <th>3P%</th>
                    <th>FT%</th>
                    <th>eFG%</th>
                    <th>TS%</th>
                  </tr>
                </thead>
                <tbody>
                  {nbaStats.season_stats.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td>{row.Season}</td>
                      <td>{row.Team}</td>
                      <td>{row.GP}</td>
                      <td>{row.PPG}</td>
                      <td>{row.RPG}</td>
                      <td>{row.APG}</td>
                      <td>{row.SPG}</td>
                      <td>{row.BPG}</td>
                      <td>{row.TOPG}</td>
                      <td>{row.FPG}</td>
                      <td>{row.FG !== undefined ? row.FG + "%" : "-"}</td>
                      <td>{row["3P"] !== undefined ? row["3P"] + "%" : "-"}</td>
                      <td>{row.FT !== undefined ? row.FT + "%" : "-"}</td>
                      <td>{row.eFG !== undefined ? row.eFG + "%" : "-"}</td>
                      <td>{row.TS !== undefined ? row.TS + "%" : "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-green-600 mr-2" /> Strengths
              </h3>
              <ul className="space-y-2">
                {player.strengths.map((s, i) => (
                  <li key={i} className="flex items-start">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-red-600 mr-2" />{" "}
                Weaknesses
              </h3>
              <ul className="space-y-2">
                {player.weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start">
                    <div className="w-2 h-2 bg-red-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* AI Scouting Report */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
              AI Scouting Report
            </h2>
            <div className="prose max-w-none">
              {player.aiAnalysis.split("\n").map((para, i) => (
                <p key={i} className="text-gray-700 leading-relaxed mb-4">
                  {para}
                </p>
              ))}
            </div>
          </div>

          {/* Draft Info */}
          {(player.draft_round || player.draft_pick || player.draft_year) && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6 text-center">
                Draft Info
              </h2>
              <div
                className={`grid gap-6 text-center ${
                  !player.draft_round && !player.draft_pick
                    ? "grid-cols-2"
                    : "grid-cols-3 sm:grid-cols-3"
                }`}
              >
                {player.draft_round || player.draft_pick ? (
                  <>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-900">
                        {player.draft_round ?? "Undrafted"}
                      </div>
                      <div className="text-gray-700">Draft Round</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-900">
                        {player.draft_pick ?? "Undrafted"}
                      </div>
                      <div className="text-gray-700">Draft Pick</div>
                    </div>
                  </>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-4 col-span-1">
                    <div className="text-2xl font-bold text-gray-900">
                      Undrafted
                    </div>
                    <div className="text-gray-700">Draft Status</div>
                  </div>
                )}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-gray-900">
                    {player.draft_year ?? "-"}
                  </div>
                  <div className="text-gray-700">Draft Year</div>
                </div>
              </div>
            </div>
          )}

          {/* Community Discussion */}
          <section className="bg-white shadow rounded-lg p-6 space-y-4">
            <h2 className="text-2xl font-semibold text-black">
              Community Discussion
            </h2>
            <CommentsWrapper
              parentId={Number(player.id)}
              contextType="nba-scouting"
            />
          </section>
        </div>
      </div>
    </div>
  );
}
