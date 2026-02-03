"""
Registration Page
Nikkang KK EPL Prediction Competition
Public page for new participant registration
FIXED VERSION - Uses DataManager class
"""

import streamlit as st
from datetime import datetime
from utils.data_manager import DataManager
from utils.auth import is_registration_locked
import string
import random

# Page configuration
st.set_page_config(
    page_title="Nikkang KK EPL - Registration",
    page_icon="⚽",
    layout="centered"
)

# Initialize data manager
dm = DataManager()

# Helper functions
def generate_user_id(length=8):
    """Generate a random user ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def safe_get(item, key, default=None):
    """Safely get attribute from dict or object"""
    if isinstance(item, dict):
        return item.get(key, default)
    return default

def to_dict_format(data):
    """Convert list format to dict format if needed"""
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        result = {}
        for i, item in enumerate(data):
            if isinstance(item, dict):
                key = item.get('id', f'item_{i}')
                result[key] = item
        return result
    return {}

# Page header
st.title("⚽ Nikkang KK EPL Prediction Competition")
st.markdown("### Season 2025-26 Registration")
st.markdown("---")

# Display logo if available
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("nikkang_logo.png", width=200)
except:
    pass

st.markdown("""
Welcome to the Nikkang KK English Premier League Prediction Competition!

**How it works:**
- Predict the scores for 10 EPL matches each gameweek
- Earn 6 points for an exact score prediction (KK)
- Earn 3 points for predicting the correct result (win/draw/loss)
- **GOTW Bonus Bonanza:** 10 pts / 5 pts for Game of the Week!
- **Week 38 Finale:** All matches score bonus points!
- Compete against friends and colleagues for bragging rights

