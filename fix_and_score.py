"""
FIX PREDICTIONS STRUCTURE AND CALCULATE SCORES
This script will:
1. Show current prediction structure
2. Fix if needed (move participant IDs inside correct week)
3. Calculate scores properly

Run with: python fix_and_score.py
"""

import json
from pathlib import Path
import shutil
from datetime import datetime

data_dir = Path("nikkang_data")

print("=" * 70)
print("NIKKANG DATA FIX & SCORING")
print("=" * 70)

# Backup first
backup_dir = data_dir / "backups"
backup_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in ['predictions.json', 'results.json', 'participants.json']:
    src = data_dir / file
    if src.exists():
        dst = backup_dir / f"{file}.{timestamp}.bak"
        shutil.copy(src, dst)
        print(f"✅ Backed up {file}")

# Load all data
with open(data_dir / "results.json", 'r') as f:
    results = json.load(f)

with open(data_dir / "predictions.json", 'r') as f:
    predictions = json.load(f)

with open(data_dir / "matches.json", 'r') as f:
    matches = json.load(f)

with open(data_dir / "participants.json", 'r') as f:
    participants = json.load(f)

# Get real participant IDs
real_participant_ids = set(participants.keys())
print(f"\n📋 Real participants: {len(real_participant_ids)}")

# Analyze predictions structure
print("\n" + "=" * 70)
print("ANALYZING PREDICTIONS STRUCTURE")
print("=" * 70)

week_keys = []
participant_keys = []

for key in predictions.keys():
    if key.isdigit():
        week_keys.append(key)
    elif key in real_participant_ids:
        participant_keys.append(key)
    else:
        print(f"   Unknown key: {key}")

print(f"\n   Week keys (correct): {week_keys}")
print(f"   Participant keys (WRONG - should be inside week): {participant_keys}")

# Check if participants have predictions stored at wrong level
needs_fix = len(participant_keys) > 0

if needs_fix:
    print("\n⚠️ PROBLEM DETECTED: Participant IDs are stored as top-level keys!")
    print("   They should be inside week numbers like: {'11': {'Y8PX0JE4': [...]}}")
    
    # For now, let's see what data is there
    for pid in participant_keys[:3]:
        print(f"\n   Checking {pid}:")
        data = predictions.get(pid, {})
        print(f"      Type: {type(data).__name__}")
        print(f"      Content: {str(data)[:200]}")

# Calculate scores with CURRENT structure
print("\n" + "=" * 70)
print("CALCULATING SCORES")
print("=" * 70)

# Convert results to standardized format
# Old format: {"1": [{home:1, away:1}, ...]}
# New format: {"11_0": {home_score:2, away_score:2, ...}}

all_results = {}

for key, value in results.items():
    if isinstance(value, list):
        # Old format - week number with list of results
        week = key
        for idx, res in enumerate(value):
            match_id = f"{week}_{idx}"
            all_results[match_id] = {
                'home_score': res.get('home', res.get('home_score')),
                'away_score': res.get('away', res.get('away_score')),
                'week': week,
                'index': idx
            }
    elif isinstance(value, dict) and 'home_score' in value:
        # New format - already has match ID
        all_results[key] = value
        # Extract week from key like "11_0"
        if '_' in key:
            week, idx = key.split('_', 1)
            all_results[key]['week'] = week
            all_results[key]['index'] = int(idx)

print(f"\n   Total results: {len(all_results)}")

# Build matches lookup
matches_lookup = {}
for week, week_matches in matches.items():
    if isinstance(week_matches, list):
        for idx, m in enumerate(week_matches):
            match_id = f"{week}_{idx}"
            matches_lookup[match_id] = {
                'home': m.get('home', ''),
                'away': m.get('away', ''),
                'gotw': m.get('gotw', False),
                'week': week,
                'index': idx
            }

print(f"   Total matches: {len(matches_lookup)}")

# Convert predictions to standardized format
all_predictions = {}

