"""
Football API Integration Module
Fetches EPL match fixtures and results from various sources
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import streamlit as st

class FootballAPIIntegration:
    """
    Integrates with football data APIs to fetch fixtures and results
    Supports multiple API providers as fallbacks
    """
    
    def __init__(self):
        self.apis = {
            'football-data': {
                'base_url': 'https://api.football-data.org/v4',
                'epl_id': '2021',  # Premier League ID
                'requires_key': True
            },
            'api-football': {
                'base_url': 'https://v3.football.api-sports.io',
                'epl_id': '39',  # Premier League ID
                'requires_key': True
            },
            'thesportsdb': {
                'base_url': 'https://www.thesportsdb.com/api/v1/json/3',
                'epl_id': '4328',  # Premier League ID
                'requires_key': False
            }
        }
        
        self.team_mappings = self._load_team_mappings()
    
    def _load_team_mappings(self) -> Dict:
        """Load team name mappings for different APIs"""
        return {
            'Manchester United': ['Man United', 'Manchester Utd'],
            'Manchester City': ['Man City', 'Manchester City'],
            'Newcastle United': ['Newcastle', 'Newcastle Utd'],
            'Wolverhampton Wanderers': ['Wolves', 'Wolverhampton'],
            'Brighton & Hove Albion': ['Brighton', 'Brighton & HA'],
            'West Ham United': ['West Ham', 'West Ham Utd'],
            'Nottingham Forest': ['Nottingham Forest', "Nott'm Forest"],
            'Tottenham Hotspur': ['Tottenham', 'Spurs'],
            'Leicester City': ['Leicester', 'Leicester City'],
            'AFC Bournemouth': ['Bournemouth', 'AFC Bournemouth'],
            'Sheffield United': ['Sheffield Utd', 'Sheffield United'],
            'Luton Town': ['Luton', 'Luton Town'],
            'Ipswich Town': ['Ipswich', 'Ipswich Town']
        }
    
    def normalize_team_name(self, api_name: str) -> str:
        """Normalize team names from API to our standard format"""
        # Direct mapping
        for standard, variants in self.team_mappings.items():
            if api_name in variants or api_name == standard:
                return variants[0]  # Return our preferred short name
        
        # If no mapping found, return as is
        return api_name
    
    # ============================================
    # FOOTBALL-DATA.ORG API (Best quality, requires free API key)
    # ============================================
    
    def fetch_fixtures_football_data(self, api_key: str, matchday: int = None) -> Optional[List[Dict]]:
        """
        Fetch fixtures from football-data.org
        Get free API key at: https://www.football-data.org/
        """
        try:
            headers = {'X-Auth-Token': api_key}
            url = f"{self.apis['football-data']['base_url']}/competitions/{self.apis['football-data']['epl_id']}/matches"
            
            params = {'season': '2025'}  # 2025-26 season
            if matchday:
                params['matchday'] = matchday
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_football_data_matches(data.get('matches', []))
            else:
                st.error(f"Football-data.org API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching from football-data.org: {e}")
            return None
    
    def _parse_football_data_matches(self, matches: List) -> List[Dict]:
        """Parse football-data.org match format"""
        parsed = []
        
        for match in matches:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            
            parsed.append({
                'home': self.normalize_team_name(home_team),
                'away': self.normalize_team_name(away_team),
                'date': match.get('utcDate', ''),
                'matchday': match.get('matchday', 0),
                'status': match.get('status', ''),
                'home_score': match['score']['fullTime']['home'],
                'away_score': match['score']['fullTime']['away'],
                'api_id': match.get('id'),
                'source': 'football-data.org'
            })
        
        return parsed
    
    # ============================================
    # API-FOOTBALL (Comprehensive, requires API key)
    # ============================================
    
    def fetch_fixtures_api_football(self, api_key: str, round_number: int = None) -> Optional[List[Dict]]:
        """
        Fetch fixtures from API-Football
        Get API key at: https://www.api-football.com/
        """
        try:
            headers = {
                'x-rapidapi-host': 'v3.football.api-sports.io',
                'x-rapidapi-key': api_key
            }
            
            url = f"{self.apis['api-football']['base_url']}/fixtures"
            
            params = {
                'league': self.apis['api-football']['epl_id'],
                'season': '2025'  # 2025-26 season
            }
            
            if round_number:
                params['round'] = f'Regular Season - {round_number}'
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_api_football_matches(data.get('response', []))
            else:
                st.error(f"API-Football error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching from API-Football: {e}")
            return None
    
    def _parse_api_football_matches(self, matches: List) -> List[Dict]:
        """Parse API-Football match format"""
        parsed = []
        
        for match in matches:
            fixture = match['fixture']
            teams = match['teams']
            goals = match['goals']
            
            parsed.append({
                'home': self.normalize_team_name(teams['home']['name']),
                'away': self.normalize_team_name(teams['away']['name']),
                'date': fixture.get('date', ''),
                'matchday': match['league'].get('round', '').split(' - ')[-1],
                'status': fixture.get('status', {}).get('long', ''),
                'home_score': goals.get('home'),
                'away_score': goals.get('away'),
                'api_id': fixture.get('id'),
                'source': 'api-football.com'
            })
        
        return parsed
    
    # ============================================
    # THESPORTSDB API (Free, no key required)
    # ============================================
    
    def fetch_fixtures_thesportsdb(self, round_number: int = None, season: str = '2025-2026') -> Optional[List[Dict]]:
        """
        Fetch fixtures from TheSportsDB (Free API)
        No API key required
        """
        try:
            url = f"{self.apis['thesportsdb']['base_url']}/eventsround.php"
            params = {
                'id': self.apis['thesportsdb']['epl_id'],
                's': season
            }
            
            if round_number:
                params['r'] = round_number
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                if events:
                    return self._parse_thesportsdb_matches(events)
                else:
                    # Try getting next events if round not available
                    return self.fetch_next_fixtures_thesportsdb()
            else:
                st.error(f"TheSportsDB API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching from TheSportsDB: {e}")
            return None
    
    def fetch_next_fixtures_thesportsdb(self) -> Optional[List[Dict]]:
        """Fetch next upcoming fixtures from TheSportsDB"""
        try:
            url = f"{self.apis['thesportsdb']['base_url']}/eventsnextleague.php"
            params = {'id': self.apis['thesportsdb']['epl_id']}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_thesportsdb_matches(data.get('events', []))
            
            return None
            
        except Exception as e:
            st.error(f"Error fetching next fixtures: {e}")
            return None
    
    def fetch_results_thesportsdb(self, round_number: int = None) -> Optional[List[Dict]]:
        """Fetch completed match results from TheSportsDB"""
        try:
            url = f"{self.apis['thesportsdb']['base_url']}/eventspastleague.php"
            params = {'id': self.apis['thesportsdb']['epl_id']}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                matches = self._parse_thesportsdb_matches(data.get('events', []))
                
                # Filter by round if specified
                if round_number and matches:
                    matches = [m for m in matches if m.get('matchday') == round_number]
                
                return matches
            
            return None
            
        except Exception as e:
            st.error(f"Error fetching results: {e}")
            return None
    
    def _parse_thesportsdb_matches(self, events: List) -> List[Dict]:
        """Parse TheSportsDB event format"""
        parsed = []
        
        for event in events:
            # Skip if not EPL match
            if event.get('strLeague') != 'English Premier League':
                continue
            
            home_score = event.get('intHomeScore')
            away_score = event.get('intAwayScore')
            
            # Convert to int if not None
            if home_score is not None:
                home_score = int(home_score)
            if away_score is not None:
                away_score = int(away_score)
            
            # Extract round number
            round_str = event.get('intRound', '0')
            try:
                matchday = int(round_str) if round_str else 0
            except:
                matchday = 0
            
            parsed.append({
                'home': self.normalize_team_name(event.get('strHomeTeam', '')),
                'away': self.normalize_team_name(event.get('strAwayTeam', '')),
                'date': event.get('dateEvent', ''),
                'time': event.get('strTime', ''),
                'matchday': matchday,
                'status': event.get('strStatus', ''),
                'home_score': home_score,
                'away_score': away_score,
                'api_id': event.get('idEvent'),
                'source': 'thesportsdb.com'
            })
        
        return parsed
    
    # ============================================
    # UNIFIED INTERFACE
    # ============================================
    
    def fetch_fixtures(self, week: int, api_source: str = 'thesportsdb', api_key: str = None) -> Optional[List[Dict]]:
        """
        Unified method to fetch fixtures from any API
        
        Args:
            week: Week/matchday number
            api_source: 'football-data', 'api-football', or 'thesportsdb'
            api_key: API key if required
        """
        if api_source == 'football-data':
            if not api_key:
                st.warning("Football-data.org requires API key")
                return None
            return self.fetch_fixtures_football_data(api_key, week)
        
        elif api_source == 'api-football':
            if not api_key:
                st.warning("API-Football requires API key")
                return None
            return self.fetch_fixtures_api_football(api_key, week)
        
        elif api_source == 'thesportsdb':
            return self.fetch_fixtures_thesportsdb(week)
        
        else:
            st.error(f"Unknown API source: {api_source}")
            return None
    
    def fetch_results(self, week: int, api_source: str = 'thesportsdb', api_key: str = None) -> Optional[List[Dict]]:
        """
        Unified method to fetch results from any API
        """
        if api_source == 'thesportsdb':
            return self.fetch_results_thesportsdb(week)
        
        # For other APIs, use fetch_fixtures and filter completed matches
        fixtures = self.fetch_fixtures(week, api_source, api_key)
        
        if fixtures:
            # Filter only completed matches
            return [f for f in fixtures if f.get('home_score') is not None and f.get('away_score') is not None]
        
        return None
    
    def get_available_weeks(self, api_source: str = 'thesportsdb', api_key: str = None) -> List[int]:
        """Get list of available weeks from API"""
        # For simplicity, return 1-38 for EPL
        return list(range(1, 39))
    
    def format_for_nikkang(self, api_matches: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Format API matches for Nikkang KK application
        
        Returns list of matches in format:
        {
            'home': 'Team Name',
            'away': 'Team Name',
            'gotw': False
        }
        """
        formatted = []
        
        for match in api_matches[:limit]:
            formatted.append({
                'home': match['home'],
                'away': match['away'],
                'gotw': False  # Will be set manually
            })
        
        return formatted
    
    def format_results_for_nikkang(self, api_matches: List[Dict]) -> List[Dict]:
        """
        Format API match results for Nikkang KK application
        
        Returns list of results in format:
        {
            'home': score,
            'away': score
        }
        """
        results = []
        
        for match in api_matches:
            if match.get('home_score') is not None and match.get('away_score') is not None:
                results.append({
                    'home': match['home_score'],
                    'away': match['away_score']
                })
        
        return results


