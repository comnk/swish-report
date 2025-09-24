import Link from "next/link";
import Navigation from "@/components/ui/navigation";

export default function LineupBuilderLandingPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navigation />

      <main className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-4">
          Build Your Dream NBA Lineup
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mb-8">
          Choose whether you want to build a <b>starting 5</b> or a{" "}
          <b>full rotation</b> and get instant AI-powered analysis.
        </p>

        <div className="flex space-x-4">
          <Link
            href="/games/lineup-builder/lineup-form?mode=starting5"
            className="px-6 py-3 rounded-2xl bg-indigo-600 text-white font-semibold text-lg shadow-lg hover:bg-indigo-700 transition"
          >
            Build Starting 5
          </Link>

          <Link
            href="/games/lineup-builder/lineup-form?mode=rotation"
            className="px-6 py-3 rounded-2xl bg-green-600 text-white font-semibold text-lg shadow-lg hover:bg-green-700 transition"
          >
            Build Rotation
          </Link>
        </div>
      </main>

      <footer className="py-6 text-center text-gray-500 text-sm">
        © {new Date().getFullYear()} Lineup Builder. All rights reserved.
      </footer>
    </div>
  );
}
