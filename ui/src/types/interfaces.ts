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

export interface SeasonStats {
  season: string;
  team: string;
  gp: number;
  ppg: number;
  apg: number;
  rpg: number;
  spg?: number;
  bpg?: number;
  topg?: number;
  fpg?: number;
  pts?: number;
  fga?: number;
  fgm?: number;
  three_pa?: number;
  three_pm?: number;
  fta?: number;
  ftm?: number;
  ts_pct?: number;
  fg?: number;
  efg?: number;
  three_p?: number;
  ft?: number;
  [key: string]: string | number | undefined;
}

export interface PlayerStats {
  full_name: string;
  ppg: number;
  apg: number;
  rpg: number;
  all_seasons: SeasonStats[];
}

export interface ComparisonData {
  player1: PlayerStats;
  player2: PlayerStats;
  ai_analysis?: string;
}

export interface PlayerResponse {
  full_name: string;
  latest: {
    ppg: number | string;
    apg: number | string;
    rpg: number | string;
  };
  all_seasons: SeasonStats[];
  [key: string]: unknown;
}