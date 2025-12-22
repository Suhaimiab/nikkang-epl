"""
Automatic Late Submission Detection
Adds timestamp to predictions and automatically marks late submissions
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

# This module adds automatic late submission tracking to the data manager

class PredictionTracker:
    """Track prediction submission times and detect late submissions"""
    
    def __init__(self, data_manager):
        self.dm = data_manager
        self.predictions_file = Path("nikkang_data/predictions.json")
        self.settings_file = Path("nikkang_data/settings.json")
    
    def get_deadline(self, week: int) -> datetime:
        """
        Get deadline for a specific week
        Returns datetime object
        """
        # Load settings
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Check if there's a specific deadline for this week
        deadlines = settings.get('deadlines', {})
        week_str = str(week)
        
        if week_str in deadlines:
            # Parse deadline string (format: "2025-12-21 18:00")
            deadline_str = deadlines[week_str]
            try:
                return datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
            except:
                pass
        
        # Default deadline: Friday 6 PM of match week
        # You can customize this logic
        return None
    
    def save_prediction_with_timestamp(self, week: int, participant_id: str, predictions: list):
        """
        Save predictions with timestamp
        Automatically marks as late if after deadline
        """
        # Load existing predictions
        if self.predictions_file.exists():
            with open(self.predictions_file, 'r') as f:
                all_predictions = json.load(f)
        else:
            all_predictions = {}
        
        week_str = str(week)
        
        # Initialize week if needed
        if week_str not in all_predictions:
            all_predictions[week_str] = {}
        
        # Get current time
        submission_time = datetime.now()
        submission_str = submission_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if late
        deadline = self.get_deadline(week)
        is_late = False
        
        if deadline and submission_time > deadline:
            is_late = True
        
        # Add metadata to each prediction
        predictions_with_meta = []
        for pred in predictions:
            pred_with_meta = {
                'home': pred.get('home', 0),
                'away': pred.get('away', 0),
                'submitted_at': submission_str,
                'late': is_late
            }
            predictions_with_meta.append(pred_with_meta)
        
        # Save
        all_predictions[week_str][participant_id] = predictions_with_meta
        
        # Write to file
        self.predictions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.predictions_file, 'w') as f:
            json.dump(all_predictions, f, indent=2)
        
        return is_late, submission_str
    
    def mark_missing_predictions_as_late(self, week: int):
        """
        After deadline passes, mark all missing predictions as late
        Called by admin or cron job
        """
        # Load data
        participants = self.dm.get_all_participants()
        matches = self.dm.load_matches()
        predictions = self.dm.load_predictions()
        
        week_str = str(week)
        week_matches = matches.get(week_str, [])
        
        if not week_matches:
            return 0  # No matches for this week
        
        # Get deadline
        deadline = self.get_deadline(week)
        if not deadline or datetime.now() < deadline:
            return 0  # Deadline hasn't passed yet
        
        # Check each participant
        marked_count = 0
        
        if week_str not in predictions:
            predictions[week_str] = {}
        
        for participant in participants:
            participant_id = participant.get('id')
            
            # Check if predictions exist
            if participant_id not in predictions[week_str]:
                # No predictions - create empty ones marked as late
                empty_predictions = []
                for _ in week_matches:
                    empty_predictions.append({
                        'home': 0,
                        'away': 0,
                        'late': True,
                        'missed': True,  # Flag to indicate no submission at all
                        'marked_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                predictions[week_str][participant_id] = empty_predictions
                marked_count += 1
        
        # Save
        self.dm.save_predictions(predictions)
        
        return marked_count
    
    def get_submission_status(self, week: int, participant_id: str) -> dict:
        """
        Get submission status for a participant in a week
        Returns: {
            'submitted': bool,
            'late': bool,
            'missed': bool,
            'submission_time': str or None,
            'deadline': str or None
        }
        """
        predictions = self.dm.load_predictions()
        week_str = str(week)
        
        # Check if predictions exist
        if week_str not in predictions or participant_id not in predictions[week_str]:
            return {
                'submitted': False,
                'late': False,
                'missed': True,
                'submission_time': None,
                'deadline': self.get_deadline(week).strftime("%Y-%m-%d %H:%M") if self.get_deadline(week) else None
            }
        
        # Get predictions
        preds = predictions[week_str][participant_id]
        
        # Check if any prediction has metadata
        if preds and isinstance(preds[0], dict):
            first_pred = preds[0]
            return {
                'submitted': True,
                'late': first_pred.get('late', False),
                'missed': first_pred.get('missed', False),
                'submission_time': first_pred.get('submitted_at'),
                'deadline': self.get_deadline(week).strftime("%Y-%m-%d %H:%M") if self.get_deadline(week) else None
            }
        
        # Old format predictions (no metadata)
        return {
            'submitted': True,
            'late': False,  # Assume not late if no metadata
            'missed': False,
            'submission_time': 'Unknown',
            'deadline': self.get_deadline(week).strftime("%Y-%m-%d %H:%M") if self.get_deadline(week) else None
        }
