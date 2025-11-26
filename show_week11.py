"""
Show Week 11 data specifically
"""

import json
from pathlib import Path

data_dir = Path("nikkang_data")

print("=" * 70)
print("WEEK 11 DATA INSPECTION")
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

# Week 11 Results
print("\n1️⃣ WEEK 11 RESULTS")
print("-" * 50)
week11_results = {k: v for k, v in results.items() if k.startswith('11')}
if week11_results:
    for k, v in week11_results.items():
        print(f"   {k}: {v}")
else:
    print("   No Week 11 results found")
    print(f"   Available keys: {list(results.keys())}")

# Week 11 Matches
print("\n2️⃣ WEEK 11 MATCHES")
print("-" * 50)
week11_matches = matches.get('11', matches.get(11, []))
if week11_matches:
    for i, m in enumerate(week11_matches):
        gotw = "🌟 GOTW" if m.get('gotw') else ""
        print(f"   {i}: {m.get('home')} vs {m.get('away')} {gotw}")
else:
    print("   No Week 11 matches found")
    print(f"   Available weeks: {list(matches.keys())}")

# Week 11 Predictions
print("\n3️⃣ WEEK 11 PREDICTIONS")
print("-" * 50)
week11_preds = predictions.get('11', predictions.get(11, {}))
if week11_preds:
    print(f"   Found {len(week11_preds)} participants with Week 11 predictions")
    for pid, preds in list(week11_preds.items())[:3]:
        print(f"\n   Participant: {pid}")
        if isinstance(preds, list):
            for i, p in enumerate(preds[:5]):
                print(f"      Match {i}: {p.get('home', '?')}-{p.get('away', '?')}")
        elif isinstance(preds, dict):
            for mid, p in list(preds.items())[:5]:
                print(f"      {mid}: {p}")
else:
    print("   No Week 11 predictions found")
    print(f"   Available weeks: {list(predictions.keys())}")

# Participants
print("\n4️⃣ REAL PARTICIPANTS (not test)")
print("-" * 50)
for uid, p in participants.items():
    if 'test' not in uid.lower() and 'test' not in p.get('name', '').lower():
        name = p.get('display_name') or p.get('name', uid)
        print(f"   {uid}: {name}")

# Check all prediction keys
print("\n5️⃣ ALL PREDICTION WEEK KEYS")
print("-" * 50)
for week_key in sorted(predictions.keys()):
    week_preds = predictions[week_key]
    if isinstance(week_preds, dict):
        print(f"   Week '{week_key}': {len(week_preds)} participants")
        # Show first participant ID format
        first_pid = list(week_preds.keys())[0] if week_preds else "None"
        print(f"      Sample participant ID: {first_pid[:50]}...")

print("\n" + "=" * 70)
