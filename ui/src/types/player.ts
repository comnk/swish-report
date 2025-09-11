export interface HighSchoolPlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    school: string;
    class?: string;
    stars: number,
    overallRating: number;
    strengths: string[];
    weaknesses: string[];
    aiAnalysis: string;
}

export interface CollegePlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    school: string;
}

export interface NBAPlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    college?: string;
    team_names: string[];
    years_pro?: string;
    draft_year?: number,
    draft_round?: number,
    draft_pick?: number,
    stars: number,
    overallRating: number;
    stats?: {
        points: number;
        rebounds: number;
        assists: number;
        fieldGoalPercentage?: number;
        threePointPercentage?: number;
        per?: number; // NBA Player Efficiency Rating
        winShares?: number; // NBA Win Shares
    };
    strengths: string[];
    weaknesses: string[];
    aiAnalysis: string;
}