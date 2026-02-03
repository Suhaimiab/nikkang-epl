"""
FINAL SOLUTION - Based on Your Actual Setup
Files are in Dropbox, all JSON files present
This replaces utils/data_manager.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
import time
import streamlit as st

class DataManager:
    """
    Dropbox-proof Data Manager
    Handles sync delays and prevents week reversion
    """
    
    def __init__(self, data_dir='nikkang_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # All your files (from screenshot)
        self.settings_file = self.data_dir / "settings.json"
        self.matches_file = self.data_dir / "matches.json"
        self.predictions_file = self.data_dir / "predictions.json"
        self.results_file = self.data_dir / "results.json"
        self.participants_file = self.data_dir / "participants.json"
        self.manual_scores_file = self.data_dir / "manual_scores.json"
        self.round_scores_file = self.data_dir / "round_scores.json"
        self.sync_time_file = self.data_dir / "sync_time.json"
    
    # ========================================================================
    # DROPBOX-SAFE READ/WRITE
    # ========================================================================
    
    def _read_json_safe(self, filepath, retries=5, default=None):
        """Read JSON with retry for Dropbox sync delays"""
        for attempt in range(retries):
            try:
                if filepath.exists():
                    # Wait a moment on retry
                    if attempt > 0:
                        time.sleep(1)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    # File doesn't exist
                    if attempt < retries - 1:
                        time.sleep(0.5)
                        continue
                    return default if default is not None else {}
                    
            except json.JSONDecodeError:
                # File corrupted or mid-sync
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return default if default is not None else {}
            
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return default if default is not None else {}
        
        return default if default is not None else {}
    
    def _write_json_safe(self, filepath, data, verify=True):
        """Write JSON with verification"""
        try:
            # Write
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Verify if requested
            if verify:
                time.sleep(0.5)
                readback = self._read_json_safe(filepath, retries=2)
                
                # For settings, verify current_week
                if 'current_week' in data:
                    return data.get('current_week') == readback.get('current_week')
                
                # For others, just check it's valid
                return readback is not None
            
            return True
            
        except Exception as e:
            return False
    
    # ========================================================================
    # SETTINGS (CRITICAL - Handles week reversion)
    # ========================================================================
    
    def load_settings(self):
        """Load settings"""
        settings = self._read_json_safe(self.settings_file, default={
            "current_week": 1,
            "locked_weeks": [],
            "global_lock": False,
            "deadline_message": "Predictions close at kickoff!",
            "last_updated": datetime.now().isoformat()
        })
        
        # Ensure timestamp
        if 'last_updated' not in settings:
            settings['last_updated'] = datetime.now().isoformat()
        
        return settings
    
    def save_settings(self, settings):
        """Save settings with verification"""
        settings['last_updated'] = datetime.now().isoformat()
        
        success = self._write_json_safe(self.settings_file, settings, verify=True)
        
        # Clear cache on success
        if success:
            if 'settings_cache' in st.session_state:
                del st.session_state['settings_cache']
            if 'current_week_cache' in st.session_state:
                del st.session_state['current_week_cache']
        
        return success
    
    def get_current_week(self, force_reload=False):
        """Get current week - always reload on mobile"""
        # Mobile always gets fresh data
        is_mobile = self._is_mobile()
        
        if is_mobile or force_reload:
            settings = self.load_settings()
            current_week = settings.get('current_week', 1)
            st.session_state['current_week_cache'] = current_week
            return current_week
        
        # Desktop can use cache
        if 'current_week_cache' in st.session_state:
            return st.session_state['current_week_cache']
        
        settings = self.load_settings()
        current_week = settings.get('current_week', 1)
        st.session_state['current_week_cache'] = current_week
        
        return current_week
    
    def set_current_week(self, week_number):
        """Set current week with verification"""
        week_number = int(week_number)
        
        settings = self.load_settings()
        settings['current_week'] = week_number
        
        # Save
        success = self.save_settings(settings)
        
        if not success:
            return False
        
        # Wait for Dropbox
        time.sleep(2)
        
        # Verify
        verification = self.load_settings()
        verified = verification.get('current_week') == week_number
        
        if verified:
            # Clear all caches
            st.cache_data.clear()
        
        return verified
    
    # ========================================================================
    # OTHER DATA FILES
    # ========================================================================
    
    def load_matches(self):
        return self._read_json_safe(self.matches_file, default={})
    
    def save_matches(self, matches):
        return self._write_json_safe(self.matches_file, matches, verify=False)
    
    def load_predictions(self):
        return self._read_json_safe(self.predictions_file, default={})
    
    def save_predictions(self, predictions):
        return self._write_json_safe(self.predictions_file, predictions, verify=False)
    
    def load_results(self):
        return self._read_json_safe(self.results_file, default={})
    
    def save_results(self, results):
        return self._write_json_safe(self.results_file, results, verify=False)
    
    def load_participants(self):
        return self._read_json_safe(self.participants_file, default=[])
    
    def save_participants(self, participants):
        return self._write_json_safe(self.participants_file, participants, verify=False)
    
    def load_manual_scores(self):
        return self._read_json_safe(self.manual_scores_file, default={})
    
    def save_manual_scores(self, scores):
        return self._write_json_safe(self.manual_scores_file, scores, verify=False)
    
    def load_round_scores(self):
        return self._read_json_safe(self.round_scores_file, default={})
    
    def save_round_scores(self, scores):
        return self._write_json_safe(self.round_scores_file, scores, verify=False)
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
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
    
    def get_week_matches(self, week):
        """Alias for get_matches_by_week"""
        return self.get_matches_by_week(week)
    
    def get_weeks(self):
        """Get list of available weeks"""
        matches = self.load_matches()
        weeks = [int(w) for w in matches.keys() if w.isdigit()]
        return sorted(weeks)
    
    def get_all_participants(self):
        """Get all participants as list of dicts"""
        data = self.load_participants()
        
        # Handle both dict and list formats
        if isinstance(data, dict):
            # Convert dict format to list
            return list(data.values())
        elif isinstance(data, list):
            # Already a list
            return data
        else:
            # Unknown format
            return []
    
    def get_participant_by_id(self, participant_id):
        """Get specific participant"""
        participants = self.load_participants()
        for p in participants:
            if isinstance(p, dict) and p.get('id') == participant_id:
                return p
        return None
    
    def get_participant(self, participant_id):
        """Alias for get_participant_by_id"""
        return self.get_participant_by_id(participant_id)
    
    def calculate_points(self, pred_home, pred_away, res_home, res_away, is_gotw=False, week=None):
        """
        Calculate points for a prediction
        
        Args:
            pred_home: Predicted home score
            pred_away: Predicted away score
            res_home: Actual home score
            res_away: Actual away score
            is_gotw: Is this Game of the Week?
            week: Week number (38 gets bonus points)
        
        Returns:
            int: Points earned
        """
        return calculate_points(pred_home, pred_away, res_home, res_away, is_gotw, week)
    
    def get_participant_predictions(self, participant_id, week):
        """Get predictions for a specific participant and week"""
        return get_participant_predictions(participant_id, week)
    
    def add_match(self, week, home, away, date, time, gotw=False, api_id=None, **kwargs):
        """Add a match to a specific week"""
        return add_match(week, home, away, date, time, gotw, api_id, **kwargs)
    
    def _is_mobile(self):
        """Detect mobile device"""
        try:
            user_agent = st.context.headers.get('user-agent', '').lower()
            return 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent
        except:
            return False
    
    def clear_all_caches(self):
        """Clear all caches"""
        st.cache_data.clear()
        st.cache_resource.clear()
        
        cache_keys = [k for k in st.session_state.keys() if 'cache' in k.lower()]
        for key in cache_keys:
            del st.session_state[key]
        
        return True

# ============================================================================
# STANDALONE HELPER FUNCTIONS (for backwards compatibility)
# ============================================================================

def load_manual_scores():
    """Standalone function for loading manual scores"""
    dm = DataManager()
    return dm.load_manual_scores()

def get_participant_manual_scores(participant_id, manual_scores_data=None):
    """Get manual scores for a specific participant"""
    if manual_scores_data is None:
        manual_scores_data = load_manual_scores()
    
    total_points = 0
    total_kk = 0
    
    # Iterate through weeks in manual scores
    for week_str, week_data in manual_scores_data.items():
        if not isinstance(week_data, dict):
            continue
        
        participant_data = week_data.get(participant_id, {})
        if isinstance(participant_data, dict):
            total_points += participant_data.get('points', 0)
            total_kk += participant_data.get('kk', 0)
    
    return {'points': total_points, 'kk': total_kk}

def calculate_points(pred_home, pred_away, res_home, res_away, is_gotw=False, week=None):
    """
    Calculate points for a prediction
    
    Args:
        pred_home: Predicted home score
        pred_away: Predicted away score
        res_home: Actual home score
        res_away: Actual away score
        is_gotw: Is this Game of the Week?
        week: Week number (38 gets bonus points)
    
    Returns:
        int: Points earned
    """
    try:
        pred_h = int(pred_home)
        pred_a = int(pred_away)
        res_h = int(res_home)
        res_a = int(res_away)
    except (ValueError, TypeError):
        return 0
    
    # Check for exact score
    if pred_h == res_h and pred_a == res_a:
        # Week 38 finale - all matches get bonus
        if week == 38:
            return 10
        # GOTW bonus
        elif is_gotw:
            return 10
        # Regular exact score
        else:
            return 6
    
    # Check for correct result
    pred_result = 'H' if pred_h > pred_a else ('A' if pred_a > pred_h else 'D')
    res_result = 'H' if res_h > res_a else ('A' if res_a > res_h else 'D')
    
    if pred_result == res_result:
        # Week 38 finale - all matches get bonus
        if week == 38:
            return 5
        # GOTW bonus
        elif is_gotw:
            return 5
        # Regular correct result
        else:
            return 3
    
    # Wrong prediction
    return 0

# ============================================================================
# MORE STANDALONE FUNCTIONS (backwards compatibility)
# ============================================================================

def load_participants():
    """Standalone function for loading participants"""
    dm = DataManager()
    return dm.load_participants()

def save_participants(participants):
    """Standalone function for saving participants"""
    dm = DataManager()
    return dm.save_participants(participants)

def load_settings():
    """Standalone function for loading settings"""
    dm = DataManager()
    return dm.load_settings()

def save_settings(settings):
    """Standalone function for saving settings"""
    dm = DataManager()
    return dm.save_settings(settings)

def load_matches():
    """Standalone function for loading matches"""
    dm = DataManager()
    return dm.load_matches()

def save_matches(matches):
    """Standalone function for saving matches"""
    dm = DataManager()
    return dm.save_matches(matches)

def load_predictions():
    """Standalone function for loading predictions"""
    dm = DataManager()
    return dm.load_predictions()

def save_predictions(predictions):
    """Standalone function for saving predictions"""
    dm = DataManager()
    return dm.save_predictions(predictions)

def load_results():
    """Standalone function for loading results"""
    dm = DataManager()
    return dm.load_results()

def save_results(results):
    """Standalone function for saving results"""
    dm = DataManager()
    return dm.save_results(results)

def get_current_week():
    """Standalone function for getting current week"""
    dm = DataManager()
    return dm.get_current_week()

def set_current_week(week):
    """Standalone function for setting current week"""
    dm = DataManager()
    return dm.set_current_week(week)

def generate_user_id(length=8):
    """Generate a random user ID"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def backup_all_data():
    """Create a backup of all data files"""
    import shutil
    from datetime import datetime
    
    dm = DataManager()
    backup_dir = Path('nikkang_data/backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_subdir = backup_dir / timestamp
    backup_subdir.mkdir(exist_ok=True)
    
    # Backup all JSON files
    data_files = [
        dm.settings_file,
        dm.matches_file,
        dm.predictions_file,
        dm.results_file,
        dm.participants_file,
        dm.manual_scores_file,
        dm.round_scores_file,
        dm.sync_time_file
    ]
    
    for file in data_files:
        if file.exists():
            shutil.copy2(file, backup_subdir / file.name)
    
    return str(backup_subdir)

def get_participant_by_id(participant_id):
    """Standalone function to get participant by ID"""
    dm = DataManager()
    return dm.get_participant_by_id(participant_id)

def get_week_matches(week):
    """Standalone function to get matches for a week (alias for get_matches_by_week)"""
    dm = DataManager()
    return dm.get_matches_by_week(week)

def get_all_matches():
    """Standalone function to get all matches"""
    dm = DataManager()
    return dm.get_all_matches()

def get_weeks():
    """Standalone function to get available weeks"""
    dm = DataManager()
    return dm.get_weeks()

def get_participant_predictions(participant_id, week):
    """Get predictions for a specific participant and week"""
    dm = DataManager()
    predictions = dm.load_predictions()
    week_str = str(week)
    
    if week_str in predictions and participant_id in predictions[week_str]:
        return predictions[week_str][participant_id]
    
    return []


def add_match(week, home, away, date, time, gotw=False, api_id=None, **kwargs):
    """Add a match to a specific week"""
    dm = DataManager()
    matches = dm.load_matches()
    week_str = str(week)
    
    if week_str not in matches:
        matches[week_str] = []
    
    # Generate match ID if not provided
    if api_id:
        match_id = str(api_id)
    else:
        import hashlib
        match_id = hashlib.md5(f"{week}_{home}_{away}_{date}".encode()).hexdigest()[:8]
    
    # Create match object
    new_match = {
        'id': match_id,
        'home': home,
        'away': away,
        'date': date,
        'time': time,
        'gotw': gotw,
        'week': int(week)
    }
    
    # Add any extra kwargs
    new_match.update(kwargs)
    
    # Check if match already exists
    for existing in matches[week_str]:
        if (existing.get('home') == home and 
            existing.get('away') == away and 
            existing.get('date') == date):
            return False, "Match already exists", existing.get('id')
    
    # Add match
    matches[week_str].append(new_match)
    dm.save_matches(matches)
    
    return True, "Match added successfully", match_id
