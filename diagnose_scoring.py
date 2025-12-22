"""
Diagnose Scoring Issues
Data folder: nikkang_data
Handles both list and dict formats
"""

import json
from pathlib import Path

data_dir = Path("nikkang_data")

print("=" * 70)
print("SCORING DIAGNOSTIC")
print("=" * 70)

# 1. Check Results
print("\n1️⃣ RESULTS (match scores entered)")
results_file = data_dir / "results.json"
results = {}
results_raw = None

if results_file.exists():
    with open(results_file, 'r') as f:
        results_raw = json.load(f)
    
    print(f"   Raw type: {type(results_raw).__name__}")
    
    # Handle different formats
    if isinstance(results_raw, dict):
        # Check if it's {match_id: {scores}} or {match_id: [list]}
        first_key = list(results_raw.keys())[0] if results_raw else None
        first_val = results_raw.get(first_key) if first_key else None
        
        if isinstance(first_val, dict):
            results = results_raw
            print(f"   Format: Dict of dicts ✓")
        elif isinstance(first_val, list):
            print(f"   Format: Dict of lists")
            # Try to convert
            for mid, val in results_raw.items():
                if len(val) >= 2:
                    results[mid] = {'home_score': val[0], 'away_score': val[1]}
        else:
            results = results_raw
    elif isinstance(results_raw, list):
        print(f"   Format: List")
        # Convert list to dict
        for item in results_raw:
            if isinstance(item, dict):
                mid = item.get('match_id', item.get('id', ''))
                if mid:
                    results[mid] = item
    
    print(f"   Total results: {len(results)}")
    
    if results:
        print("   Sample results:")
        for mid, r in list(results.items())[:5]:
            if isinstance(r, dict):
                hs = r.get('home_score', r.get('home', '?'))
                aws = r.get('away_score', r.get('away', '?'))
                print(f"      {mid}: {hs}-{aws}")
            else:
                print(f"      {mid}: {r}")
    
    # Show raw structure
    print(f"\n   Raw data sample:")
    print(f"   {str(results_raw)[:500]}")
else:
    print("   ❌ results.json NOT FOUND!")

# 2. Check Predictions
print("\n2️⃣ PREDICTIONS")
predictions_file = data_dir / "predictions.json"
predictions = {}

if predictions_file.exists():
    with open(predictions_file, 'r') as f:
        predictions_raw = json.load(f)
    
    print(f"   Raw type: {type(predictions_raw).__name__}")
    
    if isinstance(predictions_raw, dict):
        predictions = predictions_raw
    elif isinstance(predictions_raw, list):
        # Convert list format
        for item in predictions_raw:
            if isinstance(item, dict):
                uid = item.get('user_id', item.get('participant_id', ''))
                if uid:
                    if uid not in predictions:
                        predictions[uid] = {}
                    mid = item.get('match_id', '')
                    if mid:
                        predictions[uid][mid] = item
    
    print(f"   Total users with predictions: {len(predictions)}")
    
    if predictions:
        for uid, user_preds in list(predictions.items())[:2]:
            print(f"\n   User {uid}:")
            print(f"      Total predictions: {len(user_preds)}")
            for mid, pred in list(user_preds.items())[:3]:
                if isinstance(pred, dict):
                    hs = pred.get('home_score', pred.get('home', '?'))
                    aws = pred.get('away_score', pred.get('away', '?'))
                    print(f"      {mid}: {hs}-{aws}")
                else:
                    print(f"      {mid}: {pred}")
else:
    print("   ❌ predictions.json NOT FOUND!")

# 3. Check Matches
print("\n3️⃣ MATCHES (fixtures)")
matches_file = data_dir / "matches.json"
matches_list = []
matches_dict = {}

if matches_file.exists():
    with open(matches_file, 'r') as f:
        matches_raw = json.load(f)
    
    print(f"   Raw type: {type(matches_raw).__name__}")
    
    if isinstance(matches_raw, dict):
        matches_dict = matches_raw
        matches_list = list(matches_raw.values())
    elif isinstance(matches_raw, list):
        matches_list = matches_raw
        for m in matches_list:
            mid = m.get('id', '')
            if mid:
                matches_dict[mid] = m
    
    print(f"   Total matches: {len(matches_list)}")
    
    if matches_list:
        print("   Sample matches:")
        for m in matches_list[:5]:
            mid = m.get('id', '?')
            home = m.get('home', m.get('home_team', '?'))
            away = m.get('away', m.get('away_team', '?'))
            week = m.get('week', m.get('matchday', '?'))
            gotw = "🌟 GOTW" if m.get('gotw', False) else ""
            print(f"      {mid}: Week {week} - {home} vs {away} {gotw}")
else:
    print("   ❌ matches.json NOT FOUND!")

# 4. Check Participants
print("\n4️⃣ PARTICIPANTS")
participants_file = data_dir / "participants.json"
participants = {}