for key, value in predictions.items():
    if key.isdigit():
        # Week-based format: {"1": {"participant_id": [{home:0, away:1}, ...]}}
        week = key
        if isinstance(value, dict):
            for pid, preds in value.items():
                if pid not in all_predictions:
                    all_predictions[pid] = {}
                if isinstance(preds, list):
                    for idx, pred in enumerate(preds):
                        match_id = f"{week}_{idx}"
                        all_predictions[pid][match_id] = {
                            'home_score': pred.get('home', pred.get('home_score', 0)),
                            'away_score': pred.get('away', pred.get('away_score', 0))
                        }
    elif key in real_participant_ids:
        # Wrong format - participant ID as key
        # Try to figure out which week this belongs to
        pid = key
        if isinstance(value, dict):
            # Check if it contains match data directly
            for sub_key, sub_val in value.items():
                if sub_key.isdigit():
                    # Might be week number
                    week = sub_key
                    if pid not in all_predictions:
                        all_predictions[pid] = {}
                    if isinstance(sub_val, list):
                        for idx, pred in enumerate(sub_val):
                            match_id = f"{week}_{idx}"
                            all_predictions[pid][match_id] = {
                                'home_score': pred.get('home', 0),
                                'away_score': pred.get('away', 0)
                            }

print(f"   Total users with predictions: {len(all_predictions)}")

# Calculate scores
print("\n   Calculating points...")

scores = {}

for pid, user_preds in all_predictions.items():
    scores[pid] = {
        'total': 0,
        'exact': 0,
        'correct': 0,
        'wrong': 0,
        'matches_scored': 0
    }
    
    for match_id, pred in user_preds.items():
        if match_id in all_results:
            result = all_results[match_id]
            match_info = matches_lookup.get(match_id, {})
            is_gotw = match_info.get('gotw', False)
            
            pred_home = int(pred.get('home_score', -1))
            pred_away = int(pred.get('away_score', -1))
            res_home = int(result.get('home_score', -1))
            res_away = int(result.get('away_score', -1))
            
            scores[pid]['matches_scored'] += 1
            
            if pred_home == res_home and pred_away == res_away:
                pts = 10 if is_gotw else 6
                scores[pid]['total'] += pts
                scores[pid]['exact'] += 1
            elif (pred_home > pred_away and res_home > res_away) or \
                 (pred_home < pred_away and res_home < res_away) or \
                 (pred_home == pred_away and res_home == res_away):
                pts = 5 if is_gotw else 3
                scores[pid]['total'] += pts
                scores[pid]['correct'] += 1
            else:
                scores[pid]['wrong'] += 1

# Display results
print("\n" + "=" * 70)
print("FINAL SCORES")
print("=" * 70)

sorted_scores = sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True)

print(f"\n{'Rank':<5} {'Participant':<20} {'Total':<8} {'Exact':<8} {'Correct':<10} {'Wrong':<8} {'Matches':<8}")
print("-" * 75)

for rank, (pid, s) in enumerate(sorted_scores, 1):
    # Get display name
    p_name = pid
    if pid in participants:
        p_name = participants[pid].get('display_name') or participants[pid].get('name', pid)
    elif '_test' in pid:
        p_name = f"Test User {pid[-4:]}"
    
    if len(p_name) > 18:
        p_name = p_name[:15] + "..."
    
    print(f"{rank:<5} {p_name:<20} {s['total']:<8} {s['exact']:<8} {s['correct']:<10} {s['wrong']:<8} {s['matches_scored']:<8}")

# Update participants with scores
print("\n" + "=" * 70)
print("UPDATING PARTICIPANTS")
print("=" * 70)

updated = 0
for pid, s in scores.items():
    if pid in participants:
        participants[pid]['total_points'] = s['total']
        participants[pid]['exact_scores'] = s['exact']
        participants[pid]['correct_outcomes'] = s['correct']
        participants[pid]['wrong'] = s['wrong']
        updated += 1
        p_name = participants[pid].get('display_name', pid)
        print(f"   {p_name}: {s['total']} pts")

# Save updated participants
with open(data_dir / "participants.json", 'w') as f:
    json.dump(participants, f, indent=2)

print(f"\n✅ Updated {updated} participants")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
📊 Data Analysis:
   - Results: {len(all_results)} match results
   - Predictions: {len(all_predictions)} users with predictions
   - Matches: {len(matches_lookup)} fixtures

⚠️ Issues Found:
   - Participant IDs as top-level keys: {len(participant_keys)}
   - Test participants in data: {len([p for p in all_predictions if 'test' in p.lower()])}

✅ Actions Taken:
   - Backed up all JSON files
   - Updated participant scores
   - Saved to participants.json

🔧 To Fix Predictions Structure:
   The predictions are being saved incorrectly by the app.
   Need to fix save_participant_predictions in data_manager.py
""")

print("=" * 70)
print("DONE!")
print("=" * 70)