**Register below to get started!**
""")

st.markdown("---")

# CHECK IF REGISTRATION IS LOCKED
if is_registration_locked():
    st.error("🔒 **Registration is Currently Closed**")
    st.warning("Registration for the current season has been closed by the administrator.")
    st.info("📞 If you need to register, please contact the competition admin directly.")
    
    st.markdown("---")
    
    # Already registered section for locked state
    st.subheader("🔑 Already Registered?")
    st.markdown("""
    If you've already registered, you can still access your predictions:
    
    - Use your existing prediction link
    - Check your WhatsApp messages
    - Contact the admin for your User ID
    """)
    
    # Enter user ID manually
    with st.expander("Enter User ID to access predictions"):
        manual_id = st.text_input("Your User ID", placeholder="e.g., ABC12345")
        if st.button("Go to Predictions"):
            if manual_id:
                st.markdown(f"[Click here to go to predictions](?user_id={manual_id})")
            else:
                st.warning("Please enter your User ID")
    
    # Contact section
    st.markdown("---")
    with st.expander("📞 Contact Admin"):
        st.markdown("""
        Need help or want to register?
        
        Contact the competition administrator:
        - **WhatsApp:** +968XXXXXXXX
        - **Email:** admin@example.com
        
        Registration may reopen for the next season!
        """)
    
    st.stop()  # Don't show registration form

# Registration form
st.subheader("📝 Register Now")

# EPL Teams list
EPL_TEAMS = ["-- Select Team (Optional) --", "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
             "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", 
             "Leicester City", "Liverpool", "Man City", "Man United", "Newcastle", 
             "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"]

with st.form("registration_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="your@email.com (optional)")
        team = st.selectbox("Favorite Team ⚽ (Optional)", EPL_TEAMS, index=0)
    
    with col2:
        phone = st.text_input("Phone Number *", placeholder="+968XXXXXXXX")
        nickname = st.text_input("Nickname (for leaderboard)", placeholder="Optional display name")
    
    # Terms agreement
    agree = st.checkbox("I agree to participate in the competition and follow the rules")
    
    submit = st.form_submit_button("🎯 Register", use_container_width=True)
    
    if submit:
        # Validation
        if not name:
            st.error("❌ Please enter your full name")
        elif not phone:
            st.error("❌ Please enter your phone number")
        elif not agree:
            st.error("❌ Please agree to the terms to continue")
        else:
            # Load existing participants using DataManager
            participants_raw = dm.load_participants()
            participants = to_dict_format(participants_raw)
            
            # Check if phone already registered
            phone_exists = False
            for p in participants.values():
                if safe_get(p, 'phone', '') == phone:
                    phone_exists = True
                    break
            
            if phone_exists:
                st.warning("⚠️ This phone number is already registered!")
                st.info("If you forgot your prediction link, please contact the admin.")
            else:
                # Generate unique ID
                user_id = generate_user_id()
                
                # Ensure unique ID
                while user_id in participants:
                    user_id = generate_user_id()
                
                # Create new participant
                display_name = nickname if nickname else name
                selected_team = team if team != "-- Select Team (Optional) --" else ''
                new_participant = {
                    'id': user_id,
                    'name': name,
                    'display_name': display_name,
                    'email': email,
                    'phone': phone,
                    'team': selected_team,
                    'status': 'active',
                    'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'link': f"?user_id={user_id}",
                    'notes': '',
                    'predictions': {},
                    'total_points': 0
                }
                
                # Add to participants
                participants[user_id] = new_participant
                dm.save_participants(participants)
                
                # Success message
                st.success("✅ Registration successful!")
                st.balloons()
                
                st.markdown("---")
                st.markdown("### Your Prediction Link")
                
                # Generate prediction link
                # Note: Update this URL when deploying to Streamlit Cloud
                base_url = "https://your-app.streamlit.app"  # Update this!
                prediction_link = f"{base_url}?user_id={user_id}"
                
                st.code(prediction_link)
                
                st.info(f"""
                **Save this link!** You'll need it to make predictions.
                
                **Your User ID:** {user_id}
                
                You can also bookmark this page after clicking the link.
                """)
                
                # WhatsApp option
                if phone:
                    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                    message = f"Welcome to Nikkang KK EPL Competition! Your prediction link: {prediction_link}"
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={message}"
                    st.markdown(f"[📱 Send link to yourself via WhatsApp]({whatsapp_url})")

st.markdown("---")

# Already registered section
st.subheader("🔑 Already Registered?")
st.markdown("""
If you've already registered, you should have received a unique link.

- Check your WhatsApp messages
- Contact the competition admin
- Use your User ID to access predictions
""")

# Enter user ID manually
with st.expander("Enter User ID manually"):
    manual_id = st.text_input("Your User ID", placeholder="e.g., ABC12345")
    if st.button("Go to Predictions"):
        if manual_id:
            st.markdown(f"[Click here to go to predictions](?user_id={manual_id})")
        else:
            st.warning("Please enter your User ID")

st.markdown("---")

# Rules section
with st.expander("📜 Competition Rules"):
    st.markdown("""
    **Scoring System:**
    - Exact score (KK): 6 points
    - Correct result (win/draw/loss): 3 points
    - Incorrect prediction: 0 points
    - **GOTW Bonus Bonanza:** 10 pts / 5 pts
    - **Week 38 Finale:** All matches 10 pts / 5 pts
    
    **Prediction Deadlines:**
    - All predictions must be submitted before match kickoff
    - Late predictions will not be accepted
    - You can change predictions until the deadline
    
    **Leaderboard:**
    - Updated after each gameweek
    - Ties broken by number of exact scores (KK)
    - Final standings announced at season end
    
    **Fair Play:**
    - One account per person
    - No sharing of prediction links
    - Admin decision is final on disputes
    """)

# Contact section
with st.expander("📞 Contact Admin"):
    st.markdown("""
    Having trouble registering? Need help?
    
    Contact the competition administrator:
    - **WhatsApp:** +968XXXXXXXX
    - **Email:** admin@example.com
    
    We'll respond as soon as possible!
    """)

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26")
st.caption("Good luck and enjoy the season! ⚽🏆")
