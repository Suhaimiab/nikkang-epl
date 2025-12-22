"""
MASTER FIX SCRIPT
Automatically fixes all DataManager imports in your project

Run this script to automatically scan and fix all Python files
that import DataManager class.

Usage:
    cd C:\Users\suhaimi.abdullah\Desktop\Bola
    python fix_all_imports.py
"""

import os
import re
from pathlib import Path

# Project directory
PROJECT_DIR = Path("C:/Users/suhaimi.abdullah/Desktop/Bola")

# Standard imports to replace DataManager
STANDARD_IMPORTS = '''from utils.data_manager import (
    load_participants,
    save_participants,
    generate_user_id,
    get_participant_by_id,
    load_matches,
    save_matches,
    get_matches_by_week,
    load_predictions,
    save_predictions,
    get_user_predictions,
    save_user_prediction,
    load_results,
    save_results,
    save_match_result,
    get_match_result
)'''

# Mapping of old class method calls to new function calls
METHOD_MAPPINGS = [
    (r'dm\.load_participants\(\)', 'load_participants()'),
    (r'dm\.save_participants\(([^)]+)\)', r'save_participants(\1)'),
    (r'dm\.get_participant_by_id\(([^)]+)\)', r'get_participant_by_id(\1)'),
    (r'dm\.load_matches\(\)', 'load_matches()'),
    (r'dm\.save_matches\(([^)]+)\)', r'save_matches(\1)'),
    (r'dm\.get_matches_by_week\(([^)]+)\)', r'get_matches_by_week(\1)'),
    (r'dm\.load_predictions\(\)', 'load_predictions()'),
    (r'dm\.save_predictions\(([^)]+)\)', r'save_predictions(\1)'),
    (r'dm\.get_user_predictions\(([^)]+)\)', r'get_user_predictions(\1)'),
    (r'dm\.save_user_prediction\(([^)]+)\)', r'save_user_prediction(\1)'),
    (r'dm\.load_results\(\)', 'load_results()'),
    (r'dm\.save_results\(([^)]+)\)', r'save_results(\1)'),
    (r'dm\.save_match_result\(([^)]+)\)', r'save_match_result(\1)'),
    (r'dm\.get_match_result\(([^)]+)\)', r'get_match_result(\1)'),
    (r'dm\.generate_user_id\(\)', 'generate_user_id()'),
    (r'dm\.backup_all_data\(\)', 'backup_all_data()'),
    (r'dm\.export_all_data\(\)', 'export_all_data()'),
    # Also handle data_manager.method() pattern
    (r'data_manager\.load_participants\(\)', 'load_participants()'),
    (r'data_manager\.save_participants\(([^)]+)\)', r'save_participants(\1)'),
]

