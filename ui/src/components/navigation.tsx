"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Menu, X, BarChart3, ChevronDown } from "lucide-react";

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);

  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");

    if (urlToken) {
      localStorage.setItem("token", urlToken);
      setIsAuthenticated(true);
      router.replace(pathname); // clean up ?token
    } else {
      setIsAuthenticated(!!localStorage.getItem("token"));
    }
  }, [pathname, router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    window.location.href = "/";
  };

  // ----- Dropdown config -----
  const scoutingItems = [
    { name: "High School", href: "/scouting-reports/high-school" },
    { name: "College", href: "/scouting-reports/college" },
    { name: "NBA", href: "/scouting-reports/nba" },
  ];

  const gameItems = [
    { name: "Lineup Builder", href: "/games/lineup-builder/landing-page" },
    { name: "Poeltl", href: "/games/poeltl" },
  ];

  const communityItems = [
    { name: "Community Lineups", href: "/community/player-lineups" },
    { name: "Community Takes", href: "/community/hot-takes" },
  ];

  const submitItems = [
    { name: "High School", href: "/submit-player/high-school" },
    { name: "College", href: "/submit-player/college" },
    { name: "NBA", href: "/submit-player/nba" },
  ];

  const dropdowns = [
    { name: "Scouting Reports", items: scoutingItems },
    { name: "Games", items: gameItems },
    { name: "Community", items: communityItems },
    { name: "Submit Missing Player", items: submitItems },
  ];

  const toggleDropdown = (name: string) =>
    setOpenDropdown(openDropdown === name ? null : name);
  const closeDropdowns = () => setOpenDropdown(null);

  // Close dropdown if clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        closeDropdowns();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav
      ref={navRef}
      className="w-full bg-white/95 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50"
    >
      <div className="w-full px-4 sm:px-6 lg:px-8">
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
          <div className="hidden md:flex items-center flex-1 justify-end gap-6">
            {dropdowns.map((dropdown) => (
              <div key={dropdown.name} className="relative">
                <button
                  onClick={() => toggleDropdown(dropdown.name)}
                  className={`flex items-center font-medium transition-colors ${
                    dropdown.name === "Submit Missing Player"
                      ? "bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
                      : "text-slate-700 hover:text-orange-600"
                  }`}
                >
                  {dropdown.name} <ChevronDown className="h-4 w-4 ml-1" />
                </button>
                {openDropdown === dropdown.name && (
                  <div className="absolute left-0 mt-2 w-48 bg-white shadow-lg rounded-md border border-slate-200 py-2 z-50">
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

            {!isAuthenticated ? (
              <Link
                href="/login"
                className="border border-orange-600 text-orange-600 px-6 py-2 rounded-lg font-medium hover:bg-orange-50 transition-colors"
              >
                Log In
              </Link>
            ) : (
              <div className="relative">
                <button
                  onClick={() => toggleDropdown("Account")}
                  className="flex items-center text-slate-700 hover:text-orange-600 font-medium"
                >
                  Account <ChevronDown className="h-4 w-4 ml-1" />
                </button>
                {openDropdown === "Account" && (
                  <div className="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-md border border-slate-200 py-2 z-50">
                    <Link
                      href="/dashboard"
                      className="block px-4 py-2 text-slate-700 hover:bg-orange-50 hover:text-orange-600"
                      onClick={closeDropdowns}
                    >
                      Dashboard
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        closeDropdowns();
                      }}
                      className="w-full text-left px-4 py-2 text-red-500 hover:bg-red-50"
                    >
                      Log Out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-slate-700 hover:text-orange-600 transition-colors"
            >
              {isOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div
          className={`md:hidden overflow-hidden transition-max-height duration-300 ${
            isOpen ? "max-h-screen py-4 border-t border-slate-200" : "max-h-0"
          }`}
        >
          <div className="flex flex-col space-y-4 px-4 w-full">
            {dropdowns.map((dropdown) => (
              <div key={dropdown.name}>
                <button
                  onClick={() => toggleDropdown(dropdown.name)}
                  className={`flex items-center justify-between w-full px-4 py-2 font-medium transition-colors ${
                    dropdown.name === "Submit Missing Player"
                      ? "bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                      : "text-slate-700 hover:text-orange-600"
                  }`}
                >
                  {dropdown.name} <ChevronDown className="h-4 w-4 ml-1" />
                </button>
                {openDropdown === dropdown.name && (
                  <div className="ml-2 mt-2 flex flex-col space-y-2">
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

            {!isAuthenticated ? (
              <Link
                href="/login"
                className="border border-orange-600 text-orange-600 px-6 py-2 rounded-lg font-medium hover:bg-orange-50 transition-colors w-fit"
                onClick={() => setIsOpen(false)}
              >
                Log In
              </Link>
            ) : (
              <div>
                <button
                  onClick={() => toggleDropdown("AccountMobile")}
                  className="flex items-center justify-between w-full px-4 py-2 font-medium text-slate-700 hover:text-orange-600"
                >
                  Account <ChevronDown className="h-4 w-4 ml-1" />
                </button>
                {openDropdown === "AccountMobile" && (
                  <div className="ml-2 mt-2 flex flex-col space-y-2">
                    <Link
                      href="/dashboard"
                      className="text-slate-600 hover:text-orange-600 transition-colors"
                      onClick={() => {
                        closeDropdowns();
                        setIsOpen(false);
                      }}
                    >
                      Dashboard
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsOpen(false);
                      }}
                      className="text-red-500 hover:text-red-600 text-left"
                    >
                      Log Out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
