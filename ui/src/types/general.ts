export type NBAStatRow = {
  Season: string;
  Team: string;
  GP: number;
  PPG: number;
  RPG: number;
  APG: number;
  SPG: number;
  BPG: number;
  TOPG: number;
  FPG: number;

  TS?: number;   // True Shooting %
  FG?: number;   // Field Goal %
  eFG?: number;  // Effective FG %
  "3P"?: number; // Three Point %
  FT?: number;   // Free Throw %
};

export type NBAStatsResponse = {
  season_stats: NBAStatRow[];
};
