"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, BarChart3 } from "lucide-react";

export default function Navigation() {
    const [isOpen, setIsOpen] = useState(false);

    const navItems = [
        { name: "High School", href: "/high-school" },
        { name: "College", href: "/college" },
        { name: "NBA", href: "/nba" },
        
    ];

    return (
        <nav className="bg-white/95 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2 group">
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-2 rounded-lg group-hover:scale-105 transition-transform">
                <BarChart3 className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold text-slate-900">
                Swish <span className="gradient-text">Report</span>
                </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
                {navItems.map((item) => (
                <Link
                    key={item.name}
                    href={item.href}
                    className="text-slate-700 hover:text-orange-600 font-medium transition-colors relative group"
                >
                    {item.name}
                    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-orange-600 transition-all group-hover:w-full"></span>
                </Link>
                ))}
                <Link href="/submit-player" className="text-black hover:text-orange-300 transition-colors">
        +            Submit Player
        +       </Link>
                <button className="bg-orange-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-orange-700 transition-colors">
                Get Started
                </button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
                <button
                onClick={() => setIsOpen(!isOpen)}
                className="text-slate-700 hover:text-orange-600 transition-colors"
                >
                {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
            </div>
            </div>

            {/* Mobile Navigation */}
            {isOpen && (
            <div className="md:hidden py-4 border-t border-slate-200">
                <div className="flex flex-col space-y-4">
                {navItems.map((item) => (
                    <Link
                    key={item.name}
                    href={item.href}
                    className="text-slate-700 hover:text-orange-600 font-medium transition-colors px-2 py-1"
                    onClick={() => setIsOpen(false)}
                    >
                    {item.name}
                    </Link>
                ))}
                <button className="bg-orange-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-orange-700 transition-colors w-fit">
                    Get Started
                </button>
                </div>
            </div>
            )}
        </div>
        </nav>
    );
    }