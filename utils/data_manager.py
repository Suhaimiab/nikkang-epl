"""
Data Manager - Customized for Nikkang KK EPL
Works with matches format: {"1": [{home, away, gotw}, ...], "2": [...]}
"""

import json
import os
from pathlib import Path
from datetime import datetime
from utils.timezone_utils import get_malaysian_datetime_str, get_malaysian_time
from typing import Dict, List, Optional, Any
import random
import string

DATA_DIR = "nikkang_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

PARTICIPANTS_FILE = os.path.join(DATA_DIR, "participants.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
PREDICTIONS_FILE = os.path.join(DATA_DIR, "predictions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")

def generate_user_id(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class DataManager:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        for f, d in [(PARTICIPANTS_FILE, {}), (MATCHES_FILE, {}), (PREDICTIONS_FILE, {}), (RESULTS_FILE, {})]:
            if not os.path.exists(f):
                with open(f, 'w') as fp:
                    json.dump(d, fp)
    
    def _load(self, path, default=None):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default or {}
    
    def _save(self, path, data):
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            return False
    
    # === MATCHES ===
    def load_matches(self):
        return self._load(MATCHES_FILE, {})
    
    def save_matches(self, data):
        return self._save(MATCHES_FILE, data)
    
    def get_matches(self):
        return self.load_matches()
    
    def get_all_matches(self):
        matches = self.load_matches()
        result = []
        for week, week_matches in matches.items():
            if isinstance(week_matches, list):
                for idx, m in enumerate(week_matches):
                    if isinstance(m, dict):
                        result.append({
                            'id': f"{week}_{idx}",
                            'week': int(week),
                            'index': idx,
                            'home_team': m.get('home', ''),
                            'away_team': m.get('away', ''),
                            'home': m.get('home', ''),
                            'away': m.get('away', ''),
                            'game_of_week': m.get('gotw', False),
                            'gotw': m.get('gotw', False),
                            'status': 'scheduled'
                        })
        return result
    
    def get_matches_by_week(self, week):
        matches = self.load_matches()
        week_key = str(week)
        if week_key not in matches:
            return []
        result = []
        week_matches = matches[week_key]
        if isinstance(week_matches, list):
            for idx, m in enumerate(week_matches):
                if isinstance(m, dict):
                    result.append({
                        'id': f"{week}_{idx}",
                        'week': int(week),
                        'index': idx,
                        'home_team': m.get('home', ''),
                        'away_team': m.get('away', ''),
                        'home': m.get('home', ''),
                        'away': m.get('away', ''),
                        'game_of_week': m.get('gotw', False),
                        'gotw': m.get('gotw', False),
                        'status': 'scheduled'
                    })
        return result
    
    def get_week_matches(self, week):
        return self.get_matches_by_week(week)
    
    def get_match(self, match_id):
        return self.get_match_by_id(match_id)
    
    def get_match_by_id(self, match_id):
        try:
            week, idx = match_id.split('_')
            matches = self.get_matches_by_week(int(week))
            for m in matches:
                if m['index'] == int(idx):
                    return m
        except:
            pass
        return None
    
    def get_weeks(self):
        matches = self.load_matches()
        weeks = [int(k) for k in matches.keys() if k.isdigit()]
        return sorted(weeks) if weeks else [1]
    
    def get_all_weeks(self):
        return self.get_weeks()
    
    def get_current_week(self):
        """Get current week from settings.json"""
        settings_file = Path(DATA_DIR) / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                return settings.get("current_week", 1)
            except:
                pass
        # Fallback to first week with matches
        weeks = self.get_weeks()
        return weeks[0] if weeks else 1
    
    def set_current_week(self, week):
        """Set current week in settings.json"""
        settings_file = Path(DATA_DIR) / "settings.json"
        settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
        settings["current_week"] = week
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except:
            return False
    
    def get_game_of_week(self, week):
        for m in self.get_matches_by_week(week):
            if m.get('gotw') or m.get('game_of_week'):
                return m
        return None
    
    def add_match(self, week, home, away, gotw=False, **kw):
        matches = self.load_matches()
        wk = str(week)
        if wk not in matches:
            matches[wk] = []
        match_index = len(matches[wk])
        matches[wk].append({'home': home, 'away': away, 'gotw': gotw})
        match_id = f"{wk}_{match_index}"
        success = self.save_matches(matches)
        return success, "Added" if success else "Failed", match_id
    
    def update_match(self, match_id, **kw):
        try:
            week, idx = match_id.split('_')
            matches = self.load_matches()
            if week in matches and int(idx) < len(matches[week]):
                matches[week][int(idx)].update(kw)
                return self.save_matches(matches)
        except:
            pass
        return False
    
    def set_game_of_week(self, match_id, is_gotw=True):
        return self.update_match(match_id, gotw=is_gotw)
    
    # === PARTICIPANTS ===
    def load_participants(self):
        return self._load(PARTICIPANTS_FILE, {})
    
    def save_participants(self, data):
        return self._save(PARTICIPANTS_FILE, data)
    
    def get_participants(self):
        return self.load_participants()
    
    def get_all_participants(self):
        p = self.load_participants()
        return list(p.values()) if isinstance(p, dict) else p if isinstance(p, list) else []
    
    def get_participant(self, uid):
        return self.get_participant_by_id(uid)
    
    def get_participant_by_id(self, uid):
        p = self.load_participants()
        if isinstance(p, dict):
            return p.get(uid)
        if isinstance(p, list):
            for x in p:
                if x.get('id') == uid:
                    return x
        return None
    
    def get_display_name(self, participant):
        """
        Get display name for a participant
        Uses display_name if available, otherwise falls back to name
        
        Args:
            participant: Dict with participant data or user_id string
        
        Returns:
            Display name string (nickname or full name)
        """
        if isinstance(participant, str):
            # If passed a user_id, fetch the participant
            participant = self.get_participant_by_id(participant)
            if not participant:
                return "Unknown"
        
        if isinstance(participant, dict):
            # Try display_name first (nickname), then name, then 'Unknown'
            return participant.get('display_name') or participant.get('name') or 'Unknown'
        
        return 'Unknown'
    
    def add_participant(self, name, email="", phone="", team="", status="active", **kw):
        p = self.load_participants()
        if not isinstance(p, dict):
            p = {}
        uid = generate_user_id()
        while uid in p:
            uid = generate_user_id()
        p[uid] = {'id': uid, 'name': name, 'display_name': kw.get('display_name', name),
                  'email': email, 'phone': phone, 'team': team, 'favorite_team': team,
                  'status': status, 'registration_date': get_malaysian_datetime_str(),
                  'total_points': 0, **kw}
        return (True, "Added", uid) if self.save_participants(p) else (False, "Error", "")
    
    def update_participant(self, uid, **kw):
        p = self.load_participants()
        if isinstance(p, dict) and uid in p:
            p[uid].update(kw)
            return (True, "Updated") if self.save_participants(p) else (False, "Error")
        return False, "Not found"
    
    def delete_participant(self, uid):
        p = self.load_participants()
        if isinstance(p, dict) and uid in p:
            del p[uid]
            return (True, "Deleted") if self.save_participants(p) else (False, "Error")
        return False, "Not found"
    
    def get_active_participants(self):
        return [x for x in self.get_all_participants() if x.get('status', 'active') == 'active']
    
    def generate_user_id(self, length=8):
        """Generate a random alphanumeric user ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    # === PREDICTIONS ===
    def load_predictions(self):
        return self._load(PREDICTIONS_FILE, {})
    
    def save_predictions(self, data):
        return self._save(PREDICTIONS_FILE, data)
    
    def get_predictions(self):
        return self.load_predictions()
    
    def get_user_predictions(self, uid):
        return self.load_predictions().get(uid, {})
    
    def get_prediction(self, uid, mid):
        return self.get_user_prediction(uid, mid)
    
    def get_user_prediction(self, uid, mid):
        return self.get_user_predictions(uid).get(mid)
    
    def save_prediction(self, uid, mid, home, away):
        return self.save_user_prediction(uid, mid, home, away)
    
    def save_user_prediction(self, uid, mid, home, away):
        p = self.load_predictions()
        if uid not in p:
            p[uid] = {}
        p[uid][mid] = {'home_score': home, 'away_score': away, 'predicted_at': get_malaysian_datetime_str()}
        return (True, "Saved") if self.save_predictions(p) else (False, "Error")
    
    def has_predicted(self, uid, mid):
        return self.get_user_prediction(uid, mid) is not None
    
    def get_week_predictions(self, week):
        matches = self.get_matches_by_week(week)
        mids = [m['id'] for m in matches]
        preds = self.load_predictions()
        result = {}
        for uid, up in preds.items():
            uw = {m: up[m] for m in mids if m in up}
            if uw:
                result[uid] = uw
        return result
    
    def get_match_predictions(self, mid):
        preds = self.load_predictions()
        return {uid: up[mid] for uid, up in preds.items() if mid in up}
    
    def get_participant_predictions(self, user_id, week=None):
        """
        Get predictions for a participant, optionally filtered by week
        
        YOUR DATA FORMAT:
        {
            "11": {
                "Y8PX0JE4": [
                    {"home": 2, "away": 1},
                    ...
                ]
            }
        }
        """
        all_preds = self.load_predictions()
        
        if week is not None:
            # Get predictions for specific week
            week_str = str(week)
            week_preds = all_preds.get(week_str, {})
            return week_preds.get(user_id, [])
        
        # Get all predictions for this user across all weeks
        user_all_preds = {}
        for week_key, week_data in all_preds.items():
            if week_key.isdigit():  # Only process week keys
                if isinstance(week_data, dict) and user_id in week_data:
                    user_all_preds[week_key] = week_data[user_id]
        
        return user_all_preds
    
    def save_participant_predictions(self, user_id, week, predictions):
        """
        Save multiple predictions for a participant in bulk
        
        YOUR DATA FORMAT:
        {
            "11": {
                "Y8PX0JE4": [
                    {"home": 2, "away": 1},
                    {"home": 0, "away": 0},
                    ...
                ]
            }
        }
        
        Args:
            user_id: User/participant ID (e.g., "Y8PX0JE4")
            week: Week number (e.g., 11)
            predictions: List of [{'home': X, 'away': Y}, ...]
        
        Returns:
            tuple: (success, message)
        """
        all_preds = self.load_predictions()
        
        # Convert week to string (JSON keys are strings)
        week_str = str(week)
        
        # Initialize week if not exists
        if week_str not in all_preds:
            all_preds[week_str] = {}
        
        # Handle list format (from predictions page)
        if isinstance(predictions, list):
            # Store as list under week -> user_id
            all_preds[week_str][user_id] = predictions
            count = len(predictions)
        elif isinstance(predictions, dict):
            # Convert dict to list format if needed
            pred_list = []
            for match_id, scores in predictions.items():
                if isinstance(scores, dict):
                    pred_list.append({
                        'home': scores.get('home_score', scores.get('home', 0)),
                        'away': scores.get('away_score', scores.get('away', 0))
                    })
            all_preds[week_str][user_id] = pred_list
            count = len(pred_list)
        else:
            return False, "Invalid predictions format"
        
        # Save all predictions
        if self.save_predictions(all_preds):
            return True, f"Saved {count} prediction(s) for Week {week}"
        else:
            return False, "Error saving predictions"
    
    # === RESULTS ===
    def load_results(self):
        return self._load(RESULTS_FILE, {})
    
    def save_results(self, data):
        return self._save(RESULTS_FILE, data)
    
    def get_results(self):
        return self.load_results()
    
    def get_result(self, mid):
        return self.get_match_result(mid)
    
    def get_match_result(self, mid):
        return self.load_results().get(mid)
    
    def save_result(self, mid, home, away, by="admin"):
        return self.save_match_result(mid, home, away, by)
    
    def save_match_result(self, mid, home, away, by="admin"):
        r = self.load_results()
        r[mid] = {'home_score': home, 'away_score': away, 'entered_at': get_malaysian_datetime_str(), 'entered_by': by}
        return (True, "Saved") if self.save_results(r) else (False, "Error")
    
    def get_week_results(self, week):
        matches = self.get_matches_by_week(week)
        results = self.load_results()
        return {m['id']: {**m, **results[m['id']]} for m in matches if m['id'] in results}
    
    def get_completed_weeks(self):
        results = self.load_results()
        weeks = self.get_weeks()
        return [w for w in weeks if all(m['id'] in results for m in self.get_matches_by_week(w))]
    
    def get_last_completed_week(self):
        cw = self.get_completed_weeks()
        return max(cw) if cw else 0
    
    # === LEADERBOARD ===
    def _result_type(self, h, a):
        return 'H' if h > a else ('A' if a > h else 'D')
    
    def calculate_points(self, ph, pa, ah, aa, gotw=False, week=None):
        """
        Calculate points for a prediction
        
        Scoring:
        - Normal: Exact = 6, Correct Result = 3, Wrong = 0
        - GOTW: Exact = 10, Correct Result = 5, Wrong = 0
        - Week 38 FINALE: ALL matches = 10 / 5 / 0
        """
        # Week 38 finale - all matches get bonus points
        is_finale = (week == 38 or week == "38")
        use_bonus = gotw or is_finale
        
        # Check for exact score
        if ph == ah and pa == aa:
            return 10 if use_bonus else 6
        
        # Check for correct result (H/D/A)
        if self._result_type(ph, pa) == self._result_type(ah, aa):
            return 5 if use_bonus else 3
        
        # Wrong prediction
        return 0
    
    def get_leaderboard(self):
        participants = self.get_all_participants()
        predictions = self.load_predictions()
        results = self.load_results()
        all_matches = {m['id']: m for m in self.get_all_matches()}
        
        lb = []
        for p in participants:
            uid = p.get('id', '')
            up = predictions.get(uid, {})
            exact, correct, total, weeks = 0, 0, 0, set()
            
            for mid, pred in up.items():
                m = all_matches.get(mid, {})
                if m.get('week'):
                    weeks.add(m['week'])
                if mid in results:
                    r = results[mid]
                    gotw = m.get('gotw', False)
                    ph, pa = pred.get('home_score', -1), pred.get('away_score', -1)
                    ah, aa = r.get('home_score', -2), r.get('away_score', -2)
                    pts = self.calculate_points(ph, pa, ah, aa, gotw)
                    total += pts
                    if ph == ah and pa == aa:
                        exact += 1
                    elif self._result_type(ph, pa) == self._result_type(ah, aa):
                        correct += 1
            
            lb.append({
                'id': uid, 'name': p.get('name', ''), 'display_name': p.get('display_name', p.get('name', '')),
                'total_points': total, 'exact_scores': exact, 'correct_results': correct,
                'predictions_made': len(up), 'weeks_played': len(weeks),
                'team': p.get('team', p.get('favorite_team', '')), 'status': p.get('status', 'active')
            })
        
        lb.sort(key=lambda x: (x['total_points'], x['exact_scores']), reverse=True)
        for i, e in enumerate(lb, 1):
            e['rank'] = i
        return lb
    
    def calculate_leaderboard(self):
        return self.get_leaderboard()
    
    def recalculate_all_points(self):
        lb = self.get_leaderboard()
        p = self.load_participants()
        if isinstance(p, dict):
            for e in lb:
                if e['id'] in p:
                    p[e['id']]['total_points'] = e['total_points']
        return self.save_participants(p)
    
    def get_user_points_breakdown(self, uid):
        up = self.get_user_predictions(uid)
        results = self.load_results()
        matches = {m['id']: m for m in self.get_all_matches()}
        bd, total = [], 0
        for mid, pred in up.items():
            if mid in results:
                r, m = results[mid], matches.get(mid, {})
                pts = self.calculate_points(pred.get('home_score', 0), pred.get('away_score', 0),
                                           r.get('home_score', 0), r.get('away_score', 0), m.get('gotw', False))
                bd.append({'match_id': mid, 'week': m.get('week', 0),
                          'home_team': m.get('home', ''), 'away_team': m.get('away', ''),
                          'prediction': f"{pred.get('home_score', 0)}-{pred.get('away_score', 0)}",
                          'result': f"{r.get('home_score', 0)}-{r.get('away_score', 0)}",
                          'points': pts, 'gotw': m.get('gotw', False)})
                total += pts
        return {'breakdown': bd, 'total': total}
    
    # === UTILITY ===
    def backup_all_data(self, backup_dir="backups"):
        try:
            import shutil
            os.makedirs(backup_dir, exist_ok=True)
            ts = get_malaysian_time().strftime('%Y%m%d_%H%M%S')
            for f in [PARTICIPANTS_FILE, MATCHES_FILE, PREDICTIONS_FILE, RESULTS_FILE]:
                if os.path.exists(f):
                    shutil.copy2(f, os.path.join(backup_dir, f"{os.path.basename(f)}.{ts}.bak"))
            return True, "Backup created"
        except Exception as e:
            return False, str(e)
    
    def export_all_data(self):
        return {'participants': self.load_participants(), 'matches': self.load_matches(),
                'predictions': self.load_predictions(), 'results': self.load_results(),
                'exported_at': get_malaysian_datetime_str()}
    
    def get_statistics(self):
        return {'total_participants': len(self.get_all_participants()),
                'active_participants': len(self.get_active_participants()),
                'total_matches': len(self.get_all_matches()),
                'completed_matches': len(self.load_results()),
                'total_predictions': sum(len(p) for p in self.load_predictions().values()),
                'total_weeks': len(self.get_weeks())}
    
    def get_total_participants(self): return len(self.get_all_participants())
    def get_total_matches(self): return len(self.get_all_matches())
    def get_total_predictions(self): return sum(len(p) for p in self.load_predictions().values())
    def get_completed_matches(self): return len(self.load_results())

# Standalone functions
def load_participants(): return DataManager().load_participants()
def save_participants(d): return DataManager().save_participants(d)
def load_matches(): return DataManager().load_matches()
def save_matches(d): return DataManager().save_matches(d)
def load_predictions(): return DataManager().load_predictions()
def save_predictions(d): return DataManager().save_predictions(d)
def load_results(): return DataManager().load_results()
def save_results(d): return DataManager().save_results(d)
def get_participant_by_id(uid): return DataManager().get_participant_by_id(uid)
def get_matches_by_week(w): return DataManager().get_matches_by_week(w)
def get_user_predictions(uid): return DataManager().get_user_predictions(uid)
def save_user_prediction(uid, mid, h, a): return DataManager().save_user_prediction(uid, mid, h, a)
def save_participant_predictions(uid, week, preds): return DataManager().save_participant_predictions(uid, week, preds)
def save_match_result(mid, h, a, by="admin"): return DataManager().save_match_result(mid, h, a, by)
def get_match_result(mid): return DataManager().get_match_result(mid)
def backup_all_data(d="backups"): return DataManager().backup_all_data(d)
def export_all_data(): return DataManager().export_all_data()
def add_participant(name, email="", phone="", team="", status="active", **kw): return DataManager().add_participant(name, email, phone, team, status, **kw)
def update_participant(uid, **kw): return DataManager().update_participant(uid, **kw)
def delete_participant(uid): return DataManager().delete_participant(uid)
def generate_user_id(l=8): return DataManager().generate_user_id(l)
def get_participant(uid): return DataManager().get_participant(uid)
def get_display_name(participant): return DataManager().get_display_name(participant)
def get_all_participants(): return DataManager().get_all_participants()
def get_active_participants(): return DataManager().get_active_participants()
def get_match(mid): return DataManager().get_match(mid)
def get_match_by_id(mid): return DataManager().get_match_by_id(mid)
def get_all_matches(): return DataManager().get_all_matches()
def get_week_matches(w): return DataManager().get_week_matches(w)
def add_match(w, h, a, g=False, **kw): return DataManager().add_match(w, h, a, g, **kw)
def update_match(mid, **kw): return DataManager().update_match(mid, **kw)
def get_weeks(): return DataManager().get_weeks()
def get_all_weeks(): return DataManager().get_all_weeks()
def get_current_week(): return DataManager().get_current_week()
def set_current_week(week): return DataManager().set_current_week(week)
def get_game_of_week(w): return DataManager().get_game_of_week(w)
def set_game_of_week(mid, g=True): return DataManager().set_game_of_week(mid, g)
def get_prediction(uid, mid): return DataManager().get_prediction(uid, mid)
def get_user_prediction(uid, mid): return DataManager().get_user_prediction(uid, mid)
def save_prediction(uid, mid, h, a): return DataManager().save_prediction(uid, mid, h, a)
def has_predicted(uid, mid): return DataManager().has_predicted(uid, mid)
def get_week_predictions(w): return DataManager().get_week_predictions(w)
def get_match_predictions(mid): return DataManager().get_match_predictions(mid)
def get_participant_predictions(uid, week=None): return DataManager().get_participant_predictions(uid, week)
def get_result(mid): return DataManager().get_result(mid)
def save_result(mid, h, a, by="admin"): return DataManager().save_result(mid, h, a, by)
def get_week_results(w): return DataManager().get_week_results(w)
def get_completed_weeks(): return DataManager().get_completed_weeks()
def get_last_completed_week(): return DataManager().get_last_completed_week()
def get_leaderboard(): return DataManager().get_leaderboard()
def calculate_leaderboard(): return DataManager().calculate_leaderboard()
def calculate_points(ph, pa, ah, aa, g=False, week=None): return DataManager().calculate_points(ph, pa, ah, aa, g, week)
def recalculate_all_points(): return DataManager().recalculate_all_points()
def get_user_points_breakdown(uid): return DataManager().get_user_points_breakdown(uid)
def get_statistics(): return DataManager().get_statistics()
def get_total_participants(): return DataManager().get_total_participants()
def get_total_matches(): return DataManager().get_total_matches()
def get_total_predictions(): return DataManager().get_total_predictions()
def get_completed_matches(): return DataManager().get_completed_matches()

# Lock/Settings functions
def is_week_locked(week):
    """Check if a week is locked for predictions"""
    import json
    settings_file = Path("nikkang_data/settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            if settings.get("global_lock", False):
                return True
            return week in settings.get("locked_weeks", [])
        except:
            pass
    return False

def is_predictions_locked():
    """Check if predictions are globally locked"""
    import json
    settings_file = Path("nikkang_data/settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            return settings.get("global_lock", False)
        except:
            pass
    return False

def get_deadline_message():
    """Get the deadline message for users"""
    import json
    settings_file = Path("nikkang_data/settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            return settings.get("deadline_message", "Predictions close at kickoff!")
        except:
            pass
    return "Predictions close at kickoff!"

# =============================================================================
# MANUAL SCORES FUNCTIONS
# =============================================================================
MANUAL_SCORES_FILE = "nikkang_data/manual_scores.json"

def load_manual_scores():
    """Load manually entered scores for historical weeks"""
    try:
        if os.path.exists(MANUAL_SCORES_FILE):
            with open(MANUAL_SCORES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_manual_scores(data):
    """Save manual scores to file"""
    try:
        os.makedirs(os.path.dirname(MANUAL_SCORES_FILE), exist_ok=True)
        with open(MANUAL_SCORES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def get_participant_manual_scores(user_id, week=None):
    """Get manual scores for a participant, optionally for specific week"""
    manual_scores = load_manual_scores()
    
    if week is not None:
        week_key = str(week)
        week_data = manual_scores.get(week_key, {})
        return week_data.get(user_id, {'points': 0, 'kk': 0})
    
    # Return all weeks for this participant
    result = {}
    for week_key, week_data in manual_scores.items():
        if user_id in week_data:
            result[week_key] = week_data[user_id]
    return result

def get_total_manual_scores(user_id, weeks=None):
    """Get total manual scores for a participant across specified weeks"""
    manual_scores = load_manual_scores()
    
    total_points = 0
    total_kk = 0
    
    for week_key, week_data in manual_scores.items():
        # If weeks specified, only count those
        if weeks is not None:
            if int(week_key) not in weeks:
                continue
        
        if user_id in week_data:
            total_points += week_data[user_id].get('points', 0)
            total_kk += week_data[user_id].get('kk', 0)
    
    return {'points': total_points, 'kk': total_kk}

