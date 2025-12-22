"""
Test Data Generator for Nikkang KK
Run this to populate the app with sample data for testing
"""

import json
import os
import random
from datetime import datetime

# Data directory
DATA_DIR = "nikkang_data"
os.makedirs(DATA_DIR, exist_ok=True)

# EPL Teams
TEAMS = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
    'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Liverpool',
    'Man City', 'Man United', 'Newcastle', 'Nottingham Forest',
    'Tottenham', 'West Ham', 'Wolves'
]

def generate_test_participants():
    """Generate test participants"""
    participants = {}
    
    test_people = [
        {"name": "Suhaimi Rahman", "email": "suhaimi@pmvectors.com", "phone": "+60123456789", "team": "Liverpool"},
        {"name": "Ahmad Zaki", "email": "ahmad@test.com", "phone": "+60198765432", "team": "Man City"},
        {"name": "Siti Aminah", "email": "siti@test.com", "phone": "+60187654321", "team": "Arsenal"},
        {"name": "Kumar Selvan", "email": "kumar@test.com", "phone": "+60176543210", "team": "Man United"},
        {"name": "Lee Wei Ming", "email": "lee@test.com", "phone": "+60165432109", "team": "Chelsea"},
        {"name": "Nurul Huda", "email": "nurul@test.com", "phone": "+60154321098", "team": "Tottenham"},
        {"name": "David Tan", "email": "david@test.com", "phone": "+60143210987", "team": "Newcastle"},
        {"name": "Fatimah Zahra", "email": "fatimah@test.com", "phone": "+60132109876", "team": "Brighton"},
        {"name": "Raj Kumar", "email": "raj@test.com", "phone": "+60121098765", "team": "Aston Villa"},
        {"name": "Lim Mei Ling", "email": "lim@test.com", "phone": "+60110987654", "team": "West Ham"}
    ]
    
    for idx, person in enumerate(test_people):
        pid = f"participant_20250101000{idx:02d}_test{idx:04d}"
        participants[pid] = {
            'id': pid,
            'name': person['name'],
            'email': person['email'],
            'phone': person['phone'],
            'team': person['team'],
            'registered_at': '2025-01-01T00:00:00'
        }
    
    return participants

def generate_week_matches(week):
    """Generate matches for a week"""
    matches = []
    available_teams = TEAMS.copy()
    random.shuffle(available_teams)
    
    # Generate 10 matches
    for i in range(10):
        if len(available_teams) >= 2:
            home = available_teams.pop()
            away = available_teams.pop()
        else:
            available_teams = [t for t in TEAMS]
            random.shuffle(available_teams)
            home = available_teams.pop()
            away = available_teams.pop()
        
        matches.append({
            'home': home,
            'away': away,
            'gotw': (i == 4)  # Make 5th match the GOTW
        })
    
    return matches

def generate_predictions(participants, week):
    """Generate random predictions for a week"""
    predictions = {}
    
    for pid in participants.keys():
        week_predictions = []
        
        for i in range(10):
            # Random score between 0-4
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)
            
            # Bias towards realistic scores
            if random.random() < 0.3:  # 30% chance of low-scoring
                home_score = min(home_score, 2)
                away_score = min(away_score, 2)
            
            week_predictions.append({
                'home': home_score,
                'away': away_score
            })
        
        predictions[pid] = week_predictions
    
    return predictions

def generate_results(week):
    """Generate random results for a week"""
    results = []
    
    for i in range(10):
        home_score = random.randint(0, 4)
        away_score = random.randint(0, 4)
        
        # Bias towards realistic scores and home advantage
        if random.random() < 0.4:  # 40% chance of low-scoring
            home_score = min(home_score, 2)
            away_score = min(away_score, 1)
        
        if random.random() < 0.3:  # 30% chance of home advantage
            home_score += 1
        
        results.append({
            'home': home_score,
            'away': away_score
        })
    
    return results

def main():
    """Generate all test data"""
    print("=" * 60)
    print("Nikkang KK - Test Data Generator")
    print("=" * 60)
    print()
    
    # Generate participants
    print("Generating test participants...")
    participants = generate_test_participants()
    with open(os.path.join(DATA_DIR, "participants.json"), 'w') as f:
        json.dump(participants, f, indent=2)
    print(f"✅ Created {len(participants)} test participants")
    
    # Generate matches, predictions, and results for first 3 weeks
    print("\nGenerating matches, predictions, and results...")
    
    all_matches = {}
    all_predictions = {}
    all_results = {}
    
    for week in range(1, 4):
        print(f"\n  Week {week}:")
        
        # Matches
        matches = generate_week_matches(week)
        all_matches[str(week)] = matches
        print(f"    ✅ Generated 10 matches")
        
        # Predictions
        predictions = generate_predictions(participants, week)
        all_predictions[str(week)] = predictions
        print(f"    ✅ Generated predictions for {len(participants)} participants")
        
        # Results (for weeks 1 and 2 only)
        if week <= 2:
            results = generate_results(week)
            all_results[str(week)] = results
            print(f"    ✅ Generated 10 match results")
    
    # Save matches
    with open(os.path.join(DATA_DIR, "matches.json"), 'w') as f:
        json.dump(all_matches, f, indent=2)
    
    # Save predictions
    with open(os.path.join(DATA_DIR, "predictions.json"), 'w') as f:
        json.dump(all_predictions, f, indent=2)
    
    # Save results
    with open(os.path.join(DATA_DIR, "results.json"), 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Save settings
    settings = {"current_week": 3}
    with open(os.path.join(DATA_DIR, "settings.json"), 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Test data generation complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • {len(participants)} participants")
    print(f"  • 3 weeks of matches")
    print(f"  • 2 weeks of results (Week 1 & 2 complete)")
    print(f"  • Week 3 has predictions but no results yet")
    print(f"  • Current week set to: 3")
    print()
    print("You can now run the app with:")
    print("  streamlit run app.py")
    print()
    print("Test credentials:")
    print("  • Admin password: admin123")
    print("  • Sample participant: Suhaimi Rahman (suhaimi@pmvectors.com)")
    print()

if __name__ == "__main__":
    main()
