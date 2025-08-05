"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Award, TrendingUp, Calendar, Star, ArrowRight, BarChart3, Target } from 'lucide-react';
import Link from 'next/link';

export default function DraftPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const mockDraft2024 = [
    {
      pick: 1,
      name: "Alexandre Sarr",
      position: "C",
      school: "Perth Wildcats",
      age: 19,
      height: "7'1\"",
      grade: "A+",
      strengths: ["Elite rim protection", "Modern skillset", "High ceiling"],
      team: "Atlanta Hawks"
    },
    {
      pick: 2,
      name: "Reed Sheppard",
      position: "PG",
      school: "Kentucky",
      age: 19,
      height: "6'3\"",
      grade: "A",
      strengths: ["Elite shooter", "Basketball IQ", "Two-way impact"],
      team: "Washington Wizards"
    },
    {
      pick: 3,
      name: "Matas Buzelis",
      position: "SF",
      school: "G League Ignite",
      age: 19,
      height: "6'10\"",
      grade: "A",
      strengths: ["Versatility", "Shot creation", "Upside"],
      team: "Chicago Bulls"
    },
    {
      pick: 4,
      name: "Stephon Castle",
      position: "SG",
      school: "UConn",
      age: 19,
      height: "6'6\"",
      grade: "A-",
      strengths: ["Defensive intensity", "Leadership", "Winning pedigree"],
      team: "San Antonio Spurs"
    },
    {
      pick: 5,
      name: "Ron Holland",
      position: "SF",
      school: "G League Ignite",
      age: 18,
      height: "6'8\"",
      grade: "A-",
      strengths: ["Athleticism", "Defensive potential", "Motor"],
      team: "Detroit Pistons"
    }
  ];

  const draftClasses = [
    {
      year: 2024,
      strength: "Wing depth",
      topProspect: "Alexandre Sarr",
      grade: "A-",
      description: "Strong class with good depth in wings and guards"
    },
    {
      year: 2025,
      strength: "Overall talent",
      topProspect: "Cooper Flagg",
      grade: "A+",
      description: "Generational class with multiple franchise-changing talents"
    },
    {
      year: 2026,
      strength: "International talent",
      topProspect: "Hugo Gonzalez",
      grade: "A",
      description: "Deep international class with several top-tier prospects"
    }
  ];

  const risersAndFallers = [
    {
      name: "Ja'Kobe Walter",
      position: "SG",
      school: "Baylor",
      movement: "Rising",
      change: "+8",
      reason: "Improved consistency and shot selection"
    },
    {
      name: "Cody Williams",
      position: "SF",
      school: "Colorado",
      movement: "Rising",
      change: "+5",
      reason: "Strong tournament performance"
    },
    {
      name: "Tyler Smith",
      position: "PF",
      school: "G League Ignite",
      movement: "Falling",
      change: "-6",
      reason: "Inconsistent motor and effort"
    }
  ];

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
              <Link href="/nba" className="text-slate-600 hover:text-blue-600 transition-colors">
                NBA
              </Link>
              <Link href="/draft" className="text-blue-600 font-medium border-b-2 border-blue-600">
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
            <Badge className="mb-4 bg-green-100 text-green-700 hover:bg-green-200">
              <Award className="w-4 h-4 mr-1" />
              NBA Draft Analysis
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              NBA Draft
              <span className="text-blue-600 block">Intelligence Hub</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Comprehensive AI-powered NBA Draft analysis, mock drafts, and prospect evaluations. 
              Stay ahead with the most accurate draft projections and scouting insights.
            </p>
          </div>

          <Tabs defaultValue="mock-draft" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-8">
              <TabsTrigger value="mock-draft">Mock Draft</TabsTrigger>
              <TabsTrigger value="big-board">Big Board</TabsTrigger>
              <TabsTrigger value="draft-classes">Draft Classes</TabsTrigger>
              <TabsTrigger value="risers-fallers">Movers</TabsTrigger>
            </TabsList>

            <TabsContent value="mock-draft" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-600" />
                    2024 NBA Mock Draft - First Round
                  </CardTitle>
                  <CardDescription>
                    Our AI's latest first-round projections based on team needs and prospect evaluations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockDraft2024.map((prospect) => (
                      <div key={prospect.pick} className="flex items-center justify-between p-4 bg-white rounded-lg border hover:shadow-md transition-shadow">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                            {prospect.pick}
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{prospect.name}</h3>
                            <div className="flex items-center gap-2 text-sm text-slate-600">
                              <Badge variant="outline">{prospect.position}</Badge>
                              <span>{prospect.school}</span>
                              <span>• Age {prospect.age}</span>
                              <span>• {prospect.height}</span>
                            </div>
                            <div className="text-sm text-slate-500 mt-1">
                              → {prospect.team}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge 
                            className={`mb-2 ${
                              prospect.grade === 'A+' ? 'bg-green-100 text-green-700' : 
                              prospect.grade === 'A' ? 'bg-blue-100 text-blue-700' : 
                              'bg-indigo-100 text-indigo-700'
                            }`}
                          >
                            {prospect.grade}
                          </Badge>
                          <div className="text-sm text-slate-600">
                            {prospect.strengths[0]}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 text-center">
                    <Button variant="outline" size="lg">
                      View Full Mock Draft (60 picks)
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="big-board" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Draft Big Board - Top Prospects</CardTitle>
                  <CardDescription>
                    Our comprehensive ranking of the best available prospects regardless of team fit
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <Award className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-600 mb-2">Big Board Coming Soon</h3>
                    <p className="text-slate-500">
                      Our comprehensive prospect rankings will be available after the college season.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="draft-classes" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {draftClasses.map((draftClass) => (
                  <Card key={draftClass.year} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>{draftClass.year} Class</span>
                        <Badge 
                          className={`${
                            draftClass.grade === 'A+' ? 'bg-green-100 text-green-700' : 
                            draftClass.grade === 'A' ? 'bg-blue-100 text-blue-700' : 
                            'bg-indigo-100 text-indigo-700'
                          }`}
                        >
                          {draftClass.grade}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        Strength: {draftClass.strength}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <div className="text-sm font-medium text-slate-700 mb-1">Top Prospect:</div>
                          <div className="font-semibold">{draftClass.topProspect}</div>
                        </div>
                        <p className="text-sm text-slate-600">
                          {draftClass.description}
                        </p>
                        <Button variant="outline" className="w-full">
                          View {draftClass.year} Prospects
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="risers-fallers" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-700">
                      <TrendingUp className="w-5 h-5" />
                      Stock Risers
                    </CardTitle>
                    <CardDescription>
                      Prospects whose draft stock has been trending upward
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {risersAndFallers.filter(p => p.movement === 'Rising').map((player, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div>
                            <h4 className="font-semibold">{player.name}</h4>
                            <div className="text-sm text-slate-600">
                              {player.position} • {player.school}
                            </div>
                            <div className="text-sm text-slate-500 mt-1">
                              {player.reason}
                            </div>
                          </div>
                          <Badge className="bg-green-600 text-white">
                            {player.change}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-red-700">
                      <TrendingUp className="w-5 h-5 rotate-180" />
                      Stock Fallers
                    </CardTitle>
                    <CardDescription>
                      Prospects who have seen their draft stock decline recently
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {risersAndFallers.filter(p => p.movement === 'Falling').map((player, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                          <div>
                            <h4 className="font-semibold">{player.name}</h4>
                            <div className="text-sm text-slate-600">
                              {player.position} • {player.school}
                            </div>
                            <div className="text-sm text-slate-500 mt-1">
                              {player.reason}
                            </div>
                          </div>
                          <Badge className="bg-red-600 text-white">
                            {player.change}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          {/* Draft Calendar */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                2024 Draft Calendar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="font-semibold text-blue-700">Draft Lottery</div>
                  <div className="text-sm text-slate-600">May 12, 2024</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="font-semibold text-green-700">Draft Combine</div>
                  <div className="text-sm text-slate-600">May 21-26, 2024</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="font-semibold text-orange-700">Withdrawal Deadline</div>
                  <div className="text-sm text-slate-600">June 16, 2024</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="font-semibold text-purple-700">NBA Draft</div>
                  <div className="text-sm text-slate-600">June 26-27, 2024</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}