if participants_file.exists():
    with open(participants_file, 'r') as f:
        participants_raw = json.load(f)
    
    if isinstance(participants_raw, dict):
        participants = participants_raw
    elif isinstance(participants_raw, list):
        for p in participants_raw:
            uid = p.get('id', p.get('user_id', ''))
            if uid:
                participants[uid] = p
    
    print(f"   Total participants: {len(participants)}")
    for uid, p in list(participants.items())[:10]:
        if isinstance(p, dict):
            name = p.get('display_name') or p.get('name', 'NO NAME')
        else:
            name = str(p)
        print(f"      {uid}: {name}")
else:
    print("   ❌ participants.json NOT FOUND!")

# 5. Match IDs comparison
print("\n5️⃣ MATCH ID COMPARISON (Critical!)")
if results and predictions:
    result_mids = set(results.keys())
    
    all_pred_mids = set()
    for uid, user_preds in predictions.items():
        if isinstance(user_preds, dict):
            all_pred_mids.update(user_preds.keys())
    
    matching = result_mids & all_pred_mids
    results_only = result_mids - all_pred_mids
    preds_only = all_pred_mids - result_mids
    
    print(f"   Result match IDs: {len(result_mids)}")
    print(f"   Prediction match IDs: {len(all_pred_mids)}")
    print(f"   ✅ Matching IDs: {len(matching)}")
    print(f"   ⚠️ Results only (no predictions): {len(results_only)}")
    print(f"   ⚠️ Predictions only (no results): {len(preds_only)}")
    
    if matching:
        print(f"\n   Sample MATCHING IDs: {list(matching)[:5]}")
    else:
        print(f"\n   ❌ NO MATCHING IDs!")
    
    if results_only:
        print(f"   Sample Results-only IDs: {list(results_only)[:5]}")
    
    if preds_only:
        print(f"   Sample Predictions-only IDs: {list(preds_only)[:5]}")
    
    if len(matching) == 0:
        print("\n   🚨 PROBLEM: No match IDs overlap!")
        print("   Predictions and Results use DIFFERENT match IDs.")

# 6. Manual scoring test
print("\n6️⃣ MANUAL SCORING TEST")
if results and predictions:
    for uid, user_preds in list(predictions.items())[:1]:
        p_name = "Unknown"
        if isinstance(participants, dict) and uid in participants:
            p_data = participants[uid]
            if isinstance(p_data, dict):
                p_name = p_data.get('display_name') or p_data.get('name', uid)
        
        print(f"\n   Testing user: {p_name} ({uid})")
        
        total_pts = 0
        tested = 0
        
        if isinstance(user_preds, dict):
            for mid, pred in list(user_preds.items())[:10]:
                if mid in results:
                    tested += 1
                    result = results[mid]
                    match_info = matches_dict.get(mid, {})
                    is_gotw = match_info.get('gotw', False) if isinstance(match_info, dict) else False
                    
                    if isinstance(pred, dict):
                        pred_home = pred.get('home_score', pred.get('home', '?'))
                        pred_away = pred.get('away_score', pred.get('away', '?'))
                    else:
                        pred_home, pred_away = '?', '?'
                    
                    if isinstance(result, dict):
                        res_home = result.get('home_score', result.get('home', '?'))
                        res_away = result.get('away_score', result.get('away', '?'))
                    else:
                        res_home, res_away = '?', '?'
                    
                    home_team = match_info.get('home', mid) if isinstance(match_info, dict) else mid
                    away_team = match_info.get('away', '') if isinstance(match_info, dict) else ''
                    
                    print(f"\n      {home_team} vs {away_team} {'🌟GOTW' if is_gotw else ''}")
                    print(f"         Prediction: {pred_home}-{pred_away}")
                    print(f"         Result:     {res_home}-{res_away}")
                    
                    # Calculate points
                    try:
                        ph = int(pred_home) if pred_home is not None else -1
                        pa = int(pred_away) if pred_away is not None else -1
                        rh = int(res_home) if res_home is not None else -1
                        ra = int(res_away) if res_away is not None else -1
                        
                        if ph == rh and pa == ra:
                            pts = 10 if is_gotw else 6
                            print(f"         → EXACT MATCH = {pts} pts")
                            total_pts += pts
                        elif (ph > pa and rh > ra) or (ph < pa and rh < ra) or (ph == pa and rh == ra):
                            pts = 5 if is_gotw else 3
                            print(f"         → Correct outcome = {pts} pts")
                            total_pts += pts
                        else:
                            print(f"         → Wrong = 0 pts")
                    except Exception as e:
                        print(f"         → ERROR: {e}")
            
            print(f"\n   📊 TOTAL for {p_name}: {total_pts} pts (from {tested} matches with results)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if results and predictions:
    result_mids = set(results.keys())
    all_pred_mids = set()
    for uid, user_preds in predictions.items():
        if isinstance(user_preds, dict):
            all_pred_mids.update(user_preds.keys())
    matching = result_mids & all_pred_mids
    
    if len(matching) > 0:
        print(f"\n✅ {len(matching)} matches have both predictions AND results")
        print("   Scoring should work!")
    else:
        print("\n❌ NO OVERLAP between prediction IDs and result IDs")
        print("   This is why all scores are 0!")
        print("\n   FIX OPTIONS:")
        print("   1. Re-import results using the SAME match IDs as predictions")
        print("   2. Or manually update results.json to use correct match IDs")
