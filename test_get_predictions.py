"""
Test get_participant_predictions function
"""

import sys
sys.path.insert(0, '.')

from utils.data_manager import DataManager

dm = DataManager()

print("=" * 70)
print("TESTING get_participant_predictions")
print("=" * 70)

# Test with Sumi (Y8PX0JE4) for Week 11
participant_id = "Y8PX0JE4"
week = 11

print(f"\nCalling: dm.get_participant_predictions('{participant_id}', {week})")

result = dm.get_participant_predictions(participant_id, week)

print(f"\nResult type: {type(result).__name__}")
print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
print(f"Result: {result}")

if isinstance(result, list) and result:
    print(f"\n✅ SUCCESS! Got {len(result)} predictions")
    for i, pred in enumerate(result):
        print(f"   Match {i+1}: {pred.get('home', '?')}-{pred.get('away', '?')}")
elif isinstance(result, list) and not result:
    print(f"\n❌ EMPTY LIST returned!")
else:
    print(f"\n⚠️ Unexpected format: {type(result)}")

# Also test without week parameter
print("\n" + "-" * 70)
print(f"\nCalling: dm.get_participant_predictions('{participant_id}') - no week")
result_all = dm.get_participant_predictions(participant_id)
print(f"Result: {result_all}")

print("\n" + "=" * 70)
