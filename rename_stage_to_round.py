"""
Automated Stage to Round Replacement Script
Run this in your Bola directory to update all files
"""

import os
import re
from pathlib import Path

def replace_in_file(filepath, replacements):
    """Replace text in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply replacements in order (specific to general)
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    # Define replacements (order matters - do specific before general!)
    replacements = [
        # File paths and names
        ('stage_scores.json', 'round_scores.json'),
        ('STAGE_SCORES_FILE', 'ROUND_SCORES_FILE'),
        
        # Function names
        ('load_stage_scores', 'load_round_scores'),
        ('save_stage_scores', 'save_round_scores'),
        ('get_stage_scores', 'get_round_scores'),
        ('get_current_stage', 'get_current_round'),
        ('get_completed_stages', 'get_completed_rounds'),
        ('display_stage_entry', 'display_round_entry'),
        ('display_stage_tab', 'display_round_tab'),
        
        # Variable names (specific keys first)
        ('stage_1_locked', 'round_1_locked'),
        ('stage_2_locked', 'round_2_locked'),
        ('stage_3_locked', 'round_3_locked'),
        ('stage_4_locked', 'round_4_locked'),
        ('"stage_1"', '"round_1"'),
        ('"stage_2"', '"round_2"'),
        ('"stage_3"', '"round_3"'),
        ('"stage_4"', '"round_4"'),
        ("'stage_1'", "'round_1'"),
        ("'stage_2'", "'round_2'"),
        ("'stage_3'", "'round_3'"),
        ("'stage_4'", "'round_4'"),
        
        # Dictionary/variable names
        ('stage_scores', 'round_scores'),
        ('stage_key', 'round_key'),
        ('stage_num', 'round_num'),
        ('stage_info', 'round_info'),
        ('current_stage', 'current_round'),
        ('completed_stages', 'completed_rounds'),
        ('is_locked_stage', 'is_locked_round'),
        
        # Constants
        ('STAGES = {', 'ROUNDS = {'),
        ('STAGES[', 'ROUNDS['),
        ('for stage_num', 'for round_num'),
        ('stage_weeks', 'round_weeks'),
        ('stage_pts', 'round_pts'),
        ('stage_kk', 'round_kk'),
        ('stage_points', 'round_points'),
        ('stage_matches', 'round_matches'),
        
        # CSS classes
        ('.stage-card', '.round-card'),
        ('.stage-progress', '.round-progress'),
        ('.stage-badge', '.round-badge'),
        ('.stage-locked', '.round-locked'),
        ('.stage-active', '.round-active'),
        ('.stage-pending', '.round-pending'),
        ('.current-stage', '.current-round'),
        ('class="stage-', 'class="round-'),
        
        # UI Text (preserve formatting)
        ('📊 Stage Scores', '📊 Round Scores'),
        ('Stage Scores Management', 'Round Scores Management'),
        ('Stage Scores', 'Round Scores'),
        ('Stage Score', 'Round Score'),
        ('Stage Points', 'Round Points'),
        ('Stage Pts', 'Round Pts'),
        ('Stage KK', 'Round KK'),
        ('Stage Winner', 'Round Winner'),
        ('Stage Leaders', 'Round Leaders'),
        ('Stage Champion', 'Round Champion'),
        ('Stage Progress', 'Round Progress'),
        ('Stage 1', 'Round 1'),
        ('Stage 2', 'Round 2'),
        ('Stage 3', 'Round 3'),
        ('Stage 4', 'Round 4'),
        ('STAGE 1', 'ROUND 1'),
        ('STAGE 2', 'ROUND 2'),
        ('STAGE 3', 'ROUND 3'),
        ('STAGE 4', 'ROUND 4'),
        
        # General text (lowercase)
        ('stage breakdown', 'round breakdown'),
        ('stage total', 'round total'),
        ('stage winner', 'round winner'),
        ('stage champion', 'round champion'),
        ('for each stage', 'for each round'),
        ('End of Each Stage', 'End of Each Round'),
        ('completed stages', 'completed rounds'),
        ('completed stage', 'completed round'),
        ('Lock stages', 'Lock rounds'),
        ('Lock stage', 'Lock round'),
        ('the stage', 'the round'),
        ('each stage', 'each round'),
        ('Unlocked stages', 'Unlocked rounds'),
        ('all stages', 'all rounds'),
        ('4 Stages', '4 Rounds'),
        ('4 stages', '4 rounds'),
        ('Stage-by-stage', 'Round-by-round'),
        ('stage-by-stage', 'round-by-round'),
        
        # Plurals
        ('Stages:', 'Rounds:'),
        ('stages', 'rounds'),
        ('Stages', 'Rounds'),
        
        # Emojis with stage
        ('🏆 Stage', '🏆 Round'),
        ('📊 Stage', '📊 Round'),
        ('🎯 Stage', '🎯 Round'),
        
        # Comments
        ('# Stage', '# Round'),
        ('## Stage', '## Round'),
        ('### Stage', '### Round'),
    ]
    
    # Files to process
    files_to_process = [
        'app.py',
        'utils/manual_sync.py',
        'utils/navigation.py',
        'pages/1_Home.py',
        'pages/5_Leaderboard.py',
        'pages/12_Stage_Scores.py',
        'pages/14_WhatsApp.py',
        'pages/16_Guide.py',
        'pages/17_Manual_Scores.py',
    ]
    
    print("=" * 60)
    print("STAGE → ROUND REPLACEMENT SCRIPT")
    print("=" * 60)
    print()
    
    updated_files = []
    
    for filepath in files_to_process:
        if os.path.exists(filepath):
            print(f"Processing: {filepath}")
            if replace_in_file(filepath, replacements):
                print(f"  ✅ Updated")
                updated_files.append(filepath)
            else:
                print(f"  ℹ️  No changes needed")
        else:
            print(f"  ⚠️  File not found: {filepath}")
    
    # Rename JSON file
    print()
    print("Renaming JSON file...")
    old_json = Path('nikkang_data/stage_scores.json')
    new_json = Path('nikkang_data/round_scores.json')
    
    if old_json.exists():
        # Also update the JSON content
        try:
            import json
            with open(old_json, 'r') as f:
                data = json.load(f)
            
            # Rename keys
            if 'stage_1' in data:
                data['round_1'] = data.pop('stage_1')
            if 'stage_2' in data:
                data['round_2'] = data.pop('stage_2')
            if 'stage_3' in data:
                data['round_3'] = data.pop('stage_3')
            if 'stage_4' in data:
                data['round_4'] = data.pop('stage_4')
            if 'stage_1_locked' in data:
                data['round_1_locked'] = data.pop('stage_1_locked')
            if 'stage_2_locked' in data:
                data['round_2_locked'] = data.pop('stage_2_locked')
            if 'stage_3_locked' in data:
                data['round_3_locked'] = data.pop('stage_3_locked')
            if 'stage_4_locked' in data:
                data['round_4_locked'] = data.pop('stage_4_locked')
            
            # Save with new name
            with open(new_json, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Delete old file
            old_json.unlink()
            
            print(f"  ✅ Renamed: {old_json} → {new_json}")
            updated_files.append(str(new_json))
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"  ℹ️  File not found: {old_json}")
    
    # Optionally rename the page file
    old_page = Path('pages/12_Stage_Scores.py')
    new_page = Path('pages/12_Round_Scores.py')
    
    if old_page.exists():
        old_page.rename(new_page)
        print(f"  ✅ Renamed: {old_page} → {new_page}")
        updated_files.append(str(new_page))
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files updated: {len(updated_files)}")
    print()
    print("Updated files:")
    for f in updated_files:
        print(f"  • {f}")
    print()
    print("✅ COMPLETED!")
    print()
    print("Next steps:")
    print("1. Review changes: git diff")
    print("2. Test locally if possible")
    print("3. Commit: git add . && git commit -m 'Rename Stage to Round'")
    print("4. Push: git push")
    print()

if __name__ == '__main__':
    main()
