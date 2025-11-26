"""
Check Week 11 predictions
"""

import json
from pathlib import Path

data_dir = Path("nikkang_data")

with open(data_dir / "predictions.json", 'r') as f:
    predictions = json.load(f)

print("=" * 70)
print("WEEK 11 PREDICTIONS")
print("=" * 70)

if '11' in predictions:
    week11 = predictions['11']
    print(f"\nType: {type(week11).__name__}")
    
    if isinstance(week11, dict):
        print(f"Participants: {len(week11)}")
        for pid, preds in week11.items():
            print(f"\n   {pid}:")
            if isinstance(preds, list):
                print(f"      {len(preds)} predictions")
                for i, p in enumerate(preds):
                    print(f"      Match {i+1}: {p.get('home', '?')}-{p.get('away', '?')}")
            else:
                print(f"      {preds}")
    else:
        print(f"Content: {week11}")
else:
    print("\n❌ No Week 11 found!")

# Also check Week 1
print("\n" + "=" * 70)
print("WEEK 1 PREDICTIONS (for comparison)")
print("=" * 70)

if '1' in predictions:
    week1 = predictions['1']
    print(f"\nParticipants in Week 1: {list(week1.keys())[:5]}")
    
    # Check if any real participant IDs are in Week 1
    real_pids = ['Y8PX0JE4', 'AME76IMV', '6TF6LDIN', 'S67F9LGN', '5XEIF377']
    for pid in real_pids:
        if pid in week1:
            print(f"\n✅ {pid} found in Week 1!")
            preds = week1[pid]
            if isinstance(preds, list):
                print(f"   {len(preds)} predictions")
else:
    print("\n❌ No Week 1 found!")

# Load participants for name mapping
with open(data_dir / "participants.json", 'r') as f:
    participants = json.load(f)

print("\n" + "=" * 70)
print("PARTICIPANT MAPPING")
print("=" * 70)
for pid in ['Y8PX0JE4', 'AME76IMV', '6TF6LDIN']:
    if pid in participants:
        name = participants[pid].get('display_name') or participants[pid].get('name')
        print(f"   {pid} = {name}")

print("\n" + "=" * 70)
