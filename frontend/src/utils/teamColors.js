// Team accent colors for team-driven UI surfaces.

const DEFAULT_TEAM_COLOR = '#2563eb';

export const TEAM_COLORS = {
  ARI: '#97233F',
  ATL: '#A71930',
  BAL: '#241773',
  BUF: '#00338D',
  CAR: '#0085CA',
  CHI: '#C83803',
  CIN: '#FB4F14',
  CLE: '#311D00',
  DAL: '#003594',
  DEN: '#FB4F14',
  DET: '#0076B6',
  GB: '#203731',
  HOU: '#C8102E',
  IND: '#003DA5',
  JAX: '#006778',
  KC: '#E31837',
  LAC: '#0080C6',
  LAR: '#003594',
  LV: '#000000',
  MIA: '#008E97',
  MIN: '#4F2683',
  NE: '#002244',
  NO: '#9F8958',
  NYG: '#0B2265',
  NYJ: '#125740',
  PHI: '#004C54',
  PIT: '#C28C00',
  SEA: '#69BE28',
  SF: '#AA0000',
  TB: '#D50A0A',
  TEN: '#0C2340',
  WSH: '#5A1414',
};

function normalizeTeamCode(team) {
  if (!team) return '';
  return String(team).trim().toUpperCase();
}

export function getTeamColor(team) {
  return TEAM_COLORS[normalizeTeamCode(team)] || DEFAULT_TEAM_COLOR;
}

export function getTeamColorVars(team) {
  return {
    '--team-color': getTeamColor(team),
  };
}
