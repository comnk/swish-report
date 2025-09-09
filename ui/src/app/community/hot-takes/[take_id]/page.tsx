"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Navigation from "@/components/navigation";

type HotTake = {
  take_id: number;
  content: string;
  truthfulness_score: number | null;
  ai_insight: string | null;
  username: string;
  email: string;
  created_at: string;
};

export default function HotTakePage() {
  const pathname = usePathname(); // e.g., /community/hot-takes/123
  const take_id = pathname.split("/").pop(); // get "123"

  const [hotTake, setHotTake] = useState<HotTake | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!take_id) return;

    const fetchHotTake = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/community/hot-takes/${take_id}`
        );
        if (!res.ok) throw new Error("Failed to fetch hot take");
        const data: HotTake = await res.json();
        setHotTake(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchHotTake();
  }, [take_id]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="max-w-2xl mx-auto p-6">
        {loading && <p>Loading hot take...</p>}
        {error && <p className="text-red-600">{error}</p>}

        {hotTake && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-bold text-black">
              {hotTake.username}&apos;s Hot Take
            </h2>
            <p className="text-gray-800">{hotTake.content}</p>

            {hotTake.truthfulness_score !== null &&
              hotTake.truthfulness_score !== undefined && (
                <div className="p-4 bg-gray-50 rounded text-black">
                  <p>
                    <strong>AI Truthfulness Score:</strong>{" "}
                    {Number(hotTake.truthfulness_score).toFixed(1)}%
                  </p>
                  <p>
                    <strong>AI Insight:</strong> {hotTake.ai_insight}
                  </p>
                </div>
              )}

            {/* Placeholder for discussion threads */}
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Community Discussion
              </h3>
              <p className="text-gray-500">
                Discussion threads will appear here.
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
