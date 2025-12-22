"""
Find where your data files are stored
"""

import os
from pathlib import Path

print("=" * 70)
print("FINDING DATA FILES")
print("=" * 70)

# Current directory
cwd = Path.cwd()
print(f"\nCurrent directory: {cwd}")

# Search for JSON files
print("\n🔍 Searching for JSON files...")

json_files = []
for root, dirs, files in os.walk(cwd):
    # Skip venv and __pycache__
    dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
    
    for file in files:
        if file.endswith('.json'):
            full_path = Path(root) / file
            json_files.append(full_path)

if json_files:
    print(f"\n✅ Found {len(json_files)} JSON files:\n")
    for f in json_files:
        rel_path = f.relative_to(cwd) if f.is_relative_to(cwd) else f
        size = f.stat().st_size
        print(f"   📄 {rel_path} ({size} bytes)")
else:
    print("\n❌ No JSON files found!")

# Look for specific files
print("\n" + "-" * 70)
print("Looking for specific data files...")

target_files = ['participants.json', 'predictions.json', 'results.json', 'matches.json']

for target in target_files:
    found = [f for f in json_files if f.name == target]
    if found:
        print(f"\n✅ {target} found at:")
        for f in found:
            print(f"   {f}")
    else:
        print(f"\n❌ {target} NOT FOUND")

# Check common locations
print("\n" + "-" * 70)
print("Checking common data locations...")

common_paths = [
    cwd / "data",
    cwd / "Data", 
    cwd / "database",
    cwd / "db",
    cwd / "storage",
    cwd / "utils" / "data",
    cwd,
]

for p in common_paths:
    if p.exists() and p.is_dir():
        files = list(p.glob("*.json"))
        if files:
            print(f"\n📁 {p}:")
            for f in files:
                print(f"   - {f.name}")
        else:
            print(f"\n📁 {p}: (no JSON files)")

# Check data_manager.py for data path
print("\n" + "-" * 70)
print("Checking data_manager.py for data path...")

dm_paths = list(cwd.rglob("data_manager.py"))
for dm in dm_paths:
    if 'venv' not in str(dm):
        print(f"\n📄 Found: {dm}")
        with open(dm, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for data_dir or path definitions
            for line in content.split('\n')[:50]:
                if 'data_dir' in line.lower() or 'self.data' in line.lower() or 'Path(' in line:
                    print(f"   {line.strip()}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
