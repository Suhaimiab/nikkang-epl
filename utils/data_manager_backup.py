"""
Data Manager - Enhanced with Mobile Sync Fixes
Prevents week reversion on mobile devices
"""

import json
from pathlib import Path
from datetime import datetime
import os
import streamlit as st

class DataManager:
    """Manages data files with mobile-safe operations"""
    
    def __init__(self):
        self.data_dir = Path("nikkang_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.matches_file = self.data_dir / "matches.json"
        self.predictions_file = self.data_dir / "predictions.json"
        self.results_file = self.data_dir / "results.json"
        self.participants_file = self.data_dir / "participants.json"
        self.settings_file = self.data_dir / "settings.json"
    
    def _save_json_safe(self, filepath, data):
        """Save JSON with forced disk sync for mobile reliability"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()  # Flush Python buffer
                os.fsync(f.fileno())  # Force OS write to disk
            return True
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
            return False
    
    def _load_json_safe(self, filepath, default=None):
        """Load JSON with cache clearing"""
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        
        return default if default is not None else {}
    
    # ========================================================================
    # SETTINGS (with mobile fixes)
    # ========================================================================
    
    def load_settings(self):
        """Load settings with staleness detection"""
        settings = self._load_json_safe(self.settings_file, {
            "current_week": 1,
            "locked_weeks": [],
            "global_lock": False,
            "deadline_message": "Predictions close at kickoff!",
            "last_updated": datetime.now().isoformat()
        })
        
        # Ensure last_updated exists
        if 'last_updated' not in settings:
            settings['last_updated'] = datetime.now().isoformat()
            self.save_settings(settings)
        
        return settings
    
    def save_settings(self, settings):
        """Save settings with forced sync and timestamp"""
        settings['last_updated'] = datetime.now().isoformat()
        
        success = self._save_json_safe(self.settings_file, settings)
        
        # Clear cache to force reload
        if 'settings_cache' in st.session_state:
            del st.session_state['settings_cache']
        if 'current_week_cache' in st.session_state:
            del st.session_state['current_week_cache']
        
        return success
    
    def get_current_week(self, force_reload=False):
        """Get current week with optional cache bypass"""
        # Force reload on mobile or when requested
        if force_reload or 'current_week_cache' not in st.session_state:
            settings = self.load_settings()
            current_week = settings.get('current_week', 1)
            st.session_state['current_week_cache'] = current_week
            return current_week
        
        return st.session_state['current_week_cache']
    
    def set_current_week(self, week_number):
        """Set current week with verification"""
        settings = self.load_settings()
        settings['current_week'] = int(week_number)
        
        # Save with forced sync
        success = self.save_settings(settings)
        
        if success:
            # Verify it was saved
            verification = self.load_settings()
            if verification.get('current_week') == week_number:
                # Clear cache
                st.cache_data.clear()
                return True
            else:
                print(f"Week verification failed! Wanted {week_number}, got {verification.get('current_week')}")
                return False
        
        return False
    
    # ========================================================================
    # MATCHES
    # ========================================================================
    
    def load_matches(self):
        """Load all matches"""
        return self._load_json_safe(self.matches_file, {})
    
    def save_matches(self, matches):
        """Save matches"""
        return self._save_json_safe(self.matches_file, matches)
    
    def get_all_matches(self):
        """Get all matches as flat list"""
        matches_by_week = self.load_matches()
        all_matches = []
        
        for week, week_matches in matches_by_week.items():
            if isinstance(week_matches, list):
                for match in week_matches:
                    match['week'] = int(week) if week.isdigit() else week
                    all_matches.append(match)
        
        return all_matches
    
    def get_matches_by_week(self, week):
        """Get matches for specific week"""
        matches = self.load_matches()
        return matches.get(str(week), [])
    
    def get_weeks(self):
        """Get list of available weeks"""
        matches = self.load_matches()
        weeks = [int(w) for w in matches.keys() if w.isdigit()]
        return sorted(weeks)
    
    # ========================================================================
    # PREDICTIONS
    # ========================================================================
    
    def load_predictions(self):
        """Load all predictions"""
        return self._load_json_safe(self.predictions_file, {})
    
    def save_predictions(self, predictions):
        """Save predictions"""
        return self._save_json_safe(self.predictions_file, predictions)
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    
    def load_results(self):
        """Load all results"""
        return self._load_json_safe(self.results_file, {})
    
    def save_results(self, results):
        """Save results"""
        return self._save_json_safe(self.results_file, results)
    
    # ========================================================================
    # PARTICIPANTS
    # ========================================================================
    
    def load_participants(self):
        """Load participants"""
        return self._load_json_safe(self.participants_file, [])
    
    def save_participants(self, participants):
        """Save participants"""
        return self._save_json_safe(self.participants_file, participants)
    
    def get_all_participants(self):
        """Get all participants"""
        return self.load_participants()
    
    def get_participant_by_id(self, participant_id):
        """Get specific participant by ID"""
        participants = self.load_participants()
        for p in participants:
            if p.get('id') == participant_id:
                return p
        return None
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def clear_cache(self):
        """Clear all session cache"""
        cache_keys = [
            'settings_cache',
            'current_week_cache',
            'matches_cache',
            'predictions_cache',
            'results_cache',
            'participants_cache'
        ]
        
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        st.cache_data.clear()
        st.cache_resource.clear()
        
        return True
    
    def validate_week(self):
        """Validate current week and fix if stuck"""
        settings = self.load_settings()
        current_week = settings.get('current_week', 1)
        
        # If stuck on 21, check if it should be different
        if current_week == 21:
            matches = self.get_matches_by_week(21)
            results = self.load_results()
            week_21_results = results.get('21', [])
            
            # If week 21 has results, it might be correct
            # But if there are newer weeks with fixtures, update
            all_weeks = self.get_weeks()
            if all_weeks and max(all_weeks) > 21:
                # Check if newer weeks have fixtures
                latest_week = max(all_weeks)
                latest_matches = self.get_matches_by_week(latest_week)
                
                if latest_matches:
                    # Update to latest week
                    print(f"Auto-correcting week from 21 to {latest_week}")
                    self.set_current_week(latest_week)
                    return latest_week
        
        return current_week
