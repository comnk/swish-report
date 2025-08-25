export interface HighSchoolPlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    school: string;
    class?: string; // For high school and college
    stars: number,
    overallRating: number;
    strengths: string[];
    weaknesses: string[];
    aiAnalysis: string;
    draftProjection?: string;
}

export interface NBAPlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    college?: string;
    team_names?: string[];
    years_pro?: string;
    draft_year?: number,
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