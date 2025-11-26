"""
Calculate Scores - Works with Nikkang data structure
Week-based matching with position index

Scoring:
- Exact Score: 6 pts (GOTW: 10 pts)
- Correct Outcome: 3 pts (GOTW: 5 pts)
- Wrong: 0 pts
"""

import json
from pathlib import Path

data_dir = Path("nikkang_data")

print("=" * 70)
print("NIKKANG SCORING CALCULATOR")
print("=" * 70)

# Load all data
with open(data_dir / "results.json", 'r') as f:
    results = json.load(f)

with open(data_dir / "predictions.json", 'r') as f:
    predictions = json.load(f)

with open(data_dir / "matches.json", 'r') as f:
    matches = json.load(f)

with open(data_dir / "participants.json", 'r') as f:
    participants = json.load(f)

print(f"\nLoaded: {len(results)} weeks of results")
print(f"Loaded: {len(predictions)} weeks of predictions")
print(f"Loaded: {len(matches)} weeks of matches")
print(f"Loaded: {len(participants)} participants")

# Calculate scores for each participant
print("\n" + "=" * 70)
print("CALCULATING SCORES")
print("=" * 70)

all_scores = {}

for week_num, week_predictions in predictions.items():
    # Skip if not a week number
    if not week_num.isdigit():
        continue
    
    week = week_num
    
    # Get results for this week
    week_results = results.get(week, [])
    if not week_results:
        print(f"\nWeek {week}: No results yet")
        continue
    
    # Handle old format (list) vs new format (dict with 11_0, 11_1, etc.)
    if isinstance(week_results, list):
        results_list = week_results
    else:
        # New format - skip for now
        continue
    
    # Get matches for this week (for GOTW check)
    week_matches = matches.get(week, [])
    
    print(f"\nWeek {week}: {len(results_list)} results, {len(week_matches)} matches")
    
    # Process each participant's predictions for this week
    for participant_id, preds in week_predictions.items():
        if participant_id not in all_scores:
            all_scores[participant_id] = {
                'total': 0, 'exact': 0, 'correct': 0, 'wrong': 0,
                'gotw_exact': 0, 'gotw_correct': 0, 'details': []
            }
        
        if not isinstance(preds, list):
            continue
        
        # Compare each prediction with result
        for idx, pred in enumerate(preds):
            if idx >= len(results_list):
                break
            
            result = results_list[idx]
            match_info = week_matches[idx] if idx < len(week_matches) else {}
            
            is_gotw = match_info.get('gotw', False)
            
            pred_home = pred.get('home', -1)
            pred_away = pred.get('away', -1)
            res_home = result.get('home', -1)
            res_away = result.get('away', -1)
            
            home_team = match_info.get('home', f'Match {idx+1}')
            away_team = match_info.get('away', '')
            
            # Calculate points
            if pred_home == res_home and pred_away == res_away:
                # Exact score
                pts = 10 if is_gotw else 6
                all_scores[participant_id]['total'] += pts
                all_scores[participant_id]['exact'] += 1
                if is_gotw:
                    all_scores[participant_id]['gotw_exact'] += 1
                outcome = 'EXACT'
            elif (pred_home > pred_away and res_home > res_away) or \
                 (pred_home < pred_away and res_home < res_away) or \
                 (pred_home == pred_away and res_home == res_away):
                # Correct outcome
                pts = 5 if is_gotw else 3
                all_scores[participant_id]['total'] += pts
                all_scores[participant_id]['correct'] += 1
                if is_gotw:
                    all_scores[participant_id]['gotw_correct'] += 1
                outcome = 'CORRECT'
            else:
                pts = 0
                all_scores[participant_id]['wrong'] += 1
                outcome = 'WRONG'
            
            # Store detail
            all_scores[participant_id]['details'].append({
                'week': week,
                'match': f"{home_team} vs {away_team}",
                'pred': f"{pred_home}-{pred_away}",
                'result': f"{res_home}-{res_away}",
                'outcome': outcome,
                'pts': pts,
                'gotw': is_gotw
            })

# Display results
print("\n" + "=" * 70)
print("FINAL SCORES")
print("=" * 70)

# Sort by total points
sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]['total'], reverse=True)

print(f"\n{'Rank':<5} {'Participant':<35} {'Total':<8} {'Exact(6)':<10} {'Correct(3)':<12} {'Wrong':<8}")
print("-" * 80)

for rank, (pid, scores) in enumerate(sorted_scores, 1):
    # Get participant name
    p_name = pid
    for uid, p in participants.items():
        # Try to match by various ID formats
        if uid == pid or p.get('id') == pid or f"participant_{pid}" in pid:
            p_name = p.get('display_name') or p.get('name', pid)
            break
    
    # Truncate long names
    if len(p_name) > 30:
        p_name = p_name[:27] + "..."
    
    print(f"{rank:<5} {p_name:<35} {scores['total']:<8} {scores['exact']:<10} {scores['correct']:<12} {scores['wrong']:<8}")

# Show detailed breakdown for top scorer
if sorted_scores:
    print("\n" + "=" * 70)
    print("DETAILED BREAKDOWN - Top Scorer")
    print("=" * 70)
    
    top_pid, top_scores = sorted_scores[0]
    
    # Get name
    top_name = top_pid
    for uid, p in participants.items():
        if uid == top_pid or p.get('id') == top_pid:
            top_name = p.get('display_name') or p.get('name', top_pid)
            break
    
    print(f"\n{top_name}:")
    print(f"Total: {top_scores['total']} pts | Exact: {top_scores['exact']} | Correct: {top_scores['correct']} | Wrong: {top_scores['wrong']}")
    
    print("\nSample predictions:")
    for detail in top_scores['details'][:10]:
        gotw_mark = "🌟" if detail['gotw'] else "  "
        print(f"   {gotw_mark} Week {detail['week']}: {detail['match']}")
        print(f"      Pred: {detail['pred']} | Result: {detail['result']} → {detail['outcome']} ({detail['pts']} pts)")

# Update participants.json with new scores
print("\n" + "=" * 70)
print("UPDATING PARTICIPANT SCORES")
print("=" * 70)

updated = 0
for pid, scores in all_scores.items():
    # Find matching participant
    for uid, p in participants.items():
        if uid == pid or p.get('id') == pid or pid in str(p):
            participants[uid]['total_points'] = scores['total']
            updated += 1
            print(f"   Updated {p.get('display_name', p.get('name', uid))}: {scores['total']} pts")
            break

# Save updated participants
with open(data_dir / "participants.json", 'w') as f:
    json.dump(participants, f, indent=2)

print(f"\n✅ Updated {updated} participants")
print(f"💾 Saved to {data_dir / 'participants.json'}")

print("\n" + "=" * 70)
print("DONE!")
print("=" * 70)
