"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navigation from "@/components/navigation";

type HotTake = {
  take_id: number;
  content: string;
  user_id: number;
  username?: string;
  created_at: string;
};

export default function UserHotTakes() {
  const [hotTakes, setHotTakes] = useState<HotTake[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHotTakes = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/takes`);
        if (!res.ok) throw new Error("Failed to fetch hot takes");
        const data = await res.json();
        setHotTakes(data);
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

        {/* Loading / Error States */}
        {loading && <p className="text-gray-600">Loading hot takes...</p>}
        {error && hotTakes.length > 0 && (
          <p className="text-red-600">Error: {error}</p>
        )}

        {/* Hot Takes List */}
        <div className="space-y-4">
          {hotTakes.map((take) => (
            <div
              key={take.take_id}
              className="bg-white shadow-sm rounded-lg p-4 border border-gray-200"
            >
              <p className="text-gray-900">{take.content}</p>
              <div className="mt-2 text-sm text-gray-500 flex justify-between">
                <span>
                  {take.username
                    ? `@${take.username}`
                    : `User #${take.user_id}`}
                </span>
                <span>{new Date(take.created_at).toLocaleString()}</span>
              </div>
            </div>
          ))}

          {!loading && hotTakes.length === 0 && (
            <p className="text-gray-600">No hot takes yet. Be the first!</p>
          )}
        </div>
      </div>
    </main>
  );
}
