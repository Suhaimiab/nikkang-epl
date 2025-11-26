"""
Show raw data structure
"""

import json
from pathlib import Path

data_dir = Path("nikkang_data")

print("=" * 70)
print("RAW DATA INSPECTION")
print("=" * 70)

# Results
print("\n1️⃣ RESULTS.JSON")
results_file = data_dir / "results.json"
if results_file.exists():
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Type: {type(data).__name__}")
    print(f"Content:\n{json.dumps(data, indent=2)[:2000]}")
else:
    print("NOT FOUND")

# Predictions
print("\n" + "=" * 70)
print("\n2️⃣ PREDICTIONS.JSON")
predictions_file = data_dir / "predictions.json"
if predictions_file.exists():
    with open(predictions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Type: {type(data).__name__}")
    # Show first user's predictions
    if isinstance(data, dict):
        first_key = list(data.keys())[0] if data else None
        if first_key:
            print(f"First user ID: {first_key}")
            print(f"First user predictions: {json.dumps(data[first_key], indent=2)[:1000]}")
    else:
        print(f"Content:\n{json.dumps(data, indent=2)[:1500]}")
else:
    print("NOT FOUND")

# Matches
print("\n" + "=" * 70)
print("\n3️⃣ MATCHES.JSON")
matches_file = data_dir / "matches.json"
if matches_file.exists():
    with open(matches_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Type: {type(data).__name__}")
    print(f"Content:\n{json.dumps(data, indent=2)[:1500]}")
else:
    print("NOT FOUND")

# Participants
print("\n" + "=" * 70)
print("\n4️⃣ PARTICIPANTS.JSON")
participants_file = data_dir / "participants.json"
if participants_file.exists():
    with open(participants_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Type: {type(data).__name__}")
    # Show first few
    if isinstance(data, dict):
        for i, (k, v) in enumerate(data.items()):
            if i >= 3:
                break
            print(f"{k}: {json.dumps(v, indent=2)[:300]}")
    else:
        print(f"Content:\n{json.dumps(data, indent=2)[:1000]}")
else:
    print("NOT FOUND")

print("\n" + "=" * 70)
print("DONE - Please share this output")
print("=" * 70)
