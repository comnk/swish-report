"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation"; // <-- import router
import Court from "@/components/lineup-builder-court";
import Navigation from "@/components/navigation";

export default function LineupBuilderForm() {
  const router = useRouter(); // <-- initialize router
  const [mode, setMode] = useState<"starting5" | "rotation">("starting5");
  const [lineup, setLineup] = useState<Record<string, string | null>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const modeParam = params.get("mode");
    setMode(modeParam === "rotation" ? "rotation" : "starting5");
  }, []);

  useEffect(() => {
    const initialLineup: Record<string, string | null> =
      mode === "starting5"
        ? { PG: null, SG: null, SF: null, PF: null, C: null }
        : {
            PG: null,
            SG: null,
            SF: null,
            PF: null,
            C: null,
            Bench1: null,
            Bench2: null,
            Bench3: null,
            Bench4: null,
            Bench5: null,
          };
    setLineup(initialLineup);
  }, [mode]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitStatus("idle");
    setErrorMessage(null);

    const token = localStorage.getItem("token");
    const user_email = localStorage.getItem("user_email");

    if (!token || !user_email) {
      setIsSubmitting(false);
      setSubmitStatus("error");
      setErrorMessage("You must be signed in to submit a lineup.");
      return;
    }

    try {
      const res = await fetch(
        "http://localhost:8000/games/lineup-builder/submit-lineup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ mode, lineup, user_email: user_email }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Submission failed");
      }

      const data = await res.json();
      console.log("✅ Submission success:", data);

      // Redirect to the new lineup page
      router.push(`/community/player-lineups/${data.lineup_id}`);
    } catch (err: unknown) {
      console.error(err);
      setSubmitStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (Object.keys(lineup).length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="flex flex-col items-center p-6 space-y-6 w-full">
        <h2 className="text-2xl font-bold text-black">
          {mode === "starting5"
            ? "Build Your Starting 5"
            : "Build Your Full Rotation"}
        </h2>

        <Court lineup={lineup} setLineup={setLineup} mode={mode} />

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold shadow-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
        >
          {isSubmitting && (
            <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white border-b-2 mr-2"></span>
          )}
          {isSubmitting ? "Submitting..." : "Submit Lineup for AI Analysis"}
        </button>

        {submitStatus === "error" && (
          <p className="text-red-600 font-medium">{errorMessage}</p>
        )}
      </div>
    </main>
  );
}
