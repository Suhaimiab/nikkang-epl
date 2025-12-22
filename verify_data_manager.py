"""
Verify data_manager.py has all required methods
Run this to check if you have the correct version
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_data_manager():
    """Check if data_manager has all required methods"""
    
    print("=" * 60)
    print("DATA MANAGER VERIFICATION")
    print("=" * 60)
    
    try:
        from utils.data_manager import DataManager
        print("✅ Successfully imported DataManager")
    except ImportError as e:
        print(f"❌ Failed to import DataManager: {e}")
        return False
    
    # List of required methods
    required_methods = [
        'save_participant_predictions',
        'save_prediction',
        'save_predictions',
        'get_participant_predictions',
        'get_predictions',
        'load_predictions',
        'generate_user_id',
        'add_participant',
        'get_participant',
        'save_match_result',
        'get_match_result'
    ]
    
    dm = DataManager()
    missing_methods = []
    found_methods = []
    
    print(f"\nChecking {len(required_methods)} required methods...")
    print("-" * 60)
    
    for method_name in required_methods:
        if hasattr(dm, method_name):
            found_methods.append(method_name)
            print(f"✅ {method_name}")
        else:
            missing_methods.append(method_name)
            print(f"❌ {method_name} - MISSING!")
    
    print("-" * 60)
    print(f"\nResults:")
    print(f"  Found: {len(found_methods)}/{len(required_methods)}")
    print(f"  Missing: {len(missing_methods)}")
    
    if missing_methods:
        print(f"\n❌ MISSING METHODS:")
        for method in missing_methods:
            print(f"   - {method}")
        print(f"\n⚠️  You need to replace data_manager.py with the updated version!")
        return False
    else:
        print(f"\n✅ All required methods found!")
        print(f"✅ data_manager.py is up to date!")
        
        # Check timezone imports
        try:
            from utils.timezone_utils import get_malaysian_datetime_str
            print(f"✅ Timezone utilities imported successfully!")
            print(f"   Current Malaysian time: {get_malaysian_datetime_str()}")
        except ImportError:
            print(f"⚠️  Timezone utilities not found - make sure timezone_utils.py is in utils/")
        
        return True
    
    print("=" * 60)

if __name__ == "__main__":
    success = verify_data_manager()
    
    if not success:
        print("\n" + "=" * 60)
        print("ACTION REQUIRED:")
        print("=" * 60)
        print("1. Download the updated data_manager.py")
        print("2. Copy to: utils/data_manager.py")
        print("3. Run this script again to verify")
        print("4. Restart Streamlit")
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print("Your data_manager.py is up to date.")
        print("You can now run your Streamlit app.")
        sys.exit(0)
