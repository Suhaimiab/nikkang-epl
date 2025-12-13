"""
Export Prediction Matrix - Admin Tool
Nikkang KK EPL Prediction Competition
Export predictions in Excel-ready CSV format
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="Export Matrix - Nikkang KK",
    page_icon="📥",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Authentication
if not check_password():
    st.stop()

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📥 Export Prediction Matrix</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Export predictions in Excel-ready CSV format
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize data manager
dm = DataManager()

# Load data
data_dir = Path("nikkang_data")

try:
    with open(data_dir / "participants.json", 'r') as f:
        participants = json.load(f)
    with open(data_dir / "predictions.json", 'r') as f:
        predictions = json.load(f)
    with open(data_dir / "matches.json", 'r') as f:
        matches = json.load(f)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Get available weeks
available_weeks = sorted([int(w) for w in predictions.keys() if w.isdigit()])

if not available_weeks:
    st.warning("No prediction data available yet.")
    st.stop()

# Main content
st.markdown("---")

# Export options
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Export Options")
    
    export_type = st.radio(
        "What would you like to export?",
        ["All Weeks", "Specific Week", "Date Range"],
        horizontal=True
    )
    
    weeks_to_export = []
    
    if export_type == "All Weeks":
        weeks_to_export = available_weeks
        st.info(f"Will export **{len(available_weeks)} weeks** (Week {min(available_weeks)} to {max(available_weeks)})")
    
    elif export_type == "Specific Week":
        selected_week = st.selectbox(
            "Select Week:",
            available_weeks,
            format_func=lambda x: f"Week {x}"
        )
        weeks_to_export = [selected_week]
        st.info(f"Will export **Week {selected_week}** only")
    
    else:  # Date Range
        col_a, col_b = st.columns(2)
        with col_a:
            start_week = st.selectbox(
                "From Week:",
                available_weeks,
                format_func=lambda x: f"Week {x}"
            )
        with col_b:
            end_week = st.selectbox(
                "To Week:",
                [w for w in available_weeks if w >= start_week],
                format_func=lambda x: f"Week {x}",
                index=len([w for w in available_weeks if w >= start_week]) - 1
            )
        weeks_to_export = [w for w in available_weeks if start_week <= w <= end_week]
        st.info(f"Will export **{len(weeks_to_export)} weeks** (Week {start_week} to {end_week})")

with col2:
    st.markdown("### 📋 Preview")
    
    # Calculate stats
    total_participants = len(participants)
    total_weeks = len(weeks_to_export)
    
    # Count predictions for selected weeks
    pred_count = 0
    for w in weeks_to_export:
        week_preds = predictions.get(str(w), {})
        for uid, preds in week_preds.items():
            if isinstance(preds, list):
                pred_count += len(preds)
    
    st.metric("Participants", total_participants)
    st.metric("Weeks", total_weeks)
    st.metric("Total Predictions", pred_count)

# Column format info
st.markdown("---")
st.markdown("### 📄 CSV Format")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Columns included:**
    - `Week` - Gameweek number
    - `Participant` - Player name
    - `Match_No` - Match number (1-10)
    - `Home_Team` - Home team
    - `Away_Team` - Away team
    """)

with col2:
    st.markdown("""
    - `Pred_Home` - Home score (NUMBER)
    - `Pred_Away` - Away score (NUMBER)
    - `GOTW` - Game of the Week (YES/NO)
    - `Match` - Full match label
    """)

st.info("💡 **Pred_Home** and **Pred_Away** are numeric columns - perfect for Excel formulas and calculations!")

# Generate button
st.markdown("---")

