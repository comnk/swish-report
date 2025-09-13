export interface Lineup {
  lineup_id: number;
  user_id: number;
  mode: string;
  players: Record<string, number>;
  scouting_report: {
    overallScore: number;
    strengths: string[];
    weaknesses: string[];
    synergyNotes: string;
    floor: string;
    ceiling: string;
    overallAnalysis: string;
  };
}