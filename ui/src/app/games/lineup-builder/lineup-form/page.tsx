"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Court from "@/components/lineup-builder-court";
import Navigation from "@/components/navigation";

export default function LineupBuilderForm() {
  return (
    <Suspense fallback={<p>Loading lineup...</p>}>
      <LineupBuilderFormInner />
    </Suspense>
  );
}

function LineupBuilderFormInner() {
  const searchParams = useSearchParams();
  const modeParam = searchParams.get("mode");
  const mode: "starting5" | "rotation" =
    modeParam === "rotation" ? "rotation" : "starting5";

  const [lineup, setLineup] = useState<Record<string, string | null>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const initialLineup: Record<string, string | null> =
      mode === "starting5"
        ? { PG: null, SG: null, SF: null, PF: null, C: null }
        : {
            PG1: null,
            PG2: null,
            SG1: null,
            SG2: null,
            SF1: null,
            SF2: null,
            PF1: null,
            PF2: null,
            C1: null,
            C2: null,
          };
    setLineup(initialLineup);
  }, [mode]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitStatus("idle");
    setErrorMessage(null);

    console.log(lineup);

    // try {
    //   const res = await fetch(
    //     "http://localhost:8000/games/lineup-builder/submit-player",
    //     {
    //       method: "POST",
    //       headers: { "Content-Type": "application/json" },
    //       body: JSON.stringify({ mode, lineup }),
    //     }
    //   );

    //   if (!res.ok) {
    //     const errorData = await res.json();
    //     throw new Error(errorData.detail || "Submission failed");
    //   }

    //   const data = await res.json();
    //   console.log("✅ Submission success:", data);
    //   setSubmitStatus("success");

    //   // Optional: redirect to analysis page if backend returns an ID
    //   // if (data.analysis_id) window.location.href = `/games/lineup-builder/analysis/${data.analysis_id}`;
    // } catch (err: unknown) {
    //   console.error(err);
    //   setSubmitStatus("error");
    //   setErrorMessage(err instanceof Error ? err.message : "Unknown error");
    // } finally {
    //   setIsSubmitting(false);
    // }
  };

  if (Object.keys(lineup).length === 0) {
    return <p>Loading lineup...</p>; // optional loading
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
