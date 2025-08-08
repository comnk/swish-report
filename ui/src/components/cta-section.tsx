"use client";

import { ArrowRight, CheckCircle } from "lucide-react";

export default function CTASection() {
    const benefits = [
        "Access to 50,000+ player profiles",
        "Real-time performance analytics",
        "AI-powered draft projections",
        "Advanced team building tools",
        "Mobile app included",
        "24/7 customer support"
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
                    Limited Time Offer
                    </span>
                </div>
                
                <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-6">
                    Start Your Free Trial Today
                </h2>
                
                <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                    Join the revolution in basketball scouting. Get instant access to our 
                    comprehensive AI-powered platform and discover why top teams choose Swish Report.
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
                    <button className="bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-orange-700 transition-colors flex items-center justify-center group">
                    Start Free Trial
                    <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                    <button className="border-2 border-slate-300 text-slate-700 px-8 py-4 rounded-lg font-semibold text-lg hover:border-orange-600 hover:text-orange-600 transition-colors">
                    Schedule Demo
                    </button>
                </div>

                <p className="text-sm text-slate-500 mt-4">
                    No credit card required • 14-day free trial • Cancel anytime
                </p>
                </div>

                {/* Right Column - Visual */}
                <div className="bg-gradient-to-br from-orange-600 to-orange-700 p-8 lg:p-12 flex items-center justify-center">
                <div className="text-center text-white">
                    <div className="text-6xl font-bold mb-4">14</div>
                    <div className="text-2xl font-semibold mb-2">Days Free</div>
                    <div className="text-orange-200 mb-8">
                    Full access to all features
                    </div>
                    
                    {/* Pricing Cards */}
                    <div className="space-y-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                        <div className="text-sm text-orange-200">After trial</div>
                        <div className="text-2xl font-bold">$49/month</div>
                        <div className="text-sm text-orange-200">Professional Plan</div>
                    </div>
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 border border-white/30">
                        <div className="text-sm text-orange-200">Team Plan</div>
                        <div className="text-2xl font-bold">$199/month</div>
                        <div className="text-sm text-orange-200">Up to 10 users</div>
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