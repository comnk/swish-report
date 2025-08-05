"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, TrendingUp, Award, MapPin, Calendar, Star, ArrowRight, BarChart3, GraduationCap } from 'lucide-react';
import Link from 'next/link';

export default function CollegePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [conferenceFilter, setConferenceFilter] = useState('all');
  const [yearFilter, setYearFilter] = useState('all');

  const players = [
    {
      id: 1,
      name: "Isaiah Rodriguez",
      position: "SF",
      height: "6'7\"",
      weight: "225 lbs",
      school: "Duke University",
      conference: "ACC",
      year: "Junior",
      draftProjection: "1st Round",
      grade: "A",
      nbaComparison: "Jayson Tatum",
      strengths: ["Versatile scorer", "Defensive intensity", "Leadership"],
      weaknesses: ["Ball handling in traffic", "Three-point consistency"],
      stats: { ppg: 18.5, rpg: 6.8, apg: 4.2, spg: 1.5 },
      analytics: { per: 22.4, ts: 0.582, usage: 26.8 }
    },
    {
      id: 2,
      name: "Marcus Davis",
      position: "PG",
      height: "6'1\"",
      weight: "180 lbs",
      school: "Gonzaga University",
      conference: "WCC",
      year: "Senior",
      draftProjection: "Late 1st Round",
      grade: "A-",
      nbaComparison: "Fred VanVleet",
      strengths: ["Court vision", "Clutch gene", "Basketball IQ"],
      weaknesses: ["Size limitations", "Athleticism"],
      stats: { ppg: 16.2, rpg: 3.8, apg: 9.1, spg: 2.1 },
      analytics: { per: 20.8, ts: 0.601, usage: 24.5 }
    },
    {
      id: 3,
      name: "Jaylen Washington",
      position: "C",
      height: "7'0\"",
      weight: "245 lbs",
      school: "Kentucky",
      conference: "SEC",
      year: "Freshman",
      draftProjection: "Lottery Pick",
      grade: "A+",
      nbaComparison: "Jaren Jackson Jr.",
      strengths: ["Rim protection", "Three-point shooting", "Mobility"],
      weaknesses: ["Post moves", "Rebounding technique"],
      stats: { ppg: 14.8, rpg: 8.9, apg: 1.5, bpg: 2.8 },
      analytics: { per: 25.1, ts: 0.615, usage: 22.3 }
    },
    {
      id: 4,
      name: "Cameron Mitchell",
      position: "SG",
      height: "6'4\"",
      weight: "200 lbs",
      school: "UCLA",
      conference: "Pac-12",
      year: "Sophomore",
      draftProjection: "2nd Round",
      grade: "B+",
      nbaComparison: "Norman Powell",
      strengths: ["Elite shooter", "Off-ball movement", "Work ethic"],
      weaknesses: ["Creating own shot", "Defensive consistency"],
      stats: { ppg: 15.3, rpg: 4.1, apg: 2.8, spg: 1.2 },
      analytics: { per: 18.7, ts: 0.598, usage: 21.9 }
    }
  ];

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         player.school.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesConference = conferenceFilter === 'all' || player.conference === conferenceFilter;
    const matchesYear = yearFilter === 'all' || player.year === yearFilter;
    
    return matchesSearch && matchesConference && matchesYear;
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
              <Link href="/high-school" className="text-slate-600 hover:text-blue-600 transition-colors">
                High School
              </Link>
              <Link href="/college" className="text-blue-600 font-medium border-b-2 border-blue-600">
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
            <Badge className="mb-4 bg-orange-100 text-orange-700 hover:bg-orange-200">
              <GraduationCap className="w-4 h-4 mr-1" />
              College Basketball
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              College Basketball
              <span className="text-blue-600 block">Draft Prospects</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              In-depth analysis of college basketball's top NBA prospects. Track performance, 
              development, and draft projections with advanced analytics.
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
              <Select value={conferenceFilter} onValueChange={setConferenceFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Conference" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Conferences</SelectItem>
                  <SelectItem value="ACC">ACC</SelectItem>
                  <SelectItem value="SEC">SEC</SelectItem>
                  <SelectItem value="Big Ten">Big Ten</SelectItem>
                  <SelectItem value="Big 12">Big 12</SelectItem>
                  <SelectItem value="Pac-12">Pac-12</SelectItem>
                  <SelectItem value="WCC">WCC</SelectItem>
                </SelectContent>
              </Select>
              <Select value={yearFilter} onValueChange={setYearFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Class Year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  <SelectItem value="Freshman">Freshman</SelectItem>
                  <SelectItem value="Sophomore">Sophomore</SelectItem>
                  <SelectItem value="Junior">Junior</SelectItem>
                  <SelectItem value="Senior">Senior</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Draft Mock Section */}
          <Card className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5 text-blue-600" />
                Mock Draft Preview
              </CardTitle>
              <CardDescription>
                Our AI's latest 2024 NBA Draft projections based on current performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 mb-1">#3</div>
                  <div className="font-medium">Jaylen Washington</div>
                  <div className="text-sm text-slate-600">Kentucky • C</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-orange-500 mb-1">#8</div>
                  <div className="font-medium">Isaiah Rodriguez</div>
                  <div className="text-sm text-slate-600">Duke • SF</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-green-600 mb-1">#28</div>
                  <div className="font-medium">Marcus Davis</div>
                  <div className="text-sm text-slate-600">Gonzaga • PG</div>
                </div>
              </div>
              <div className="mt-4 text-center">
                <Button variant="outline">
                  View Full Mock Draft
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Player Results */}
          <div className="space-y-6">
            {filteredPlayers.map((player) => (
              <Card key={player.id} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-200">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Player Info */}
                    <div className="lg:col-span-1">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold mb-1">{player.name}</h3>
                          <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                            <Badge variant="outline">{player.position}</Badge>
                            <span>{player.height} • {player.weight}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
                            <MapPin className="w-4 h-4" />
                            <span>{player.school}</span>
                          </div>
                          <div className="text-sm text-slate-600">
                            {player.conference} • {player.year}
                          </div>
                        </div>
                        <Badge 
                          className={`${
                            player.grade === 'A+' ? 'bg-green-100 text-green-700' : 
                            player.grade === 'A' ? 'bg-blue-100 text-blue-700' : 
                            player.grade === 'A-' ? 'bg-indigo-100 text-indigo-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}
                        >
                          {player.grade}
                        </Badge>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">Draft Projection:</div>
                          <Badge variant={player.draftProjection.includes('Lottery') ? 'default' : 'secondary'}>
                            {player.draftProjection}
                          </Badge>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">NBA Comparison:</div>
                          <div className="text-sm text-slate-600">{player.nbaComparison}</div>
                        </div>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="lg:col-span-1">
                      <div className="bg-slate-50 rounded-lg p-4">
                        <h4 className="font-medium text-slate-700 mb-3 text-center">Season Stats</h4>
                        <div className="grid grid-cols-2 gap-3">
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
                          <div className="text-center">
                            <div className="font-bold text-lg">{player.stats.spg || player.stats.bpg}</div>
                            <div className="text-xs text-slate-600">{player.stats.spg ? 'SPG' : 'BPG'}</div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-blue-50 rounded-lg p-4 mt-4">
                        <h4 className="font-medium text-slate-700 mb-3 text-center">Advanced Analytics</h4>
                        <div className="grid grid-cols-3 gap-3">
                          <div className="text-center">
                            <div className="font-bold text-lg">{player.analytics.per}</div>
                            <div className="text-xs text-slate-600">PER</div>
                          </div>
                          <div className="text-center">
                            <div className="font-bold text-lg">{(player.analytics.ts * 100).toFixed(1)}%</div>
                            <div className="text-xs text-slate-600">TS%</div>
                          </div>
                          <div className="text-center">
                            <div className="font-bold text-lg">{player.analytics.usage}%</div>
                            <div className="text-xs text-slate-600">USG</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Analysis */}
                    <div className="lg:col-span-1">
                      <div className="space-y-4">
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-2">Strengths:</div>
                          <div className="space-y-1">
                            {player.strengths.map((strength, index) => (
                              <div key={index} className="flex items-center text-sm text-slate-600">
                                <Star className="w-3 h-3 text-green-500 mr-2 flex-shrink-0" />
                                {strength}
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-2">Areas for Growth:</div>
                          <div className="space-y-1">
                            {player.weaknesses.map((weakness, index) => (
                              <div key={index} className="flex items-center text-sm text-slate-600">
                                <TrendingUp className="w-3 h-3 text-orange-500 mr-2 flex-shrink-0" />
                                {weakness}
                              </div>
                            ))}
                          </div>
                        </div>

                        <Button className="w-full bg-blue-600 hover:bg-blue-700 mt-4">
                          View Full Scouting Report
                          <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                      </div>
                    </div>
                  </div>
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