def fix_file(filepath):
    """Fix DataManager imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Check if file has DataManager import
        if 'DataManager' not in content:
            return False, []
        
        # 1. Replace DataManager import
        import_pattern = r'from utils\.data_manager import DataManager'
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, STANDARD_IMPORTS, content)
            changes_made.append("Replaced DataManager import with function imports")
        
        # Also handle: from utils.data_manager import DataManager, other_stuff
        import_pattern2 = r'from utils\.data_manager import DataManager,\s*'
        if re.search(import_pattern2, content):
            content = re.sub(import_pattern2, STANDARD_IMPORTS + '\nfrom utils.data_manager import ', content)
            changes_made.append("Fixed mixed DataManager import")
        
        # 2. Remove class instantiation
        instantiation_patterns = [
            r'dm\s*=\s*DataManager\(\)\n?',
            r'data_manager\s*=\s*DataManager\(\)\n?',
            r'self\.dm\s*=\s*DataManager\(\)\n?',
        ]
        for pattern in instantiation_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                changes_made.append("Removed DataManager instantiation")
        
        # 3. Replace method calls
        for old_pattern, new_pattern in METHOD_MAPPINGS:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes_made.append(f"Replaced {old_pattern[:30]}...")
        
        # 4. Handle self.dm pattern
        self_dm_patterns = [
            (r'self\.dm\.load_participants\(\)', 'load_participants()'),
            (r'self\.dm\.save_participants\(([^)]+)\)', r'save_participants(\1)'),
            (r'self\.dm\.load_matches\(\)', 'load_matches()'),
            (r'self\.dm\.save_matches\(([^)]+)\)', r'save_matches(\1)'),
        ]
        for old_pattern, new_pattern in self_dm_patterns:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes_made.append(f"Replaced self.dm pattern")
        
        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, []
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False, [f"Error: {e}"]

def scan_and_fix_project():
    """Scan entire project and fix all DataManager imports"""
    print("=" * 70)
    print("DATAMANAGER IMPORT FIXER")
    print("=" * 70)
    print()
    
    if not PROJECT_DIR.exists():
        print(f"❌ Project directory not found: {PROJECT_DIR}")
        print("Please update PROJECT_DIR in this script.")
        return
    
    print(f"📁 Scanning: {PROJECT_DIR}")
    print()
    
    # Find all Python files
    python_files = list(PROJECT_DIR.rglob("*.py"))
    
    # Filter out venv and __pycache__
    python_files = [f for f in python_files 
                   if 'venv' not in str(f) 
                   and '__pycache__' not in str(f)
                   and 'fix_all_imports.py' not in str(f)]
    
    print(f"Found {len(python_files)} Python files to scan")
    print()
    
    fixed_files = []
    files_with_datamanager = []
    
    # First pass: identify files with DataManager
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'DataManager' in content:
                files_with_datamanager.append(py_file)
        except:
            pass
    
    if not files_with_datamanager:
        print("✅ No files with DataManager imports found!")
        print("Your project is already fixed.")
        return
    
    print(f"⚠️  Found {len(files_with_datamanager)} files with DataManager:")
    for f in files_with_datamanager:
        rel_path = f.relative_to(PROJECT_DIR)
        print(f"   - {rel_path}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to automatically fix these files? (y/n): ")
    if response.lower() != 'y':
        print("Aborted. No changes made.")
        return
    
    print()
    print("Fixing files...")
    print("-" * 70)
    
    # Second pass: fix files
    for py_file in files_with_datamanager:
        rel_path = py_file.relative_to(PROJECT_DIR)
        
        # Create backup
        backup_path = str(py_file) + '.bak'
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        except:
            pass
        
        # Fix file
        was_fixed, changes = fix_file(py_file)
        
        if was_fixed:
            print(f"✅ Fixed: {rel_path}")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   - {change}")
            fixed_files.append(py_file)
        else:
            print(f"⚠️  Could not auto-fix: {rel_path}")
            print(f"   Please fix manually")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files scanned: {len(python_files)}")
    print(f"Files with DataManager: {len(files_with_datamanager)}")
    print(f"Files fixed: {len(fixed_files)}")
    print()
    
    if len(fixed_files) < len(files_with_datamanager):
        print("⚠️  Some files could not be auto-fixed.")
        print("Please check these files manually:")
        for f in files_with_datamanager:
            if f not in fixed_files:
                print(f"   - {f.relative_to(PROJECT_DIR)}")
    
    print()
    print("✅ Done! Backups created with .bak extension.")
    print()
    print("Next steps:")
    print("1. Restart your Streamlit app: streamlit run app.py")
    print("2. Test each page")
    print("3. Delete .bak files once everything works")

def list_datamanager_files():
    """Just list files with DataManager without fixing"""
    print("=" * 70)
    print("SCANNING FOR DATAMANAGER IMPORTS")
    print("=" * 70)
    print()
    
    if not PROJECT_DIR.exists():
        print(f"❌ Project directory not found: {PROJECT_DIR}")
        return
    
    python_files = list(PROJECT_DIR.rglob("*.py"))
    python_files = [f for f in python_files 
                   if 'venv' not in str(f) 
                   and '__pycache__' not in str(f)]
    
    files_found = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if 'DataManager' in line:
                    files_found.append({
                        'file': py_file.relative_to(PROJECT_DIR),
                        'line': i,
                        'content': line.strip()[:60]
                    })
        except:
            pass
    
    if files_found:
        print(f"Found {len(files_found)} occurrences of DataManager:\n")
        for item in files_found:
            print(f"📄 {item['file']}")
            print(f"   Line {item['line']}: {item['content']}...")
            print()
    else:
        print("✅ No DataManager references found!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_datamanager_files()
    else:
        scan_and_fix_project()
