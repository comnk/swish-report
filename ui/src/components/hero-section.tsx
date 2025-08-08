"use client";

import { ArrowRight, Zap, Target, TrendingUp } from "lucide-react";
import Link from "next/link";

export default function HeroSection() {
    return (
        <section className="relative py-20 lg:py-32 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 court-pattern"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-orange-100 text-orange-800 text-sm font-medium mb-8">
                <Zap className="h-4 w-4 mr-2" />
                AI-Powered Basketball Analytics
            </div>

            {/* Main Heading */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 leading-tight">
                The Future of
                <br />
                <span className="gradient-text">Basketball Scouting</span>
            </h1>

            {/* Subheading */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                Get comprehensive AI-powered scouting reports and analysis for high school, 
                college, and NBA players. Make smarter decisions with data-driven insights.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
                <Link
                href="/high-school"
                className="bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-orange-700 transition-colors flex items-center group"
                >
                Start Scouting
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="border-2 border-slate-300 text-slate-700 px-8 py-4 rounded-lg font-semibold text-lg hover:border-orange-600 hover:text-orange-600 transition-colors">
                Watch Demo
                </button>
            </div>

            {/* Feature Pills */}
            <div className="flex flex-wrap justify-center gap-4 mb-16">
                <div className="flex items-center bg-white px-6 py-3 rounded-full shadow-sm border border-slate-200">
                <Target className="h-5 w-5 text-orange-600 mr-2" />
                <span className="text-slate-700 font-medium">High School Prospects</span>
                </div>
                <div className="flex items-center bg-white px-6 py-3 rounded-full shadow-sm border border-slate-200">
                <TrendingUp className="h-5 w-5 text-orange-600 mr-2" />
                <span className="text-slate-700 font-medium">Draft Projections</span>
                </div>
                <div className="flex items-center bg-white px-6 py-3 rounded-full shadow-sm border border-slate-200">
                <Zap className="h-5 w-5 text-orange-600 mr-2" />
                <span className="text-slate-700 font-medium">NBA Career Analysis</span>
                </div>
            </div>

            {/* Hero Image Placeholder */}
            <div className="relative max-w-5xl mx-auto">
                <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border border-slate-700">
                <div className="bg-slate-700 rounded-lg p-6 mb-4">
                    <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-orange-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-lg">JS</span>
                        </div>
                        <div>
                        <h3 className="text-white font-semibold text-lg">Jayson Smith</h3>
                        <p className="text-slate-400">Senior | Point Guard | 6'2"</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-bold text-orange-400">92</div>
                        <div className="text-slate-400 text-sm">Overall Rating</div>
                    </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <div className="text-xl font-bold text-white">18.5</div>
                        <div className="text-slate-400 text-sm">PPG</div>
                    </div>
                    <div>
                        <div className="text-xl font-bold text-white">7.2</div>
                        <div className="text-slate-400 text-sm">APG</div>
                    </div>
                    <div>
                        <div className="text-xl font-bold text-white">45%</div>
                        <div className="text-slate-400 text-sm">3PT%</div>
                    </div>
                    </div>
                </div>
                <div className="text-slate-300 text-sm leading-relaxed">
                    <strong className="text-orange-400">AI Analysis:</strong> Elite court vision and basketball IQ. 
                    Exceptional three-point shooter with NBA-ready range. Projects as a lottery pick with 
                    potential for immediate impact at the next level...
                </div>
                </div>
            </div>
            </div>
        </div>
        </section>
    );
}