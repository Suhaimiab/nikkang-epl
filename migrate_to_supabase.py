"""
Fixed migration script - Handles data validation and cleaning
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.supabase_manager import SupabaseManager

def load_json_data():
    """Load all existing JSON files"""
    data = {}
    data_dir = "nikkang_data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory '{data_dir}' not found!")
        return None
    
    # Load participants
    path = os.path.join(data_dir, "participants.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['participants'] = json.load(f)
        print(f"✅ Loaded {len(data['participants'])} participants")
    else:
        data['participants'] = {}
    
    # Load matches
    path = os.path.join(data_dir, "matches.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['matches'] = json.load(f)
        print(f"✅ Loaded matches for {len(data['matches'])} weeks")
    else:
        data['matches'] = {}
    
    # Load predictions
    path = os.path.join(data_dir, "predictions.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['predictions'] = json.load(f)
        print(f"✅ Loaded predictions for {len(data['predictions'])} weeks")
    else:
        data['predictions'] = {}
    
    # Load results
    path = os.path.join(data_dir, "results.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['results'] = json.load(f)
        print(f"✅ Loaded results for {len(data['results'])} weeks")
    else:
        data['results'] = {}
    
    # Load config
    path = os.path.join(data_dir, "config.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['config'] = json.load(f)
        print(f"✅ Loaded config (current week: {data['config'].get('current_week', 1)})")
    else:
        data['config'] = {'current_week': 1}
        print("⚠️  No config.json found, using defaults")
    
    return data

def validate_and_clean_data(json_data):
    """Validate and clean the data before migration"""
    print("\n🔍 Validating data...")
    
    issues = []
    
    # Get valid participant IDs
    valid_participant_ids = set(json_data['participants'].keys())
    print(f"  Valid participant IDs: {len(valid_participant_ids)}")
    
    # Validate predictions structure
    cleaned_predictions = {}
    for week_str, week_preds in json_data['predictions'].items():
        # Make sure week is numeric
        try:
            week_num = int(week_str)
        except ValueError:
            issues.append(f"⚠️  Skipping invalid week key in predictions: '{week_str}'")
            continue
        
        if not isinstance(week_preds, dict):
            issues.append(f"⚠️  Skipping week {week_str} - predictions not a dict")
            continue
        
        cleaned_week_preds = {}
        for pid, preds in week_preds.items():
            # Check if participant exists
            if pid not in valid_participant_ids:
                issues.append(f"⚠️  Week {week_str}: Unknown participant '{pid}' - skipping")
                continue
            
            # Validate predictions format
            if not isinstance(preds, list):
                issues.append(f"⚠️  Week {week_str}, participant {pid}: predictions not a list - skipping")
                continue
            
            # Validate each prediction
            valid_preds = []
            for idx, pred in enumerate(preds):
                if isinstance(pred, dict) and 'home' in pred and 'away' in pred:
                    try:
                        home = int(pred['home'])
                        away = int(pred['away'])
                        valid_preds.append({'home': home, 'away': away})
                    except (ValueError, TypeError):
                        issues.append(f"⚠️  Week {week_str}, participant {pid}, match {idx}: invalid scores - skipping")
                else:
                    issues.append(f"⚠️  Week {week_str}, participant {pid}, match {idx}: invalid format - skipping")
            
            if valid_preds:
                cleaned_week_preds[pid] = valid_preds
        
        if cleaned_week_preds:
            cleaned_predictions[str(week_num)] = cleaned_week_preds
    
    json_data['predictions'] = cleaned_predictions
    
    # Validate results structure
    cleaned_results = {}
    for week_str, week_results in json_data['results'].items():
        try:
            week_num = int(week_str)
        except ValueError:
            issues.append(f"⚠️  Skipping invalid week key in results: '{week_str}'")
            continue
        
        if not isinstance(week_results, list):
            issues.append(f"⚠️  Skipping week {week_str} results - not a list")
            continue
        
        valid_results = []
        for idx, result in enumerate(week_results):
            if isinstance(result, dict) and 'home' in result and 'away' in result:
                try:
                    home = int(result['home'])
                    away = int(result['away'])
                    valid_results.append({'home': home, 'away': away})
                except (ValueError, TypeError):
                    issues.append(f"⚠️  Week {week_str}, match {idx}: invalid result scores - skipping")
            else:
                issues.append(f"⚠️  Week {week_str}, match {idx}: invalid result format - skipping")
        
        if valid_results:
            cleaned_results[str(week_num)] = valid_results
    
    json_data['results'] = cleaned_results
    
    # Validate matches structure
    cleaned_matches = {}
    for week_str, week_matches in json_data['matches'].items():
        try:
            week_num = int(week_str)
        except ValueError:
            issues.append(f"⚠️  Skipping invalid week key in matches: '{week_str}'")
            continue
        
        if not isinstance(week_matches, list):
            issues.append(f"⚠️  Skipping week {week_str} matches - not a list")
            continue
        
        valid_matches = []
        for idx, match in enumerate(week_matches):
            if isinstance(match, dict) and 'home' in match and 'away' in match:
                valid_matches.append({
                    'home': str(match['home']),
                    'away': str(match['away']),
                    'gotw': bool(match.get('gotw', False))
                })
            else:
                issues.append(f"⚠️  Week {week_str}, match {idx}: invalid match format - skipping")
        
        if valid_matches:
            cleaned_matches[str(week_num)] = valid_matches
    
    json_data['matches'] = cleaned_matches
    
    # Print issues
    if issues:
        print("\n⚠️  Data validation issues found:")
        for issue in issues:
            print(f"  {issue}")
        print()
    else:
        print("  ✅ All data validated successfully!")
    
    return json_data

def migrate_data(json_data):
    """Migrate JSON data to Supabase"""
    print("\n" + "="*60)
    print("Starting migration to Supabase...")
    print("="*60 + "\n")
    
    try:
        db = SupabaseManager()
        
        # Migrate participants
        if json_data['participants']:
            print(f"📤 Migrating {len(json_data['participants'])} participants...")
            success_count = 0
            for pid, participant in json_data['participants'].items():
                participant['id'] = pid
                if db.save_participant(participant):
                    success_count += 1
            print(f"✅ {success_count}/{len(json_data['participants'])} participants migrated\n")
        
        # Migrate matches
        if json_data['matches']:
            print(f"📤 Migrating matches for {len(json_data['matches'])} weeks...")
            success_count = 0
            for week_str, matches in json_data['matches'].items():
                week = int(week_str)
                if db.save_week_matches(week, matches):
                    print(f"  ✅ Week {week}: {len(matches)} matches")
                    success_count += 1
                else:
                    print(f"  ❌ Week {week}: Failed")
            print(f"✅ {success_count}/{len(json_data['matches'])} weeks of matches migrated\n")
        
        # Migrate predictions
        if json_data['predictions']:
            print(f"📤 Migrating predictions for {len(json_data['predictions'])} weeks...")
            total_success = 0
            total_attempts = 0
            for week_str, week_preds in json_data['predictions'].items():
                week = int(week_str)
                week_success = 0
                for pid, preds in week_preds.items():
                    total_attempts += 1
                    if db.save_predictions(pid, week, preds):
                        week_success += 1
                        total_success += 1
                print(f"  ✅ Week {week}: {week_success}/{len(week_preds)} participants")
            print(f"✅ {total_success}/{total_attempts} predictions migrated\n")
        
        # Migrate results
        if json_data['results']:
            print(f"📤 Migrating results for {len(json_data['results'])} weeks...")
            success_count = 0
            for week_str, results in json_data['results'].items():
                week = int(week_str)
                if db.save_week_results(week, results):
                    print(f"  ✅ Week {week}: {len(results)} results")
                    success_count += 1
                else:
                    print(f"  ❌ Week {week}: Failed")
            print(f"✅ {success_count}/{len(json_data['results'])} weeks of results migrated\n")
        
        # Migrate config
        current_week = json_data['config'].get('current_week', 1)
        print(f"📤 Migrating config (current week: {current_week})...")
        db.set_current_week(current_week)
        print("✅ Config migrated\n")
        
        print("="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next steps:")
        print("1. Add Supabase secrets to Streamlit Cloud")
        print("2. Your app will restart automatically")
        print("3. Test sync between mobile and desktop")
        print("4. Enjoy perfect sync! 🎉\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Nikkang KK - Supabase Migration Tool (Fixed)")
    print("="*60 + "\n")
    
    # Check for secrets file
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        print("❌ ERROR: .streamlit/secrets.toml not found!")
        print("\nMake sure the file exists with:")
        print("\n[supabase]")
        print('url = "https://xxxxx.supabase.co"')
        print('key = "your_anon_key_here"')
        sys.exit(1)
    
    print("Loading JSON data...")
    print("-" * 60)
    
    json_data = load_json_data()
    
    if not json_data:
        sys.exit(1)
    
    # Validate and clean data
    json_data = validate_and_clean_data(json_data)
    
    print("\n" + "-" * 60)
    print("\nCleaned Summary:")
    print(f"  📊 Participants: {len(json_data['participants'])}")
    print(f"  ⚽ Weeks with matches: {len(json_data['matches'])}")
    print(f"  🎯 Weeks with predictions: {len(json_data['predictions'])}")
    print(f"  📈 Weeks with results: {len(json_data['results'])}")
    print(f"  📅 Current week: {json_data['config'].get('current_week', 1)}")
    
    print("\n" + "="*60)
    response = input("\n⚠️  Ready to migrate to Supabase? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        success = migrate_data(json_data)
        sys.exit(0 if success else 1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
