"""
Check which version of data_manager.py you have
"""

from pathlib import Path

dm_path = Path("utils/data_manager.py")

print("=" * 70)
print("CHECKING DATA_MANAGER VERSION")
print("=" * 70)

if dm_path.exists():
    with open(dm_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the NEW save_participant_predictions function
    if 'week_str = str(week)' in content and 'all_preds[week_str][user_id] = predictions' in content:
        print("\n✅ You have the NEW (correct) data_manager.py")
        print("   Predictions should save as: {'11': {'Y8PX0JE4': [...]}}")
    elif 'all_preds[user_id][match_id]' in content:
        print("\n❌ You have the OLD (incorrect) data_manager.py")
        print("   Predictions are saving as: {'Y8PX0JE4': {...}} - WRONG!")
        print("\n   ➡️ Please replace with the new data_manager.py I provided")
    else:
        print("\n⚠️ Unknown version - checking save_participant_predictions...")
        
        # Find and show the function
        lines = content.split('\n')
        in_func = False
        func_lines = []
        
        for i, line in enumerate(lines):
            if 'def save_participant_predictions' in line:
                in_func = True
            if in_func:
                func_lines.append(f"{i+1}: {line}")
                if len(func_lines) > 1 and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    break
                if len(func_lines) > 30:
                    break
        
        if func_lines:
            print("\nCurrent save_participant_predictions function:")
            print('\n'.join(func_lines[:25]))
else:
    print(f"\n❌ File not found: {dm_path}")

# Also check what's in predictions.json now
print("\n" + "=" * 70)
print("CURRENT PREDICTIONS.JSON")
print("=" * 70)

import json
pred_path = Path("nikkang_data/predictions.json")

if pred_path.exists():
    with open(pred_path, 'r') as f:
        preds = json.load(f)
    
    print(f"\nKeys: {list(preds.keys())}")
    
    # Check Week 1
    if '1' in preds:
        week1 = preds['1']
        print(f"\nWeek '1' type: {type(week1).__name__}")
        if isinstance(week1, dict):
            print(f"Week '1' participants: {list(week1.keys())[:5]}")
            for pid, p in list(week1.items())[:2]:
                print(f"   {pid}: {type(p).__name__} with {len(p) if isinstance(p, list) else '?'} items")
    
    # Check for participant IDs as top-level keys
    real_pids = ['Y8PX0JE4', 'AME76IMV', '6TF6LDIN']
    for pid in real_pids:
        if pid in preds:
            print(f"\n⚠️ {pid} found as TOP-LEVEL key (wrong!): {preds[pid]}")
else:
    print(f"\n❌ File not found: {pred_path}")

print("\n" + "=" * 70)
