"""
Configuration and styling utilities
"""

import streamlit as st

def setup_page():
    """Setup page configuration"""
    st.set_page_config(
        page_title="Nikkang KK - EPL Predictions",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: #c41e3a;
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
            color: white;
        }
        
        /* Match card styling */
        .match-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
        }
        
        .match-card.gotw {
            background: #fff3e0;
            border-color: #ff9800;
            box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #c41e3a;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px 25px;
            border: none;
            transition: background-color 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #a01729;
        }
        
        /* Leaderboard item */
        .leaderboard-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #c41e3a;
        }
        
        .leaderboard-item.top3 {
            background: linear-gradient(135deg, #fff8e1 0%, #fffbf5 100%);
            border-left: 4px solid #ffd700;
        }
        
        /* Participant card */
        .participant-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #dee2e6;
        }
        
        /* Info boxes */
        .info-box {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .info-box.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .info-box.warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        
        .info-box.info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        /* Score input styling */
        .score-display {
            font-size: 20px;
            font-weight: bold;
            color: #c41e3a;
            text-align: center;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .main-header {
                padding: 15px;
            }
            
            .logo {
                width: 60px;
                height: 60px;
                font-size: 24px;
            }
            
            .match-card {
                padding: 10px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# EPL Teams
TEAMS = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
    'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
    'Liverpool', 'Man City', 'Man United', 'Newcastle', 'Nottingham Forest',
    'Sheffield United', 'Tottenham', 'West Ham', 'Wolves', 'Luton Town',
    'Ipswich', 'Southampton', 'Leicester'
]

# Admin password
ADMIN_PASSWORD = "admin123"

# Football-Data.org API Key (hardcoded)
FOOTBALL_DATA_API_KEY = "789354c1955e403bb10d792e31cc5282"

# Data directory
DATA_DIR = "nikkang_data"
