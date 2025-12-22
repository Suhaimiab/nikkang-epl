"""
Fix timezone_utils imports across all Python files
Run this script in your project root directory
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix timezone_utils imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: from utils.timezone_utils import ...
        pattern1 = r'from utils.timezone_utils import'
        replacement1 = r'from utils.timezone_utils import'
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: import timezone_utils
        pattern2 = r'^import timezone_utils$'
        replacement2 = r'import utils.timezone_utils as timezone_utils'
        content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
        
        # Check if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, filepath
        return False, None
        
    except Exception as e:
        return False, f"Error in {filepath}: {str(e)}"

def fix_all_imports(root_dir):
    """Fix imports in all Python files in the project"""
    root_path = Path(root_dir)
    fixed_files = []
    errors = []
    
    # Find all Python files
    for py_file in root_path.rglob('*.py'):
        # Skip virtual environment and __pycache__
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        changed, result = fix_imports_in_file(py_file)
        if changed:
            fixed_files.append(result)
        elif result and "Error" in str(result):
            errors.append(result)
    
    return fixed_files, errors

if __name__ == "__main__":
    import sys
    
    # Get project root directory
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # Assume current directory
        project_root = os.getcwd()
    
    print(f"Fixing timezone_utils imports in: {project_root}")
    print("=" * 60)
    
    fixed_files, errors = fix_all_imports(project_root)
    
    if fixed_files:
        print(f"\n✅ Fixed {len(fixed_files)} file(s):")
        for filepath in fixed_files:
            print(f"  - {filepath}")
    else:
        print("\n✅ No files needed fixing")
    
    if errors:
        print(f"\n❌ Errors in {len(errors)} file(s):")
        for error in errors:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print("Done! Restart your Streamlit app.")
