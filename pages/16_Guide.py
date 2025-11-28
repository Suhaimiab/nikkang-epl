"""
Guide Page - Quick Reference for Participants and Admins
Nikkang KK EPL Prediction Competition 2025/26
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(page_title="Guide - Nikkang KK", page_icon="📖", layout="wide")

# Try to apply custom CSS
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.markdown("""
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:2rem;border-radius:15px;text-align:center;margin-bottom:2rem;">
    <h1 style="margin:0;font-size:2.5rem;">📖 Nikkang KK Guide</h1>
    <p style="margin:0.5rem 0 0 0;opacity:0.9;font-size:1.1rem;">EPL Prediction Competition 2025/26</p>
</div>
""", unsafe_allow_html=True)

# Toggle between Participant and Admin guide
guide_type = st.radio(
    "Select Guide:",
    ["👤 Participant Guide", "🔧 Admin Guide"],
    horizontal=True
)

st.markdown("---")

# =============================================================================
# PARTICIPANT GUIDE
# =============================================================================
if guide_type == "👤 Participant Guide":
    
    st.markdown("## 👤 Participant Guide")
    st.markdown("*Everything you need to know to participate in the competition*")
    
    # Quick Start
    st.markdown("""
    <div style="background:#d4edda;border-left:4px solid #28a745;padding:1rem;border-radius:5px;margin:1rem 0;">
        <h4 style="margin:0;color:#155724;">🚀 Quick Start</h4>
        <ol style="margin:0.5rem 0 0 0;color:#155724;">
            <li>Register your name (if not already registered)</li>
            <li>Go to <strong>Predictions</strong> page</li>
            <li>Select your name and the current week</li>
            <li>Enter your score predictions for all 10 matches</li>
            <li>Click <strong>Save Predictions</strong> before the deadline!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Scoring System
    st.markdown("### 🎯 Scoring System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background:#f8f9fa;padding:1.5rem;border-radius:10px;margin-bottom:1rem;">
            <h4 style="color:#1a1a2e;margin-top:0;">Regular Matches</h4>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="border-bottom:1px solid #dee2e6;">
                    <td style="padding:8px 0;"><span style="background:#28a745;color:white;padding:2px 8px;border-radius:4px;">Exact Score (KK)</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;">6 points</td>
                </tr>
                <tr style="border-bottom:1px solid #dee2e6;">
                    <td style="padding:8px 0;"><span style="background:#ffc107;color:#1a1a2e;padding:2px 8px;border-radius:4px;">Correct Result</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;">3 points</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;"><span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;">Wrong</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;">0 points</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background:#f3e5f5;padding:1.5rem;border-radius:10px;margin-bottom:1rem;">
            <h4 style="color:#6b46c1;margin-top:0;">⭐ GOTW & Week 38 Finale</h4>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="border-bottom:1px solid #ce93d8;">
                    <td style="padding:8px 0;"><span style="background:#9b59b6;color:white;padding:2px 8px;border-radius:4px;">Exact Score (KK)</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;color:#6b46c1;">10 points</td>
                </tr>
                <tr style="border-bottom:1px solid #ce93d8;">
                    <td style="padding:8px 0;"><span style="background:#9b59b6;color:white;padding:2px 8px;border-radius:4px;">Correct Result</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;color:#6b46c1;">5 points</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;"><span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;">Wrong</span></td>
                    <td style="padding:8px 0;text-align:right;font-weight:bold;">0 points</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    **What counts as "Correct Result"?**
    - You predicted Home Win and the home team won (any score)
    - You predicted Away Win and the away team won (any score)
    - You predicted Draw and the match ended in a draw (any score)
    """)
    
    st.markdown("---")
    
    # Season Structure
    st.markdown("### 📅 Season Structure")
    
    st.markdown("""
    The season is divided into **4 Stages**:
    
    | Stage | Weeks | Description |
    |-------|-------|-------------|
    | **Stage 1** | Week 1-10 | Opening stage |
    | **Stage 2** | Week 11-20 | Mid-season stage |
    | **Stage 3** | Week 21-30 | Second half stage |
    | **Stage 4** | Week 31-38 | Finale stage (includes Week 38 double points!) |
    
    **Points carry forward** from previous stages to the next!
    """)
    
    st.markdown("---")
    
    # Winners & Tiebreakers
    st.markdown("### 🏆 Winners & Tiebreakers")
    
    st.markdown("""
    <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:1rem;border-radius:5px;margin:1rem 0;">
        <h4 style="margin:0;color:#856404;">Tiebreaker Rules</h4>
        <ol style="margin:0.5rem 0 0 0;color:#856404;">
            <li><strong>Points</strong> - Highest points wins</li>
            <li><strong>KK Count</strong> - If points are equal, most exact scores (KK) wins</li>
            <li><strong>Joint Winners</strong> - If both points AND KK are equal, joint winners declared</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Awards:**
    - 🏆 **Weekly Champion** - Highest points each gameweek
    - 🏆 **Stage Winner** - Highest points at end of each stage
    - 🏆 **Season Champion** - Highest total points at end of season
    - 🎯 **KK Master** - Most exact score predictions
    """)
    
    st.markdown("---")
    
    # How to Submit Predictions
    st.markdown("### 📝 How to Submit Predictions")
    
    st.markdown("""
    **Step-by-Step:**
    
    1. **Go to Predictions page** from the sidebar
    
    2. **Select your name** from the dropdown (or use your personal link)
    
    3. **Select the week** you want to predict
    
    4. **Enter scores** for each match:
       - Use the number inputs to set Home and Away scores
       - All 10 matches must be filled
    
    5. **Click "Save Predictions"** to submit
    
    6. **Verify** your predictions in the summary shown
    """)
    
    st.warning("""
    ⏰ **IMPORTANT:** Submit predictions **BEFORE** the first match of the gameweek kicks off!
    Late submissions will NOT be accepted.
    """)
    
    st.markdown("---")
    
    # Checking Results
    st.markdown("### 📊 Checking Your Results")
    
    st.markdown("""
    **Weekly Results Page:**
    - See all participants' predictions vs actual results
    - Color-coded: 🟢 Green = KK, 🟡 Yellow = Correct, 🔴 Red = Wrong
    - Download as PNG to share
    
    **Leaderboard Page:**
    - Season standings with stage breakdown
    - Top 3 by points and by KK count
    - Stage-by-stage performance
    """)
    
    st.markdown("---")
    
    # FAQ
    st.markdown("### ❓ FAQ")
    
    with st.expander("Can I change my predictions after submitting?"):
        st.markdown("Yes, you can update your predictions anytime **before the deadline** (first match kickoff).")
    
    with st.expander("What is GOTW (Game of the Week)?"):
        st.markdown("One match each week is designated as GOTW with bonus points: 10 pts for exact score, 5 pts for correct result.")
    
    with st.expander("What happens if I miss a week?"):
        st.markdown("You will score 0 points for that week. There's no penalty, but you'll fall behind in the standings.")
    
    with st.expander("How do I get my personal prediction link?"):
        st.markdown("After making predictions, click 'Copy My Prediction Link'. This link takes you directly to your predictions without needing to select your name.")

# =============================================================================
# ADMIN GUIDE
# =============================================================================
else:
    st.markdown("## 🔧 Admin Guide")
    st.markdown("*Managing the Nikkang KK EPL Prediction Competition*")
    
    # Admin Password
    st.markdown("""
    <div style="background:#f8d7da;border-left:4px solid #dc3545;padding:1rem;border-radius:5px;margin:1rem 0;">
        <h4 style="margin:0;color:#721c24;">🔐 Admin Access</h4>
        <p style="margin:0.5rem 0 0 0;color:#721c24;">
            Admin pages require password authentication. Contact the competition organizer for access.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Weekly Workflow
    st.markdown("### 📋 Weekly Admin Workflow")
    
    st.markdown("""
    <div style="background:#e3f2fd;padding:1.5rem;border-radius:10px;margin:1rem 0;">
        <h4 style="color:#1565c0;margin-top:0;">Before Gameweek Starts</h4>
        <ol style="margin:0;color:#1565c0;">
            <li>Go to <strong>Fixtures</strong> page</li>
            <li>Import fixtures for the upcoming week from API</li>
            <li>Set the <strong>GOTW</strong> (Game of the Week) match</li>
            <li>Verify fixtures are correct</li>
            <li>Send WhatsApp reminder to participants</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#fff8e1;padding:1.5rem;border-radius:10px;margin:1rem 0;">
        <h4 style="color:#f57f17;margin-top:0;">After Gameweek Ends</h4>
        <ol style="margin:0;color:#f57f17;">
            <li>Go to <strong>Results Management</strong> page</li>
            <li>Import results from API (or enter manually)</li>
            <li>Verify results are correct for each match</li>
            <li>Go to <strong>Recalculate Points</strong> to update scores</li>
            <li>Check <strong>Weekly Results</strong> page for accuracy</li>
            <li>Send WhatsApp update with weekly standings</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Admin Pages Overview
    st.markdown("### 📂 Admin Pages Overview")
    
    admin_pages = [
        ("7️⃣ Admin Panel", "Main admin dashboard - system overview, quick actions"),
        ("8️⃣ Manage Participants", "Add, edit, delete participants, manage nicknames"),
        ("9️⃣ Fixtures", "Import fixtures from API, set GOTW matches"),
        ("🔟 Results Management", "Import/enter match results, repair tools"),
        ("1️⃣1️⃣ Recalculate Points", "Recalculate all scores from predictions vs results"),
        ("1️⃣2️⃣ Stage Scores", "Lock stage scores, enter manual adjustments"),
        ("1️⃣4️⃣ WhatsApp", "Generate WhatsApp messages for reminders/updates"),
        ("1️⃣5️⃣ Repair Results", "Fix mismatched results, clear and re-enter week data"),
    ]
    
    for page, desc in admin_pages:
        st.markdown(f"**{page}** - {desc}")
    
    st.markdown("---")
    
    # Results Management
    st.markdown("### 🎯 Results Management")
    
    st.markdown("""
    **Importing Results:**
    1. Go to Results Management → Import Results tab
    2. Set date range covering the gameweek
    3. Click "Fetch from API"
    4. Review the fetched results
    5. Click "Apply Results"
    
    **If Results Are Wrong:**
    1. Go to Results Management → Settings tab
    2. Use "Clear Results for This Week" feature
    3. Re-import from API or use **Repair Results** page
    4. Enter correct scores manually
    """)
    
    st.warning("""
    ⚠️ **Important:** After importing/fixing results, always run **Recalculate Points** to update all scores!
    """)
    
    st.markdown("---")
    
    # Stage Management
    st.markdown("### 📊 Stage Management")
    
    st.markdown("""
    **At End of Each Stage:**
    1. Go to **Stage Scores** page
    2. Review calculated scores for the stage
    3. Make any manual adjustments if needed
    4. Click **"Save & Lock Stage"** to finalize
    
    **Locked vs Unlocked:**
    - 🔓 **Unlocked** - Uses automated calculation from predictions
    - 🔒 **Locked** - Uses manually entered/confirmed scores
    
    Once locked, stage scores won't change even if predictions are recalculated.
    """)
    
    st.markdown("---")
    
    # WhatsApp Messages
    st.markdown("### 📱 WhatsApp Messages")
    
    st.markdown("""
    The **WhatsApp** page generates ready-to-copy messages for:
    
    | Message Type | When to Use |
    |--------------|-------------|
    | **Prediction Reminder** | Before gameweek deadline |
    | **Results Update** | After results are entered |
    | **Weekly Standings** | After weekly points calculated |
    | **Stage Summary** | At end of each stage |
    """)
    
    st.markdown("---")
    
    # Troubleshooting
    st.markdown("### 🔧 Troubleshooting")
    
    with st.expander("Results showing wrong scores"):
        st.markdown("""
        1. Go to **Repair Results** page
        2. Select the affected week
        3. Clear all results for that week
        4. Re-enter correct scores manually
        5. Run **Recalculate Points**
        """)
    
    with st.expander("Weekly Results colors don't match"):
        st.markdown("""
        This usually means results are stored in wrong order.
        1. Use **Repair Results** page to clear and re-enter
        2. The fix in Results Management now matches by team names
        """)
    
    with st.expander("Participant missing from leaderboard"):
        st.markdown("""
        1. Check if participant is registered in **Manage Participants**
        2. Ensure they have submitted predictions
        3. Run **Recalculate Points** to refresh
        """)
    
    with st.expander("API not returning fixtures/results"):
        st.markdown("""
        1. Check your internet connection
        2. Verify API key in secrets.toml
        3. Try different date range
        4. Enter data manually if API is down
        """)
    
    st.markdown("---")
    
    # Best Practices
    st.markdown("### ✅ Best Practices")
    
    st.markdown("""
    1. **Always verify** imported data before saving
    2. **Backup** by downloading data periodically
    3. **Run Recalculate** after any results changes
    4. **Lock stages** promptly after they complete
    5. **Send reminders** 24 hours before deadline
    6. **Check Weekly Results** page after entering results to verify accuracy
    """)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📧 Contact Admin**")
    st.caption("For issues or questions")

with col2:
    st.markdown("**🔄 Last Updated**")
    st.caption("November 2025")

with col3:
    st.markdown("**⚽ Season**")
    st.caption("EPL 2025/26")

st.markdown("---")
st.caption("Nikkang KK EPL Prediction League - Competition Guide")
