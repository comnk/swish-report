"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navigation from "@/components/navigation";

type HotTake = {
  take_id: number;
  content: string;
  username: string;
  created_at: string;
  truthfulness_score?: number | null;
  ai_insight?: string | null;
};

export default function UserHotTakes() {
  const [hotTakes, setHotTakes] = useState<HotTake[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHotTakes = async () => {
      try {
        const res = await fetch(`http://localhost:8000/community/hot-takes`);
        if (!res.ok) throw new Error("Failed to fetch hot takes");

        const data = await res.json();
        // data.hot_takes contains the array from backend
        setHotTakes(data.hot_takes || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchHotTakes();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Community Hot Takes
          </h1>
          <Link
            href="/community/hot-takes/form"
            className="bg-orange-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-orange-700 transition-colors"
          >
            Submit a Hot Take
          </Link>
        </div>

        {/* Loading / Error */}
        {loading && <p className="text-gray-600">Loading hot takes...</p>}
        {error && hotTakes.length === 0 && (
          <p className="text-red-600">Error: {error}</p>
        )}

        {/* Hot Takes List */}
        <div className="space-y-4">
          {hotTakes.map((take) => (
            <Link
              key={take.take_id}
              href={`/community/hot-takes/${take.take_id}`}
              className="block bg-white shadow-sm rounded-lg p-4 border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <p className="text-gray-900">{take.content}</p>

              {take.truthfulness_score !== null && take.ai_insight && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm text-gray-700 border border-gray-200">
                  <p>
                    <strong>AI Truthfulness:</strong>{" "}
                    {take.truthfulness_score!.toFixed(1)}%
                  </p>
                  <p>
                    <strong>AI Insight:</strong> {take.ai_insight}
                  </p>
                </div>
              )}

              <div className="mt-2 text-sm text-gray-500 flex justify-between">
                <span>@{take.username}</span>
                <span>{new Date(take.created_at).toLocaleString()}</span>
              </div>
            </Link>
          ))}

          {!loading && hotTakes.length === 0 && (
            <p className="text-gray-600">No hot takes yet. Be the first!</p>
          )}
        </div>
      </div>
    </main>
  );
}
