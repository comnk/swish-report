"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, BarChart3, ChevronDown } from "lucide-react";

export default function Navigation() {
    const [isOpen, setIsOpen] = useState(false);
    const [openDropdown, setOpenDropdown] = useState<string | null>(null); // Track which dropdown is open

    const scoutingItems = [
        { name: "High School", href: "/scouting-reports/high-school" },
        { name: "College", href: "/scouting-reports/college" },
        { name: "NBA", href: "/scouting-reports/nba" },
    ];

    const gameItems = [
        { name: "Lineup Builder", href: "/games/lineup-builder" },
        { name: "Poeltl", href: "/games/poeltl" },
    ];

    const submitItems = [
        { name: "High School", href: "/submit-player/high-school" },
        { name: "College", href: "/submit-player/college" },
        { name: "NBA", href: "/submit-player/nba" },
    ];

    const toggleDropdown = (name: string) => {
        setOpenDropdown(openDropdown === name ? null : name);
    };

    const closeDropdowns = () => setOpenDropdown(null);

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
                {/** Dropdown Template */}
                {[
                { name: "Scouting Reports", items: scoutingItems },
                { name: "Games", items: gameItems },
                { name: "Submit Missing Player", items: submitItems },
                ].map((dropdown) => (
                <div key={dropdown.name} className="relative group">
                    <button
                    onClick={() => toggleDropdown(dropdown.name)}
                    className="flex items-center text-slate-700 hover:text-orange-600 font-medium transition-colors"
                    >
                    {dropdown.name} <ChevronDown className="h-4 w-4 ml-1" />
                    </button>

                    {openDropdown === dropdown.name && (
                    <div className={`absolute left-0 mt-2 w-48 bg-white shadow-lg rounded-md border border-slate-200 py-2 z-50`}>
                        {dropdown.items.map((item) => (
                        <Link
                            key={item.name}
                            href={item.href}
                            className="block px-4 py-2 text-slate-700 hover:bg-orange-50 hover:text-orange-600"
                            onClick={closeDropdowns}
                        >
                            {item.name}
                        </Link>
                        ))}
                    </div>
                    )}
                </div>
                ))}

                {/* Log In Button */}
                <Link
                href="/login"
                className="border border-orange-600 text-orange-600 px-6 py-2 rounded-lg font-medium hover:bg-orange-50 transition-colors"
                >
                Log In
                </Link>
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
                {[
                    { name: "Scouting Reports", items: scoutingItems },
                    { name: "Games", items: gameItems },
                    { name: "Submit Missing Player", items: submitItems },
                ].map((dropdown) => (
                    <div key={dropdown.name}>
                    <button
                        onClick={() => toggleDropdown(dropdown.name)}
                        className={`flex items-center justify-between w-full ${
                        dropdown.name === "Submit Missing Player"
                            ? "bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
                            : "text-slate-700 hover:text-orange-600 font-medium px-2 py-1"
                        } transition-colors`}
                    >
                        {dropdown.name} <ChevronDown className="h-4 w-4 ml-1" />
                    </button>
                    {openDropdown === dropdown.name && (
                        <div className="ml-4 mt-2 flex flex-col space-y-2">
                        {dropdown.items.map((item) => (
                            <Link
                            key={item.name}
                            href={item.href}
                            className="text-slate-600 hover:text-orange-600 transition-colors"
                            onClick={() => {
                                closeDropdowns();
                                setIsOpen(false);
                            }}
                            >
                            {item.name}
                            </Link>
                        ))}
                        </div>
                    )}
                    </div>
                ))}

                <Link
                    href="/login"
                    className="border border-orange-600 text-orange-600 px-6 py-2 rounded-lg font-medium hover:bg-orange-50 transition-colors w-fit"
                    onClick={() => setIsOpen(false)}
                >
                    Log In
                </Link>
                </div>
            </div>
            )}
        </div>
        </nav>
    );
}
