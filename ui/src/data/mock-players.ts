import { HighSchoolPlayer, Player } from "@/types/player";

export const mockHighSchoolPlayers: HighSchoolPlayer[] = [
    {
        id: "hs1",
        name: "Marcus Thompson",
        position: "PG",
        height: "6'3\"",
        weight: "185 lbs",
        school: "Oak Hill Academy",
        class: "2024",
        overallRating: 94,
        strengths: ["Court Vision", "Three-Point Shooting", "Leadership"],
        weaknesses: ["Defensive Consistency", "Turnovers"],
        aiAnalysis: "Elite floor general with exceptional basketball IQ. Projects as a lottery pick with immediate impact potential at the collegiate level.",
        draftProjection: "Lottery Pick"
    },
    {
        id: "hs2",
        name: "Jordan Williams",
        position: "SF",
        height: "6'8\"",
        weight: "210 lbs",
        school: "Montverde Academy",
        class: "2024",
        overallRating: 91,
        strengths: ["Versatility", "Athleticism", "Rebounding"],
        weaknesses: ["Ball Handling", "Free Throw Shooting"],
        aiAnalysis: "Versatile wing with excellent size and athleticism. Strong two-way potential with continued development of perimeter skills.",
        draftProjection: "First Round"
    },
    {
        id: "hs3",
        name: "Alex Rodriguez",
        position: "C",
        height: "6'11\"",
        weight: "240 lbs",
        school: "IMG Academy",
        class: "2025",
        overallRating: 88,
        strengths: ["Shot Blocking", "Post Moves", "Rebounding"],
        weaknesses: ["Perimeter Defense", "Three-Point Range"],
        aiAnalysis: "Traditional big man with excellent rim protection. Needs to develop modern center skills but has solid fundamentals.",
        draftProjection: "Second Round"
    }
];

export const mockCollegePlayers: Player[] = [
    {
        id: "col1",
        name: "Tyler Johnson",
        position: "PG",
        height: "6'1\"",
        weight: "180 lbs",
        school: "Duke University",
        class: "Junior",
        overallRating: 92,
        stats: {
        points: 18.7,
        rebounds: 3.9,
        assists: 7.8,
        fieldGoalPercentage: 46,
        threePointPercentage: 41
        },
        strengths: ["Three-Point Shooting", "Decision Making", "Clutch Performance"],
        weaknesses: ["Size", "Defensive Rebounding"],
        aiAnalysis: "Elite shooter with excellent decision-making. Projects as a solid NBA backup with starter upside if he improves defensively.",
        draftProjection: "Late First Round"
    },
    {
        id: "col2",
        name: "David Chen",
        position: "PF",
        height: "6'9\"",
        weight: "225 lbs",
        school: "Gonzaga University",
        class: "Senior",
        overallRating: 89,
        stats: {
        points: 21.2,
        rebounds: 8.5,
        assists: 2.7,
        fieldGoalPercentage: 54,
        threePointPercentage: 37
        },
        strengths: ["Shooting Range", "Basketball IQ", "Versatility"],
        weaknesses: ["Athleticism", "Lateral Quickness"],
        aiAnalysis: "Skilled big man with modern skill set. Excellent shooter for his size but may struggle with NBA athleticism.",
        draftProjection: "Second Round"
    },
    {
        id: "col3",
        name: "Michael Davis",
        position: "SG",
        height: "6'5\"",
        weight: "200 lbs",
        school: "Kentucky",
        class: "Sophomore",
        overallRating: 90,
        stats: {
        points: 20.1,
        rebounds: 5.2,
        assists: 3.8,
        fieldGoalPercentage: 49,
        threePointPercentage: 39
        },
        strengths: ["Scoring Ability", "Size", "Defensive Potential"],
        weaknesses: ["Consistency", "Ball Handling"],
        aiAnalysis: "Dynamic scorer with good size for his position. Has the tools to be a solid NBA contributor with improved consistency.",
        draftProjection: "First Round"
    }
];

export const mockNBAPlayers: Player[] = [
    {
        id: "nba1",
        name: "LeBron James",
        position: "SF",
        height: "6'9\"",
        weight: "250 lbs",
        school: "Los Angeles Lakers",
        experience: "21 Years",
        overallRating: 96,
        stats: {
        points: 25.3,
        rebounds: 7.3,
        assists: 7.3,
        fieldGoalPercentage: 54,
        threePointPercentage: 41,
        per: 25.8,
        winShares: 8.1
        },
        strengths: ["Basketball IQ", "Versatility", "Leadership"],
        weaknesses: ["Age", "Free Throw Shooting"],
        aiAnalysis: "Still performing at an elite level despite his age. Continues to be one of the most impactful players in the league.",
        salary: "$47.6M"
    },
    {
        id: "nba2",
        name: "Jayson Tatum",
        position: "SF",
        height: "6'8\"",
        weight: "210 lbs",
        school: "Boston Celtics",
        experience: "7 Years",
        overallRating: 94,
        stats: {
        points: 26.9,
        rebounds: 8.1,
        assists: 4.9,
        fieldGoalPercentage: 47,
        threePointPercentage: 35,
        per: 22.4,
        winShares: 7.2
        },
        strengths: ["Scoring", "Size", "Clutch Performance"],
        weaknesses: ["Playmaking", "Efficiency"],
        aiAnalysis: "Elite scorer entering his prime. Has established himself as a top-tier player with championship experience.",
        salary: "$34.8M"
    },
    {
        id: "nba3",
        name: "Victor Wembanyama",
        position: "C",
        height: "7'4\"",
        weight: "210 lbs",
        school: "San Antonio Spurs",
        experience: "Rookie",
        overallRating: 91,
        stats: {
        points: 21.4,
        rebounds: 10.6,
        assists: 3.9,
        fieldGoalPercentage: 46,
        threePointPercentage: 33,
        per: 23.1,
        winShares: 4.8
        },
        strengths: ["Shot Blocking", "Unique Size", "Shooting Range"],
        weaknesses: ["Strength", "Injury Concerns"],
        aiAnalysis: "Generational talent with unprecedented combination of size and skill. Projects to be a perennial All-Star and DPOY candidate.",
        salary: "$12.2M"
    }
];