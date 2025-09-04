"use client";

import { ArrowRight, CheckCircle } from "lucide-react";
import Link from "next/link";

export default function CTASection() {
  const benefits = [
    "Discover 50,000+ verified player profiles",
    "Track real-time performance & trends",
    "AI-powered draft insights and projections",
    "Build and share custom lineups",
    "Engage with the Swish Report community",
    "Completely free to get started",
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-orange-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            {/* Left Column - Content */}
            <div className="p-8 lg:p-12">
              <div className="mb-6">
                <span className="inline-flex items-center px-4 py-2 rounded-full bg-orange-100 text-orange-800 text-sm font-medium">
                  Join the Movement
                </span>
              </div>

              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-6">
                Create Your Free Account Today
              </h2>

              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                Be part of the fastest-growing basketball scouting and analytics
                community. Whether you’re a fan, coach, or player, Swish Report
                gives you the tools to analyze, share, and compete.
              </p>

              {/* Benefits List */}
              <div className="space-y-4 mb-8">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-slate-700">{benefit}</span>
                  </div>
                ))}
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/signup"
                  className="bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-orange-700 transition-colors flex items-center justify-center group"
                >
                  Sign Up Now
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/community/hot-takes"
                  className="border-2 border-slate-300 text-slate-700 px-8 py-4 rounded-lg font-semibold text-lg hover:border-orange-600 hover:text-orange-600 transition-colors"
                >
                  Explore Community Hot Takes
                </Link>
              </div>

              <p className="text-sm text-slate-500 mt-4">
                100% free to join • No payment required • Cancel anytime
              </p>
            </div>

            {/* Right Column - Visual */}
            <div className="bg-gradient-to-br from-orange-600 to-orange-700 p-8 lg:p-12 flex items-center justify-center">
              <div className="text-center text-white">
                <div className="text-5xl font-bold mb-4">🏀</div>
                <div className="text-2xl font-semibold mb-2">
                  The Future of Scouting
                </div>
                <div className="text-orange-200 mb-8">
                  Trusted by hoopers, coaches, and fans everywhere
                </div>

                {/* Value Highlight Cards */}
                <div className="space-y-4">
                  <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                    <div className="text-sm text-orange-200">Community</div>
                    <div className="text-2xl font-bold">10,000+ Members</div>
                    <div className="text-sm text-orange-200">
                      Growing every day
                    </div>
                  </div>
                  <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 border border-white/30">
                    <div className="text-sm text-orange-200">
                      Players Tracked
                    </div>
                    <div className="text-2xl font-bold">50,000+</div>
                    <div className="text-sm text-orange-200">
                      Across HS, College & NBA
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
