"""
Supabase Data Manager - Cloud Database Integration
Handles all database operations for Nikkang KK EPL Prediction Competition
"""

import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Optional

class SupabaseManager:
    """Manage all database operations with Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.supabase: Client = create_client(url, key)
        except Exception as e:
            st.error(f"Failed to connect to Supabase: {e}")
            st.info("Make sure Supabase secrets are configured in Streamlit Cloud")
            raise
    
    # ============================================
    # PARTICIPANTS
    # ============================================
    
    def save_participant(self, participant_data: Dict) -> bool:
        """Save or update participant"""
        try:
            response = self.supabase.table('participants').upsert(participant_data).execute()
            return True
        except Exception as e:
            st.error(f"Error saving participant: {e}")
            return False
    
    def get_participant(self, participant_id: str) -> Optional[Dict]:
        """Get participant by ID"""
        try:
            response = self.supabase.table('participants').select('*').eq('id', participant_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Error getting participant: {e}")
            return None
    
    def get_all_participants(self) -> Dict[str, Dict]:
        """Get all participants as dictionary"""
        try:
            response = self.supabase.table('participants').select('*').execute()
            participants = {}
            for p in response.data:
                participants[p['id']] = p
            return participants
        except Exception as e:
            st.error(f"Error getting participants: {e}")
            return {}
    
    # ============================================
    # MATCHES
    # ============================================
    
    def save_week_matches(self, week: int, matches: List[Dict]) -> bool:
        """Save matches for a week"""
        try:
            # Delete existing matches for this week
            self.supabase.table('matches').delete().eq('week', week).execute()
            
            # Prepare data
            match_data = []
            for idx, match in enumerate(matches):
                match_data.append({
                    'week': week,
                    'match_index': idx,
                    'home_team': match['home'],
                    'away_team': match['away'],
                    'is_gotw': match.get('gotw', False)
                })
            
            # Insert new matches
            if match_data:
                self.supabase.table('matches').insert(match_data).execute()
            
            return True
        except Exception as e:
            st.error(f"Error saving matches: {e}")
            return False
    
    def get_week_matches(self, week: int) -> List[Dict]:
        """Get matches for a specific week"""
        try:
            response = self.supabase.table('matches').select('*').eq('week', week).order('match_index').execute()
            
            matches = []
            for m in response.data:
                matches.append({
                    'home': m['home_team'],
                    'away': m['away_team'],
                    'gotw': m['is_gotw']
                })
            return matches
        except Exception as e:
            st.error(f"Error getting matches: {e}")
            return []
    
    def get_all_matches(self) -> Dict[str, List[Dict]]:
        """Get all matches grouped by week"""
        try:
            response = self.supabase.table('matches').select('*').order('week, match_index').execute()
            
            matches_by_week = {}
            for m in response.data:
                week_str = str(m['week'])
                if week_str not in matches_by_week:
                    matches_by_week[week_str] = []
                
                matches_by_week[week_str].append({
                    'home': m['home_team'],
                    'away': m['away_team'],
                    'gotw': m['is_gotw']
                })
            
            return matches_by_week
        except Exception as e:
            st.error(f"Error getting all matches: {e}")
            return {}
    
    # ============================================
    # PREDICTIONS
    # ============================================
    
    def save_predictions(self, participant_id: str, week: int, predictions: List[Dict]) -> bool:
        """Save predictions for a participant"""
        try:
            # Delete existing predictions
            self.supabase.table('predictions').delete().eq('participant_id', participant_id).eq('week', week).execute()
            
            # Prepare data
            pred_data = []
            for idx, pred in enumerate(predictions):
                pred_data.append({
                    'participant_id': participant_id,
                    'week': week,
                    'match_index': idx,
                    'home_score': pred['home'],
                    'away_score': pred['away']
                })
            
            # Insert new predictions
            if pred_data:
                self.supabase.table('predictions').insert(pred_data).execute()
            
            return True
        except Exception as e:
            st.error(f"Error saving predictions: {e}")
            return False
    
    def get_participant_predictions(self, participant_id: str, week: int) -> List[Dict]:
        """Get predictions for a participant in a specific week"""
        try:
            response = self.supabase.table('predictions').select('*').eq('participant_id', participant_id).eq('week', week).order('match_index').execute()
            
            predictions = []
            for p in response.data:
                predictions.append({
                    'home': p['home_score'],
                    'away': p['away_score']
                })
            return predictions
        except Exception as e:
            st.error(f"Error getting predictions: {e}")
            return []
    
    def get_all_predictions(self) -> Dict:
        """Get all predictions grouped by week and participant"""
        try:
            response = self.supabase.table('predictions').select('*').order('week, participant_id, match_index').execute()
            
            predictions_by_week = {}
            for p in response.data:
                week_str = str(p['week'])
                if week_str not in predictions_by_week:
                    predictions_by_week[week_str] = {}
                
                if p['participant_id'] not in predictions_by_week[week_str]:
                    predictions_by_week[week_str][p['participant_id']] = []
                
                predictions_by_week[week_str][p['participant_id']].append({
                    'home': p['home_score'],
                    'away': p['away_score']
                })
            
            return predictions_by_week
        except Exception as e:
            st.error(f"Error getting all predictions: {e}")
            return {}
    
    # ============================================
    # RESULTS
    # ============================================
    
    def save_week_results(self, week: int, results: List[Dict]) -> bool:
        """Save results for a week"""
        try:
            # Delete existing results
            self.supabase.table('results').delete().eq('week', week).execute()
            
            # Prepare data
            result_data = []
            for idx, result in enumerate(results):
                result_data.append({
                    'week': week,
                    'match_index': idx,
                    'home_score': result['home'],
                    'away_score': result['away']
                })
            
            # Insert new results
            if result_data:
                self.supabase.table('results').insert(result_data).execute()
            
            return True
        except Exception as e:
            st.error(f"Error saving results: {e}")
            return False
    
    def get_week_results(self, week: int) -> List[Dict]:
        """Get results for a specific week"""
        try:
            response = self.supabase.table('results').select('*').eq('week', week).order('match_index').execute()
            
            results = []
            for r in response.data:
                results.append({
                    'home': r['home_score'],
                    'away': r['away_score']
                })
            return results
        except Exception as e:
            st.error(f"Error getting results: {e}")
            return []
    
    def get_all_results(self) -> Dict[str, List[Dict]]:
        """Get all results grouped by week"""
        try:
            response = self.supabase.table('results').select('*').order('week, match_index').execute()
            
            results_by_week = {}
            for r in response.data:
                week_str = str(r['week'])
                if week_str not in results_by_week:
                    results_by_week[week_str] = []
                
                results_by_week[week_str].append({
                    'home': r['home_score'],
                    'away': r['away_score']
                })
            
            return results_by_week
        except Exception as e:
            st.error(f"Error getting all results: {e}")
            return {}
    
    # ============================================
    # CONFIG
    # ============================================
    
    def get_current_week(self) -> int:
        """Get current week from config"""
        try:
            response = self.supabase.table('app_config').select('value').eq('key', 'current_week').execute()
            if response.data:
                return int(response.data[0]['value'])
            return 1
        except Exception as e:
            st.error(f"Error getting current week: {e}")
            return 1
    
    def set_current_week(self, week: int) -> bool:
        """Set current week in config"""
        try:
            self.supabase.table('app_config').upsert({
                'key': 'current_week',
                'value': str(week)
            }).execute()
            return True
        except Exception as e:
            st.error(f"Error setting current week: {e}")
            return False
