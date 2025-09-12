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
};

export type NBAStatsResponse = {
  season_stats?: NBAStatRow[];
};