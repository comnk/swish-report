"use client";

import { useEffect, useState } from "react";

export default function StatsSection() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
        ([entry]) => {
            if (entry.isIntersecting) {
            setIsVisible(true);
            }
        },
        { threshold: 0.1 }
        );

        const element = document.getElementById('stats-section');
        if (element) {
        observer.observe(element);
        }

        return () => observer.disconnect();
    }, []);

    const stats = [
        {
        number: "50,000+",
        label: "Players Analyzed",
        description: "Comprehensive scouting reports across all levels"
        },
        {
        number: "95%",
        label: "Accuracy Rate",
        description: "AI predictions validated by professional outcomes"
        },
        {
        number: "500+",
        label: "Teams Served",
        description: "High schools, colleges, and professional organizations"
        },
        {
        number: "24/7",
        label: "Real-time Updates",
        description: "Continuous monitoring and analysis of player performance"
        }
    ];

    return (
        <section id="stats-section" className="py-20 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Section Header */}
            <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Trusted by Basketball Professionals
            </h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
                Our AI-powered platform delivers insights that help teams make better decisions, 
                from recruitment to roster management.
            </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
                <div
                key={stat.label}
                className={`text-center ${isVisible ? 'animate-count-up' : 'opacity-0'}`}
                style={{ animationDelay: `${index * 0.2}s` }}
                >
                <div className="text-4xl md:text-5xl font-bold text-orange-400 mb-2">
                    {stat.number}
                </div>
                <div className="text-xl font-semibold text-white mb-2">
                    {stat.label}
                </div>
                <div className="text-slate-400 leading-relaxed">
                    {stat.description}
                </div>
                </div>
            ))}
            </div>

            {/* Testimonial */}
            <div className="mt-20 text-center">
            <div className="bg-slate-800 rounded-2xl p-8 max-w-4xl mx-auto border border-slate-700">
                <div className="text-2xl text-slate-300 mb-6 italic">
                "Swish Report has completely transformed how we evaluate talent. The AI insights 
                have helped us identify hidden gems and make more informed recruiting decisions."
                </div>
                <div className="flex items-center justify-center space-x-4">
                <div className="w-12 h-12 bg-orange-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">MJ</span>
                </div>
                <div className="text-left">
                    <div className="font-semibold text-white">Mike Johnson</div>
                    <div className="text-slate-400">Head Coach, State University</div>
                </div>
                </div>
            </div>
            </div>
        </div>
        </section>
    );
}