"""
One-time migration script - Migrate JSON data to Supabase
Run this LOCALLY before deploying to Streamlit Cloud
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.supabase_manager import SupabaseManager

def load_json_data():
    """Load all existing JSON files"""
    data = {}
    data_dir = "nikkang_data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory '{data_dir}' not found!")
        print("Make sure you're running this from the app directory")
        return None
    
    # Load participants
    path = os.path.join(data_dir, "participants.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['participants'] = json.load(f)
        print(f"✅ Loaded {len(data['participants'])} participants")
    else:
        data['participants'] = {}
        print("⚠️  No participants.json found")
    
    # Load matches
    path = os.path.join(data_dir, "matches.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['matches'] = json.load(f)
        print(f"✅ Loaded matches for {len(data['matches'])} weeks")
    else:
        data['matches'] = {}
        print("⚠️  No matches.json found")
    
    # Load predictions
    path = os.path.join(data_dir, "predictions.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['predictions'] = json.load(f)
        print(f"✅ Loaded predictions for {len(data['predictions'])} weeks")
    else:
        data['predictions'] = {}
        print("⚠️  No predictions.json found")
    
    # Load results
    path = os.path.join(data_dir, "results.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data['results'] = json.load(f)
        print(f"✅ Loaded results for {len(data['results'])} weeks")
    else:
        data['results'] = {}
        print("⚠️  No results.json found")
    
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
            for pid, participant in json_data['participants'].items():
                participant['id'] = pid
                db.save_participant(participant)
            print("✅ Participants migrated\n")
        
        # Migrate matches
        if json_data['matches']:
            print(f"📤 Migrating matches for {len(json_data['matches'])} weeks...")
            for week_str, matches in json_data['matches'].items():
                week = int(week_str)
                db.save_week_matches(week, matches)
                print(f"  ✅ Week {week}: {len(matches)} matches")
            print("✅ All matches migrated\n")
        
        # Migrate predictions
        if json_data['predictions']:
            print(f"📤 Migrating predictions for {len(json_data['predictions'])} weeks...")
            total_preds = 0
            for week_str, week_preds in json_data['predictions'].items():
                week = int(week_str)
                for pid, preds in week_preds.items():
                    db.save_predictions(pid, week, preds)
                    total_preds += 1
                print(f"  ✅ Week {week}: {len(week_preds)} participants")
            print(f"✅ All predictions migrated ({total_preds} total)\n")
        
        # Migrate results
        if json_data['results']:
            print(f"📤 Migrating results for {len(json_data['results'])} weeks...")
            for week_str, results in json_data['results'].items():
                week = int(week_str)
                db.save_week_results(week, results)
                print(f"  ✅ Week {week}: {len(results)} results")
            print("✅ All results migrated\n")
        
        # Migrate config
        current_week = json_data['config'].get('current_week', 1)
        print(f"📤 Migrating config (current week: {current_week})...")
        db.set_current_week(current_week)
        print("✅ Config migrated\n")
        
        print("="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next steps:")
        print("1. Keep your JSON files as backup")
        print("2. Deploy updated code to Streamlit Cloud")
        print("3. Add Supabase secrets to Streamlit Cloud")
        print("4. Test the app - data should sync perfectly!")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPlease check:")
        print("1. Supabase secrets are in .streamlit/secrets.toml")
        print("2. All tables are created in Supabase")
        print("3. Internet connection is working")
        return False

if __name__ == "__main__":
    print("\n")
    print("="*60)
    print("Nikkang KK - Supabase Migration Tool")
    print("="*60)
    print("\n")
    
    # Check for secrets file
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        print("❌ ERROR: .streamlit/secrets.toml not found!")
        print("\nPlease create this file with your Supabase credentials:")
        print("\n[supabase]")
        print('url = "https://xxxxx.supabase.co"')
        print('key = "your_anon_key_here"')
        print("\n")
        sys.exit(1)
    
    print("Loading JSON data...")
    print("-" * 60)
    
    json_data = load_json_data()
    
    if not json_data:
        sys.exit(1)
    
    print("\n" + "-" * 60)
    print("\nSummary:")
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
