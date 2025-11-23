"""
Data management module for Nikkang KK
Handles all data persistence and retrieval
"""

import json
import os
from datetime import datetime
import uuid
from typing import Dict, List, Optional

class DataManager:
    """Centralized data management for the application"""
    
    def __init__(self, data_dir="nikkang_data"):
        self.data_dir = data_dir
        self.participants_file = os.path.join(data_dir, "participants.json")
        self.matches_file = os.path.join(data_dir, "matches.json")
        self.predictions_file = os.path.join(data_dir, "predictions.json")
        self.results_file = os.path.join(data_dir, "results.json")
        self.settings_file = os.path.join(data_dir, "settings.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files with default values"""
        if not os.path.exists(self.participants_file):
            self._save_json(self.participants_file, {})
        
        if not os.path.exists(self.matches_file):
            self._save_json(self.matches_file, {})
        
        if not os.path.exists(self.predictions_file):
            self._save_json(self.predictions_file, {})
        
        if not os.path.exists(self.results_file):
            self._save_json(self.results_file, {})
        
        if not os.path.exists(self.settings_file):
            self._save_json(self.settings_file, {"current_week": 1})
    
    def _load_json(self, filepath: str, default=None) -> Dict:
        """Load JSON data from file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                return default if default is not None else {}
        return default if default is not None else {}
    
    def _save_json(self, filepath: str, data: Dict):
        """Save JSON data to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    # Participant methods
    def load_participants(self) -> Dict:
        """Load all participants"""
        return self._load_json(self.participants_file, {})
    
    def save_participants(self, participants: Dict):
        """Save all participants"""
        self._save_json(self.participants_file, participants)
    
    def add_participant(self, name: str, email: str, phone: str, team: str = "") -> str:
        """Add new participant and return participant ID"""
        participants = self.load_participants()
        
        # Check if email already exists
        for pid, p in participants.items():
            if p.get('email') == email:
                return None
        
        # Generate unique ID
        participant_id = self.generate_participant_id()
        
        # Create participant profile
        participants[participant_id] = {
            'id': participant_id,
            'name': name,
            'email': email,
            'phone': phone,
            'team': team,
            'registered_at': datetime.now().isoformat()
        }
        
        self.save_participants(participants)
        return participant_id
    
    def get_participant(self, participant_id: str) -> Optional[Dict]:
        """Get participant by ID"""
        participants = self.load_participants()
        return participants.get(participant_id)
    
    def get_participant_by_name(self, name: str) -> Optional[Dict]:
        """Get participant by name"""
        participants = self.load_participants()
        for p in participants.values():
            if p['name'] == name:
                return p
        return None
    
    @staticmethod
    def generate_participant_id() -> str:
        """Generate unique participant ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique = uuid.uuid4().hex[:8]
        return f"participant_{timestamp}_{unique}"
    
    # Match methods
    def load_matches(self) -> Dict:
        """Load all matches"""
        return self._load_json(self.matches_file, {})
    
    def save_matches(self, matches: Dict):
        """Save all matches"""
        self._save_json(self.matches_file, matches)
    
    def get_week_matches(self, week: int) -> List:
        """Get matches for a specific week"""
        matches = self.load_matches()
        return matches.get(str(week), [])
    
    def save_week_matches(self, week: int, matches: List):
        """Save matches for a specific week"""
        all_matches = self.load_matches()
        all_matches[str(week)] = matches
        self.save_matches(all_matches)
    
    # Prediction methods
    def load_predictions(self) -> Dict:
        """Load all predictions"""
        return self._load_json(self.predictions_file, {})
    
    def save_predictions(self, predictions: Dict):
        """Save all predictions"""
        self._save_json(self.predictions_file, predictions)
    
    def get_participant_predictions(self, participant_id: str, week: int) -> List:
        """Get predictions for a participant in a specific week"""
        predictions = self.load_predictions()
        week_str = str(week)
        if week_str in predictions and participant_id in predictions[week_str]:
            return predictions[week_str][participant_id]
        return []
    
    def save_participant_predictions(self, participant_id: str, week: int, pred_list: List):
        """Save predictions for a participant"""
        predictions = self.load_predictions()
        week_str = str(week)
        
        if week_str not in predictions:
            predictions[week_str] = {}
        
        predictions[week_str][participant_id] = pred_list
        self.save_predictions(predictions)
    
    # Results methods
    def load_results(self) -> Dict:
        """Load all results"""
        return self._load_json(self.results_file, {})
    
    def save_results(self, results: Dict):
        """Save all results"""
        self._save_json(self.results_file, results)
    
    def get_week_results(self, week: int) -> List:
        """Get results for a specific week"""
        results = self.load_results()
        return results.get(str(week), [])
    
    def save_week_results(self, week: int, results: List):
        """Save results for a specific week"""
        all_results = self.load_results()
        all_results[str(week)] = results
        self.save_results(all_results)
    
    # Settings methods
    def get_current_week(self) -> int:
        """Get current week number"""
        settings = self._load_json(self.settings_file, {"current_week": 1})
        return settings.get("current_week", 1)
    
    def set_current_week(self, week: int):
        """Set current week number"""
        settings = self._load_json(self.settings_file, {})
        settings["current_week"] = week
        self._save_json(self.settings_file, settings)
    
    # Scoring methods
    def calculate_points(self, prediction: Dict, result: Dict, is_gotw: bool = False, is_week38: bool = False) -> int:
        """Calculate points for a single prediction"""
        if not prediction or not result:
            return 0
        
        pred_home = prediction.get('home', 0)
        pred_away = prediction.get('away', 0)
        res_home = result.get('home', 0)
        res_away = result.get('away', 0)
        
        # Exact score
        if pred_home == res_home and pred_away == res_away:
            return 10 if (is_gotw or is_week38) else 6
        
        # Correct result
        pred_result = 'H' if pred_home > pred_away else ('A' if pred_home < pred_away else 'D')
        actual_result = 'H' if res_home > res_away else ('A' if res_home < res_away else 'D')
        
        if pred_result == actual_result:
            return 5 if (is_gotw or is_week38) else 3
        
        return 0
    
    def calculate_leaderboard(self) -> List[Dict]:
        """Calculate complete leaderboard with scores"""
        participants = self.load_participants()
        predictions = self.load_predictions()
        results = self.load_results()
        matches = self.load_matches()
        
        scores = {}
        
        # Initialize scores for all participants
        for pid, p in participants.items():
            scores[pid] = {
                'id': pid,
                'name': p['name'],
                'email': p['email'],
                'team': p.get('team', ''),
                'total_points': 0,
                'exact_scores': 0,
                'correct_results': 0,
                'weeks_played': 0
            }
        
        # Calculate scores for each week
        for week_str, week_predictions in predictions.items():
            week = int(week_str)
            week_results = results.get(week_str, [])
            week_matches = matches.get(week_str, [])
            
            if not week_results or not week_matches:
                continue
            
            is_week38 = (week == 38)
            
            for pid, pred_list in week_predictions.items():
                if pid not in scores:
                    continue
                
                scores[pid]['weeks_played'] += 1
                
                for idx, pred in enumerate(pred_list):
                    if idx >= len(week_results) or idx >= len(week_matches):
                        continue
                    
                    result = week_results[idx]
                    match = week_matches[idx]
                    is_gotw = match.get('gotw', False)
                    
                    points = self.calculate_points(pred, result, is_gotw, is_week38)
                    scores[pid]['total_points'] += points
                    
                    # Track exact scores and correct results
                    if pred.get('home') == result.get('home') and pred.get('away') == result.get('away'):
                        scores[pid]['exact_scores'] += 1
                    elif points > 0:
                        scores[pid]['correct_results'] += 1
        
        # Convert to list and sort by total points
        leaderboard = list(scores.values())
        leaderboard.sort(key=lambda x: (x['total_points'], x['exact_scores'], x['correct_results']), reverse=True)
        
        # Add rank
        for rank, entry in enumerate(leaderboard, 1):
            entry['rank'] = rank
        
        return leaderboard
    
    def get_participant_stats(self, participant_id: str) -> Dict:
        """Get detailed statistics for a participant"""
        leaderboard = self.calculate_leaderboard()
        
        for entry in leaderboard:
            if entry['id'] == participant_id:
                return entry
        
        return None
