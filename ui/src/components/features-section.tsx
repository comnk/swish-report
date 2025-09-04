"use client";

import {
  GraduationCap,
  Trophy,
  Star,
  TrendingUp,
  Users,
  BarChart3,
} from "lucide-react";
import Link from "next/link";

export default function FeaturesSection() {
  const features = [
    {
      icon: GraduationCap,
      title: "High School Scouting",
      description:
        "Comprehensive evaluations of high school prospects with college recruitment insights and development projections.",
      href: "/scouting-reports/high-school",
      color: "bg-blue-500",
    },
    {
      icon: Trophy,
      title: "College Analysis",
      description:
        "In-depth analysis of college players including performance metrics, draft stock, and professional potential.",
      href: "/scouting-reports/college",
      color: "bg-green-500",
    },
    {
      icon: Star,
      title: "NBA Evaluation",
      description:
        "Advanced NBA player analysis covering current performance, career trajectories, and trade value assessments.",
      href: "/scouting-reports/nba",
      color: "bg-purple-500",
    },
    {
      icon: TrendingUp,
      title: "Draft Projections",
      description:
        "Real-time NBA draft rankings with AI-powered projections and team fit analysis for upcoming prospects.",
      href: "/draft",
      color: "bg-orange-500",
    },
    {
      icon: Users,
      title: "Team Building",
      description:
        "Strategic insights for roster construction, player combinations, and team chemistry optimization.",
      href: "/games/lineup-builder/landing-page",
      color: "bg-red-500",
    },
    {
      icon: BarChart3,
      title: "Advanced Metrics",
      description:
        "Cutting-edge analytics including efficiency ratings, impact metrics, and predictive modeling.",
      href: "/analytics",
      color: "bg-indigo-500",
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Complete Basketball Intelligence
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            From high school gyms to NBA arenas, our AI-powered platform
            provides comprehensive scouting and analysis across all levels of
            basketball.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Link
              key={feature.title}
              href={feature.href}
              className="group card-hover bg-slate-50 rounded-2xl p-8 border border-slate-200 hover:border-orange-200 hover:bg-orange-50/50"
            >
              <div
                className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}
              >
                <feature.icon className="h-6 w-6 text-white" />
              </div>

              <h3 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-orange-600 transition-colors">
                {feature.title}
              </h3>

              <p className="text-slate-600 leading-relaxed mb-4">
                {feature.description}
              </p>

              <div className="flex items-center text-orange-600 font-medium group-hover:translate-x-2 transition-transform">
                Explore
                <svg
                  className="ml-2 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <div className="bg-gradient-to-r from-orange-600 to-orange-700 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to revolutionize your scouting?
            </h3>
            <p className="text-orange-100 mb-6 max-w-2xl mx-auto">
              Join thousands of coaches, scouts, and analysts who trust Swish
              Report for their basketball intelligence needs.
            </p>
            <button className="bg-white text-orange-600 px-8 py-3 rounded-lg font-semibold hover:bg-orange-50 transition-colors">
              Start Free Trial
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
