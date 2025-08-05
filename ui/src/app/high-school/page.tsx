"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Filter, TrendingUp, Users, MapPin, Calendar, Star, ArrowRight, BarChart3 } from 'lucide-react';
import Link from 'next/link';

export default function HighSchoolPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [positionFilter, setPositionFilter] = useState('all');
  const [classFilter, setClassFilter] = useState('all');

  const players = [
    {
      id: 1,
      name: "Marcus Thompson",
      position: "PG",
      height: "6'2\"",
      weight: "185 lbs",
      school: "Oak Hill Academy",
      location: "Mouth of Wilson, VA",
      class: "2024",
      ranking: 5,
      grade: "A+",
      collegeCommitment: "Duke University",
      strengths: ["Elite court vision", "Strong leadership", "NBA-ready skillset"],
      weaknesses: ["Needs to improve shot consistency", "Physical strength"],
      stats: { ppg: 24.5, apg: 8.2, rpg: 5.1 }
    },
    {
      id: 2,
      name: "Jordan Williams",
      position: "SF",
      height: "6'8\"",
      weight: "210 lbs",
      school: "Montverde Academy",
      location: "Montverde, FL",
      class: "2024",
      ranking: 12,
      grade: "A",
      collegeCommitment: "Uncommitted",
      strengths: ["Versatile scorer", "Defensive length", "Basketball IQ"],
      weaknesses: ["Ball handling", "Three-point shooting"],
      stats: { ppg: 19.8, apg: 4.5, rpg: 7.3 }
    },
    {
      id: 3,
      name: "Alex Rodriguez",
      position: "C",
      height: "6'11\"",
      weight: "240 lbs",
      school: "IMG Academy",
      location: "Bradenton, FL",
      class: "2025",
      ranking: 8,
      grade: "A+",
      collegeCommitment: "Uncommitted",
      strengths: ["Rim protection", "Post moves", "Rebounding"],
      weaknesses: ["Mobility", "Free throw shooting"],
      stats: { ppg: 16.2, apg: 2.1, rpg: 11.8 }
    },
    {
      id: 4,
      name: "Tyler Johnson",
      position: "SG",
      height: "6'5\"",
      weight: "195 lbs",
      school: "Sierra Canyon",
      location: "Chatsworth, CA",
      class: "2024",
      ranking: 18,
      grade: "A-",
      collegeCommitment: "UCLA",
      strengths: ["Elite shooter", "Clutch performer", "Work ethic"],
      weaknesses: ["Playmaking", "Lateral quickness"],
      stats: { ppg: 22.3, apg: 3.8, rpg: 4.7 }
    }
  ];

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         player.school.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPosition = positionFilter === 'all' || player.position === positionFilter;
    const matchesClass = classFilter === 'all' || player.class === classFilter;
    
    return matchesSearch && matchesPosition && matchesClass;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900">Swish Report</h1>
            </Link>
            <nav className="hidden md:flex space-x-8">
              <Link href="/high-school" className="text-blue-600 font-medium border-b-2 border-blue-600">
                High School
              </Link>
              <Link href="/college" className="text-slate-600 hover:text-blue-600 transition-colors">
                College
              </Link>
              <Link href="/nba" className="text-slate-600 hover:text-blue-600 transition-colors">
                NBA
              </Link>
              <Link href="/draft" className="text-slate-600 hover:text-blue-600 transition-colors">
                Draft Analysis
              </Link>
            </nav>
            <Button className="bg-blue-600 hover:bg-blue-700">
              Sign In
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-blue-100 text-blue-700 hover:bg-blue-200">
              <Users className="w-4 h-4 mr-1" />
              High School Prospects
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              Elite High School
              <span className="text-blue-600 block">Basketball Prospects</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Comprehensive AI-powered scouting reports for the nation's top high school basketball talent. 
              Discover the next generation of college and NBA stars.
            </p>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <Input
                    type="text"
                    placeholder="Search players or schools..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={positionFilter} onValueChange={setPositionFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Position" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Positions</SelectItem>
                  <SelectItem value="PG">Point Guard</SelectItem>
                  <SelectItem value="SG">Shooting Guard</SelectItem>
                  <SelectItem value="SF">Small Forward</SelectItem>
                  <SelectItem value="PF">Power Forward</SelectItem>
                  <SelectItem value="C">Center</SelectItem>
                </SelectContent>
              </Select>
              <Select value={classFilter} onValueChange={setClassFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Class" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Classes</SelectItem>
                  <SelectItem value="2024">Class of 2024</SelectItem>
                  <SelectItem value="2025">Class of 2025</SelectItem>
                  <SelectItem value="2026">Class of 2026</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">2,847</div>
                <div className="text-slate-600">Players Tracked</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-orange-500 mb-2">156</div>
                <div className="text-slate-600">D1 Commits</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">89%</div>
                <div className="text-slate-600">Accuracy Rate</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">24</div>
                <div className="text-slate-600">Future NBA</div>
              </CardContent>
            </Card>
          </div>

          {/* Player Results */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredPlayers.map((player) => (
              <Card key={player.id} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-200">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl font-bold mb-1">{player.name}</CardTitle>
                      <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                        <Badge variant="outline">{player.position}</Badge>
                        <span>{player.height} • {player.weight}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <MapPin className="w-4 h-4" />
                        <span>{player.school}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-600 mt-1">
                        <Calendar className="w-4 h-4" />
                        <span>Class of {player.class}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge 
                        className={`mb-2 ${
                          player.grade === 'A+' ? 'bg-green-100 text-green-700' : 
                          player.grade === 'A' ? 'bg-blue-100 text-blue-700' : 
                          'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {player.grade}
                      </Badge>
                      <div className="text-sm text-slate-600">
                        #{player.ranking} National
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-slate-50 rounded-lg">
                    <div className="text-center">
                      <div className="font-bold text-lg">{player.stats.ppg}</div>
                      <div className="text-xs text-slate-600">PPG</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-lg">{player.stats.rpg}</div>
                      <div className="text-xs text-slate-600">RPG</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-lg">{player.stats.apg}</div>
                      <div className="text-xs text-slate-600">APG</div>
                    </div>
                  </div>

                  {/* College Commitment */}
                  <div className="mb-4">
                    <div className="text-sm font-medium text-slate-700 mb-1">College Commitment:</div>
                    <Badge variant={player.collegeCommitment === "Uncommitted" ? "secondary" : "default"}>
                      {player.collegeCommitment}
                    </Badge>
                  </div>

                  {/* Strengths */}
                  <div className="mb-4">
                    <div className="text-sm font-medium text-slate-700 mb-2">Strengths:</div>
                    <div className="space-y-1">
                      {player.strengths.slice(0, 2).map((strength, index) => (
                        <div key={index} className="flex items-center text-sm text-slate-600">
                          <Star className="w-3 h-3 text-green-500 mr-2 flex-shrink-0" />
                          {strength}
                        </div>
                      ))}
                    </div>
                  </div>

                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    View Full Scouting Report
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Load More */}
          <div className="text-center mt-8">
            <Button variant="outline" size="lg">
              Load More Players
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}