if st.button("📥 Generate Prediction Matrix CSV", type="primary", use_container_width=True):
    with st.spinner("Generating CSV file..."):
        # Build data
        all_rows = []
        
        for week_num in weeks_to_export:
            week_str = str(week_num)
            week_predictions = predictions.get(week_str, {})
            week_matches = matches.get(week_str, [])
            
            if not week_matches:
                st.warning(f"⚠️ Week {week_num}: No matches found, skipping")
                continue
            
            for participant_id, preds in week_predictions.items():
                # Get participant name
                p_name = participant_id
                for uid, p in participants.items():
                    if uid == participant_id or p.get('id') == participant_id:
                        p_name = p.get('display_name') or p.get('name', participant_id)
                        break
                
                if not isinstance(preds, list):
                    continue
                
                for idx, pred in enumerate(preds):
                    if idx >= len(week_matches):
                        break
                    
                    match = week_matches[idx]
                    
                    # Get prediction
                    if isinstance(pred, dict):
                        pred_home = pred.get('home')
                        pred_away = pred.get('away')
                    else:
                        pred_home = None
                        pred_away = None
                    
                    # Build row
                    all_rows.append({
                        'Week': week_num,
                        'Participant': p_name,
                        'Match_No': idx + 1,
                        'Home_Team': match.get('home', ''),
                        'Away_Team': match.get('away', ''),
                        'Pred_Home': pred_home,
                        'Pred_Away': pred_away,
                        'GOTW': 'YES' if match.get('gotw', False) else 'NO',
                        'Match': f"{match.get('home', '')} vs {match.get('away', '')}"
                    })
        
        if not all_rows:
            st.error("No data to export!")
            st.stop()
        
        # Create DataFrame
        df = pd.DataFrame(all_rows)
        
        # Success message
        st.success(f"✅ Generated **{len(df)} predictions** from **{len(weeks_to_export)} weeks**")
        
        # Download button
        csv = df.to_csv(index=False)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"prediction_matrix_{timestamp}.csv"
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.download_button(
                label="💾 Download CSV File",
                data=csv,
                file_name=filename,
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        
        # Preview
        st.markdown("---")
        st.markdown("### 👀 Preview (First 20 rows)")
        st.dataframe(df.head(20), use_container_width=True)
        
        # Summary by week
        st.markdown("---")
        st.markdown("### 📊 Export Summary")
        
        summary_data = []
        for week in weeks_to_export:
            week_df = df[df['Week'] == week]
            participants_count = week_df['Participant'].nunique()
            predictions_count = len(week_df)
            
            summary_data.append({
                'Week': f"Week {week}",
                'Participants': participants_count,
                'Predictions': predictions_count
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Usage guide
st.markdown("---")
st.markdown("### 💡 Excel Usage Tips")

with st.expander("📖 How to use this CSV in Excel", expanded=False):
    st.markdown("""
    #### Quick Excel Formulas
    
    **1. Create "Score" column (display format):**
    ```excel
    =F2&"-"&G2
    ```
    Result: "2-1", "3-0", etc.
    
    **2. Count predictions per participant:**
    ```excel
    =COUNTIF(B:B, "Suhaimi")
    ```
    
    **3. Average predicted home goals:**
    ```excel
    =AVERAGEIF(B:B, "Suhaimi", F:F)
    ```
    
    #### Pivot Table for Traditional Matrix View
    - **Rows:** Participant
    - **Columns:** Match
    - **Values:** Pred_Home (or custom "Score" field)
    
    #### Conditional Formatting
    - Highlight GOTW: Format cells where `H2="YES"`
    - Highlight draws: Format cells where `F2=G2`
    - Highlight high scores: Format cells where `F2>=3` or `G2>=3`
    
    #### Filtering
    1. Select data → Data → Filter
    2. Use dropdowns to filter by:
       - Week number
       - Participant name
       - GOTW (YES/NO)
       - Specific matches
    
    #### Analysis Ideas
    - Most optimistic predictor (highest avg total goals)
    - Most defensive predictions (lowest avg goals)
    - Home win bias (Pred_Home > Pred_Away count)
    - Draw predictor (Pred_Home = Pred_Away count)
    """)

with st.expander("📊 Sample Pivot Table Setups", expanded=False):
    st.markdown("""
    #### 1. Traditional Prediction Matrix
    ```
    Rows: Participant
    Columns: Match
    Values: Pred_Home or "Score" column
    ```
    Shows classic matrix view
    
    #### 2. Participant Summary
    ```
    Rows: Participant
    Values: 
      - Count of Match_No (predictions made)
      - Average of Pred_Home
      - Average of Pred_Away
    ```
    Shows participation and tendencies
    
    #### 3. Match Analysis
    ```
    Rows: Match
    Values:
      - Average of Pred_Home
      - Average of Pred_Away
      - Count of Participant
    ```
    See consensus predictions
    
    #### 4. GOTW Summary
    ```
    Filter: GOTW = "YES"
    Rows: Participant, Week
    Values: Pred_Home, Pred_Away
    ```
    All GOTW predictions
    
    #### 5. Week-by-Week Performance
    ```
    Rows: Week, Participant
    Values: Count of Match_No
    ```
    Track participation over time
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem 0; color: #6c757d; font-size: 0.9rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> - Export Tool</p>
    <p>CSV files open in Excel, Google Sheets, Numbers, and any spreadsheet software</p>
</div>
""", unsafe_allow_html=True)
