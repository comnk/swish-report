export interface HighSchoolPlayer {
    id: string;
    full_name: string;
    position: string;
    height: string;
    weight: string;
    school: string;
    class?: string;
    stars: number;
    overallRating: number;
    strengths: string[];
    weaknesses: string[];
    aiAnalysis: string;
    image_url: string;
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
    strengths: string[];
    weaknesses: string[];
    aiAnalysis: string;
    image_url?: string;
}