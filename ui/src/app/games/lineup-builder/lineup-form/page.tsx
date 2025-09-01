"use client";

import { useState } from "react";
import Court from "@/components/lineup-builder-court";
import Navigation from "@/components/navigation";

export default function LineupBuilderGame() {
  const [lineup, setLineup] = useState<Record<string, string | null>>({
    PG: null,
    SG: null,
    SF: null,
    PF: null,
    C: null,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus("idle");
    setErrorMessage(null);

    try {
      const res = await fetch(
        "http://localhost:8000/games/lineup-builder/submit-player",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lineup }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Submission failed");
      }

      const data = await res.json();
      console.log("✅ Submission success:", data);

      // Example: redirect to analysis result page
      // if backend returns a player_uid or result id
      if (data.player_uid) {
        window.location.href = `/players/${data.player_uid}`;
      }

      setSubmitStatus("success");
    } catch (err: unknown) {
      console.error(err);
      setSubmitStatus("error");

      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("An unknown error occurred");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Navigation />
      <div className="flex flex-col items-center p-6 space-y-6">
        <Court lineup={lineup} setLineup={setLineup} />

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold shadow-md hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {isSubmitting ? "Submitting..." : "Submit Lineup for AI Analysis"}
        </button>

        {submitStatus === "error" && (
          <p className="text-red-600 font-medium">{errorMessage}</p>
        )}
        {submitStatus === "success" && (
          <p className="text-green-600 font-medium">
            Lineup submitted successfully!
          </p>
        )}
      </div>
    </main>
  );
}
