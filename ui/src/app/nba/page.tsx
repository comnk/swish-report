"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, TrendingUp, Trophy, MapPin, Calendar, Star, ArrowRight, BarChart3, Activity } from 'lucide-react';
import Link from 'next/link';

export default function NBAPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [teamFilter, setTeamFilter] = useState('all');
  const [positionFilter, setPositionFilter] = useState('all');

  const players = [
    {
      id: 1,
      name: "Luka Dončić",
      position: "PG/SG",
      age: 24,
      team: "Dallas Mavericks",
      experience: "6th Year",
      contract: "$215M / 5yr",
      careerGrade: "S",
      currentForm: "Elite",
      strengths: ["Elite playmaking", "Clutch performer", "Basketball IQ"],
      concerns: ["Defensive consistency", "Conditioning"],
      stats: { ppg: 32.8, rpg: 8.5, apg: 9.1, fg: 48.7 },
      advanced: { per: 31.2, ws: 12.4, vorp: 7.8 },
      projection: "MVP Candidate"
    },
    {
      id: 2,
      name: "Jayson Tatum",
      position: "SF/PF",
      age: 25,
      team: "Boston Celtics",
      experience: "7th Year",
      contract: "$195M / 5yr",
      careerGrade: "A+",
      currentForm: "All-Star",
      strengths: ["Versatile scoring", "Clutch gene", "Two-way impact"],
      concerns: ["Shot selection", "Playmaking consistency"],
      stats: { ppg: 27.2, rpg: 8.1, apg: 4.8, fg: 46.8 },
      advanced: { per: 25.8, ws: 10.2, vorp: 5.9 },
      projection: "Championship Leader"
    },
    {
      id: 3,
      name: "Victor Wembanyama",
      position: "C",
      age: 20,
      team: "San Antonio Spurs",
      experience: "Rookie",
      contract: "$55M / 4yr",
      careerGrade: "A+",
      currentForm: "Rising Star",
      strengths: ["Unique physical tools", "Shot blocking", "Three-point shooting"],
      concerns: ["NBA physicality", "Injury prevention"],
      stats: { ppg: 21.8, rpg: 10.2, apg: 3.5, bpg: 3.2 },
      advanced: { per: 24.1, ws: 7.8, vorp: 4.2 },
      projection: "Future Superstar"
    },
    {
      id: 4,
      name: "Anthony Edwards",
      position: "SG",
      age: 22,
      team: "Minnesota Timberwolves",
      experience: "4th Year",
      contract: "$244M / 5yr",
      careerGrade: "A",
      currentForm: "All-Star",
      strengths: ["Elite athleticism", "Scoring versatility", "Leadership growth"],
      concerns: ["Shot efficiency", "Defensive consistency"],
      stats: { ppg: 25.6, rpg: 5.8, apg: 5.2, fg: 46.1 },
      advanced: { per: 22.4, ws: 8.9, vorp: 4.8 },
      projection: "Franchise Cornerstone"
    }
  ];

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         player.team.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTeam = teamFilter === 'all' || player.team === teamFilter;
    const matchesPosition = positionFilter === 'all' || player.position.includes(positionFilter);
    
    return matchesSearch && matchesTeam && matchesPosition;
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
              <Link href="/college" className="text-slate-600 hover:text-blue-600 transition-colors">
                College
              </Link>
              <Link href="/nba" className="text-blue-600 font-medium border-b-2 border-blue-600">
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
            <Badge className="mb-4 bg-purple-100 text-purple-700 hover:bg-purple-200">
              <Trophy className="w-4 h-4 mr-1" />
              NBA Analysis
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              NBA Player
              <span className="text-blue-600 block">Analysis & Insights</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Comprehensive AI-powered analysis of NBA players, career trajectories, and performance insights. 
              Track the league's elite talent with advanced analytics.
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
                    placeholder="Search players or teams..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={teamFilter} onValueChange={setTeamFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Team" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Teams</SelectItem>
                  <SelectItem value="Boston Celtics">Boston Celtics</SelectItem>
                  <SelectItem value="Dallas Mavericks">Dallas Mavericks</SelectItem>
                  <SelectItem value="Minnesota Timberwolves">Minnesota Timberwolves</SelectItem>
                  <SelectItem value="San Antonio Spurs">San Antonio Spurs</SelectItem>
                </SelectContent>
              </Select>
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
            </div>
          </div>

          {/* League Leaders */}
          <Card className="mb-8 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Current Season Leaders
              </CardTitle>
              <CardDescription>
                Top performers in key statistical categories this season
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">Scoring</div>
                  <div className="font-bold">Luka Dončić</div>
                  <div className="text-lg text-blue-600">32.8 PPG</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">Rebounding</div>
                  <div className="font-bold">Domantas Sabonis</div>
                  <div className="text-lg text-green-600">12.4 RPG</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">Assists</div>
                  <div className="font-bold">Tyrese Haliburton</div>
                  <div className="text-lg text-orange-600">10.8 APG</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">Blocks</div>
                  <div className="font-bold">Victor Wembanyama</div>
                  <div className="text-lg text-red-600">3.2 BPG</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Player Results */}
          <div className="space-y-6">
            {filteredPlayers.map((player) => (
              <Card key={player.id} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-200">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Player Info */}
                    <div className="lg:col-span-1">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold mb-1">{player.name}</h3>
                          <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                            <Badge variant="outline">{player.position}</Badge>
                            <span>Age {player.age}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
                            <MapPin className="w-4 h-4" />
                            <span>{player.team}</span>
                          </div>
                          <div className="text-sm text-slate-600">
                            {player.experience}
                          </div>
                        </div>
                        <Badge 
                          className={`${
                            player.careerGrade === 'S' ? 'bg-purple-100 text-purple-700' : 
                            player.careerGrade === 'A+' ? 'bg-green-100 text-green-700' : 
                            'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {player.careerGrade}
                        </Badge>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">Contract:</div>
                          <div className="text-sm text-slate-600">{player.contract}</div>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">Current Form:</div>
                          <Badge variant={player.currentForm === 'Elite' ? 'default' : 'secondary'}>
                            {player.currentForm}
                          </Badge>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">Projection:</div>
                          <div className="text-sm text-slate-600">{player.projection}</div>
                        </div>
                      </div>
                    </div>

                    {/* Current Stats */}
                    <div className="lg:col-span-1">
                      <div className="bg-slate-50 rounded-lg p-4">
                        <h4 className="font-medium text-slate-700 mb-3 text-center">2023-24 Stats</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">PPG</span>
                            <span className="font-semibold">{player.stats.ppg}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">RPG</span>
                            <span className="font-semibold">{player.stats.rpg}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">APG</span>
                            <span className="font-semibold">{player.stats.apg}</span>
                          </div>
                          {player.stats.bpg && (
                            <div className="flex justify-between">
                              <span className="text-sm text-slate-600">BPG</span>
                              <span className="font-semibold">{player.stats.bpg}</span>
                            </div>
                          )}
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">FG%</span>
                            <span className="font-semibold">{player.stats.fg}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Advanced Stats */}
                    <div className="lg:col-span-1">
                      <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-medium text-slate-700 mb-3 text-center">Advanced</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">PER</span>
                            <span className="font-semibold">{player.advanced.per}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">Win Shares</span>
                            <span className="font-semibold">{player.advanced.ws}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-slate-600">VORP</span>
                            <span className="font-semibold">{player.advanced.vorp}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Analysis */}
                    <div className="lg:col-span-1">
                      <div className="space-y-4">
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-2">Key Strengths:</div>
                          <div className="space-y-1">
                            {player.strengths.slice(0, 2).map((strength, index) => (
                              <div key={index} className="flex items-center text-sm text-slate-600">
                                <Star className="w-3 h-3 text-green-500 mr-2 flex-shrink-0" />
                                {strength}
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-2">Watch Points:</div>
                          <div className="space-y-1">
                            {player.concerns.map((concern, index) => (
                              <div key={index} className="flex items-center text-sm text-slate-600">
                                <TrendingUp className="w-3 h-3 text-orange-500 mr-2 flex-shrink-0" />
                                {concern}
                              </div>
                            ))}
                          </div>
                        </div>

                        <Button className="w-full bg-blue-600 hover:bg-blue-700 mt-4">
                          View Career Analysis
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