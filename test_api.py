"""
Test Football-Data.org API for Results
Run this to diagnose API issues
"""

import requests
from datetime import datetime, timedelta

# API Configuration
API_KEY = "789354c1955e403bb10d792e31cc5282"
BASE_URL = "https://api.football-data.org/v4"
COMPETITION_ID = "PL"

def test_api():
    print("=" * 60)
    print("FOOTBALL-DATA.ORG API TEST")
    print("=" * 60)
    
    # Test 1: Basic API connectivity
    print("\n1️⃣ Testing API connectivity...")
    try:
        headers = {"X-Auth-Token": API_KEY}
        response = requests.get(
            f"{BASE_URL}/competitions/{COMPETITION_ID}",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Connected! Competition: {data.get('name', 'Unknown')}")
            print(f"   Current Matchday: {data.get('currentSeason', {}).get('currentMatchday', 'Unknown')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Test 2: Fetch finished matches
    print("\n2️⃣ Fetching finished matches (last 7 days)...")
    try:
        date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "status": "FINISHED",
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        print(f"   Date range: {date_from} to {date_to}")
        
        response = requests.get(
            f"{BASE_URL}/competitions/{COMPETITION_ID}/matches",
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            
            print(f"   ✅ Found {len(matches)} finished matches")
            
            if matches:
                print("\n   📋 Matches found:")
                for m in matches[:5]:  # Show first 5
                    home = m.get("homeTeam", {}).get("name", "?")
                    away = m.get("awayTeam", {}).get("name", "?")
                    score = m.get("score", {}).get("fullTime", {})
                    h_score = score.get("home", "?")
                    a_score = score.get("away", "?")
                    matchday = m.get("matchday", "?")
                    date = m.get("utcDate", "")[:10]
                    
                    print(f"      Week {matchday} | {date} | {home} {h_score}-{a_score} {away}")
                
                if len(matches) > 5:
                    print(f"      ... and {len(matches) - 5} more")
            else:
                print("   ⚠️ No finished matches in this date range")
                print("   Try extending the date range or check if EPL is in season")
        
        elif response.status_code == 429:
            print(f"   ❌ Rate limit exceeded! Wait 1 minute and try again.")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Fetch ALL matches (scheduled and finished)
    print("\n3️⃣ Fetching ALL matches (last 14 days)...")
    try:
        date_from = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        response = requests.get(
            f"{BASE_URL}/competitions/{COMPETITION_ID}/matches",
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            
            # Group by status
            by_status = {}
            for m in matches:
                status = m.get("status", "UNKNOWN")
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(m)
            
            print(f"   ✅ Found {len(matches)} total matches")
            print(f"   By status:")
            for status, mlist in by_status.items():
                print(f"      {status}: {len(mlist)}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    print("""
TROUBLESHOOTING:

If "No finished matches found":
1. Check if EPL season is active
2. Try extending the date range
3. Look at "By status" - matches might be SCHEDULED, not FINISHED

If "Rate limit exceeded":
1. Wait 1 minute
2. Try again
3. Free tier: 10 requests/minute

If connection error:
1. Check internet connection
2. Firewall may be blocking API
3. API might be temporarily down
""")

if __name__ == "__main__":
    test_api()
