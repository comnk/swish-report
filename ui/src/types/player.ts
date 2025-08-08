export interface Player {
    id: string;
    name: string;
    position: string;
    height: string;
    weight: string;
    school: string;
    class?: string; // For high school and college
    experience?: string; // For NBA
    overallRating: number;
    stats: {
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
    draftProjection?: string;
    salary?: string; // For NBA players
}

export interface DraftProspect {
    id: string;
    name: string;
    position: string;
    height: string;
    school: string;
    overallRating: number;
    stats: {
        points: number;
        rebounds: number;
        assists: number;
    };
    projection: string;
    movement: "up" | "down" | "same";
    aiAnalysis: string;
}