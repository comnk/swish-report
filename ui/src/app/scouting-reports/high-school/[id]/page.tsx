import { HighSchoolPlayer } from "@/types/player";
import { notFound } from "next/navigation";
import {
    MapPin,
    Calendar,
    Ruler,
    Weight,
    TrendingUp,
    TrendingDown,
    Star,
    Target,
} from "lucide-react";
import Navigation from "@/components/navigation";

interface PlayerPageProps {
    params: { id: string };
}

export default async function PlayerPage({ params }: PlayerPageProps) {
    const { id } = await params;

    // Fetch player info
    const res = await fetch(`http://localhost:8000/high-school/prospects/${id}`, {
        cache: "no-store",
    });

    if (!res.ok) {
        notFound();
    }

    const player: HighSchoolPlayer = await res.json();

    // Fetch videos
    const videoRes = await fetch(
        `http://localhost:8000/high-school/prospects/${id}/videos`,
        {
        cache: "no-store",
        }
    );

    let videos: string[] = [];
    if (videoRes.ok) {
        videos = await videoRes.json(); // assuming it's an array of YouTube URLs
    }

    const getGradeColor = (rating: number) => {
        if (rating >= 93) return "text-green-600 bg-green-50"; // A+
        if (rating >= 90) return "text-green-500 bg-green-50"; // A-
        if (rating >= 80) return "text-yellow-600 bg-yellow-50"; // B
        if (rating >= 70) return "text-orange-600 bg-orange-50"; // C
        return "text-red-600 bg-red-50"; // below 70
    };

    return (
        <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b">
            <Navigation />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                <div className="flex items-center space-x-6">
                <div className="w-24 h-24 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                    {player?.full_name
                    ? player.full_name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                    : "?"}
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                    {player.full_name}
                    </h1>
                    <div className="flex items-center space-x-4 mt-2 text-gray-600">
                    <span className="flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        {player.school}
                    </span>
                    <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        Class of {player.class}
                    </span>
                    </div>
                </div>
                </div>

                <div className="mt-4 lg:mt-0 flex items-center space-x-4">
                <div
                    className={`px-4 py-2 rounded-full text-sm font-semibold ${getGradeColor(
                    player.overallRating
                    )}`}
                >
                    Overall Grade: {player.overallRating}
                </div>
                <div className="flex items-center">
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
                    {player.class}
                    </div>
                    <div className="text-sm text-gray-600">Class</div>
                </div>
                </div>
            </div>

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
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        ></iframe>
                    </div>
                    ))}
                </div>
                </div>
            )}

            {/* AI Scouting Report */}
            <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
                AI Scouting Report
                </h2>
                <div className="prose max-w-none">
                {player.aiAnalysis.split("\n").map((para, i) => (
                    <p
                    key={i}
                    className="text-gray-700 leading-relaxed mb-4"
                    >
                    {para}
                    </p>
                ))}
                </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                    Strengths
                </h3>
                <ul className="space-y-2">
                    {player.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start">
                        <div className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">{strength}</span>
                    </li>
                    ))}
                </ul>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5 text-red-600 mr-2" />
                    Weaknesses
                </h3>
                <ul className="space-y-2">
                    {player.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start">
                        <div className="w-2 h-2 bg-red-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                        <span className="text-gray-700">{weakness}</span>
                    </li>
                    ))}
                </ul>
                </div>
            </div>
            </div>
        </div>
        </div>
    );
}