# ============================================
# HELPER FUNCTIONS FOR STREAMLIT UI
# ============================================

def display_api_matches(matches: List[Dict], show_scores: bool = True):
    """Display matches in Streamlit UI"""
    if not matches:
        st.info("No matches found")
        return
    
    for idx, match in enumerate(matches, 1):
        col1, col2, col3 = st.columns([3, 1, 3])
        
        with col1:
            st.markdown(f"**{match['home']}**")
        
        with col2:
            if show_scores and match.get('home_score') is not None:
                st.markdown(f"<div style='text-align: center;'>{match['home_score']} - {match['away_score']}</div>", 
                          unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align: center;'>vs</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"**{match['away']}**")
        
        # Show additional info
        info_parts = []
        if match.get('date'):
            info_parts.append(f"📅 {match['date']}")
        if match.get('matchday'):
            info_parts.append(f"Week {match['matchday']}")
        if match.get('source'):
            info_parts.append(f"Source: {match['source']}")
        
        if info_parts:
            st.caption(" | ".join(info_parts))
        
        st.markdown("---")


def test_api_connection(api_source: str = 'thesportsdb', api_key: str = None) -> bool:
    """Test if API is accessible"""
    api = FootballAPIIntegration()
    
    try:
        matches = api.fetch_fixtures(week=1, api_source=api_source, api_key=api_key)
        return matches is not None and len(matches) > 0
    except:
        return False
