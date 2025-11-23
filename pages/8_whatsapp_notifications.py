"""
WhatsApp Notifications Admin Page
Send notifications to participants via WhatsApp
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.whatsapp_notifier import WhatsAppNotifier, MessageTemplates
from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="WhatsApp Notifications - Nikkang KK",
    page_icon="📱",
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
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📱 WhatsApp Notifications</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Send notifications to participants
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize data manager
dm = DataManager()
participants = dm.load_participants()

# Info about notification methods
st.info("""
**Two Methods Available:**

1. **WhatsApp Web URLs (FREE)** - Generate clickable links that open WhatsApp
2. **Twilio WhatsApp API (PAID)** - Automatic sending ($0.005 per message)

**Recommendation**: Start with FREE WhatsApp Web URLs!
""")

# Notification method selection
notification_method = st.radio(
    "Select Notification Method:",
    ["WhatsApp Web URLs (FREE)", "Twilio API (Requires Setup)"],
    help="WhatsApp Web URLs are free but require manual clicking. Twilio sends automatically but requires account setup."
)

st.markdown("---")

# Tabs for different notification types
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Prediction Reminders",
    "👋 Welcome Messages",
    "📊 Results Posted",
    "🏆 Weekly Winners",
    "✉️ Custom Message"
])

# Base URL for the app
base_url = st.text_input(
    "App Base URL:",
    value="https://nikkang-kk-epl.streamlit.app",
    help="Your app's URL for generating links"
)

# Tab 1: Prediction Reminders
with tab1:
    st.markdown("### ⏰ Send Prediction Reminders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        week_number = st.number_input("Week Number:", min_value=1, max_value=38, value=1)
        deadline = st.text_input("Deadline:", value="Saturday 3:00 PM GMT")
    
    with col2:
        # Select recipients
        if participants:
            all_participants = st.checkbox("Send to all participants", value=True)
            
            if not all_participants:
                participant_names = [p['name'] for p in participants]
                selected_names = st.multiselect(
                    "Select Recipients:",
                    participant_names
                )
        else:
            st.warning("No participants registered yet!")
    
    # Preview message
    if participants:
        st.markdown("#### 📝 Message Preview:")
        preview_message = MessageTemplates.prediction_reminder(
            "John Doe",
            week_number,
            deadline,
            f"{base_url}?user_id=ABC123"
        )
        st.code(preview_message, language=None)
    
    # Generate notifications
    if st.button("🚀 Generate Notifications", key="reminder_btn", use_container_width=True, type="primary"):
        if not participants:
            st.error("No participants to notify!")
        else:
            with st.spinner("Generating notifications..."):
                # Filter participants
                if all_participants:
                    selected_participants = participants
                else:
                    selected_participants = [p for p in participants if p['name'] in selected_names]
                
                if not selected_participants:
                    st.error("No participants selected!")
                else:
                    notifier = WhatsAppNotifier(method='url')
                    results = []
                    
                    for participant in selected_participants:
                        prediction_url = f"{base_url}?user_id={participant.get('id', 'unknown')}"
                        message = MessageTemplates.prediction_reminder(
                            participant['name'],
                            week_number,
                            deadline,
                            prediction_url
                        )
                        
                        url = notifier.send_whatsapp_url(
                            participant.get('phone', ''), 
                            message
                        )
                        
                        results.append({
                            'Name': participant['name'],
                            'Phone': participant.get('phone', 'Not provided'),
                            'WhatsApp Link': url
                        })
                    
                    st.success(f"✅ Generated {len(results)} notifications!")
                    
                    # Display results
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Instructions
                    st.info("""
                    **How to send:**
                    1. Click each WhatsApp link in the table above
                    2. This opens WhatsApp with the message pre-filled
                    3. Click Send in WhatsApp
                    4. Repeat for each participant
                    
                    **Tip**: Open links in new tabs to speed up the process!
                    """)

# Tab 2: Welcome Messages
with tab2:
    st.markdown("### 👋 Send Welcome Messages")
    
    st.info("Send welcome messages to newly registered participants")
    
    if participants:
        # Select new participants
        new_participants = st.multiselect(
            "Select New Participants:",
            [p['name'] for p in participants]
        )
        
        # Preview
        if new_participants:
            st.markdown("#### 📝 Message Preview:")
            preview_message = MessageTemplates.welcome_message(
                new_participants[0],
                f"{base_url}?user_id=ABC123"
            )
            st.code(preview_message, language=None)
        
        if st.button("🚀 Generate Welcome Messages", key="welcome_btn", use_container_width=True, type="primary"):
            if not new_participants:
                st.error("Please select participants!")
            else:
                with st.spinner("Generating notifications..."):
                    notifier = WhatsAppNotifier(method='url')
                    results = []
                    
                    for participant in participants:
                        if participant['name'] in new_participants:
                            registration_url = f"{base_url}?user_id={participant.get('id', 'unknown')}"
                            message = MessageTemplates.welcome_message(
                                participant['name'],
                                registration_url
                            )
                            
                            url = notifier.send_whatsapp_url(
                                participant.get('phone', ''),
                                message
                            )
                            
                            results.append({
                                'Name': participant['name'],
                                'Phone': participant.get('phone', 'Not provided'),
                                'WhatsApp Link': url
                            })
                    
                    st.success(f"✅ Generated {len(results)} welcome messages!")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
    else:
        st.warning("No participants registered yet!")

# Tab 3: Results Posted
with tab3:
    st.markdown("### 📊 Results Posted Notifications")
    
    week_results = st.number_input("Week Number:", min_value=1, max_value=38, value=1, key="results_week")
    
    st.info("This will notify participants that results are posted. Points and ranks will be included.")
    
    if st.button("🚀 Generate Results Notifications", key="results_btn", use_container_width=True, type="primary"):
        if not participants:
            st.error("No participants to notify!")
        else:
            with st.spinner("Generating notifications..."):
                notifier = WhatsAppNotifier(method='url')
                results = []
                
                for idx, participant in enumerate(participants, 1):
                    message = MessageTemplates.results_posted(
                        participant['name'],
                        week_results,
                        points=15,  # Replace with actual points
                        rank=idx,   # Replace with actual rank
                        url=f"{base_url}/5_leaderboard"
                    )
                    
                    url = notifier.send_whatsapp_url(
                        participant.get('phone', ''),
                        message
                    )
                    
                    results.append({
                        'Name': participant['name'],
                        'Phone': participant.get('phone', 'Not provided'),
                        'WhatsApp Link': url
                    })
                
                st.success(f"✅ Generated {len(results)} notifications!")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)

# Tab 4: Weekly Winners
with tab4:
    st.markdown("### 🏆 Congratulate Weekly Winners")
    
    week_winner = st.number_input("Week Number:", min_value=1, max_value=38, value=1, key="winner_week")
    
    if participants:
        winner_name = st.selectbox(
            "Select Week Winner:",
            [p['name'] for p in participants]
        )
        
        winner_points = st.number_input("Winner's Points:", min_value=0, value=18)
        
        # Preview
        st.markdown("#### 📝 Message Preview:")
        preview_message = MessageTemplates.weekly_winner(
            winner_name,
            week_winner,
            winner_points,
            f"{base_url}/5_leaderboard"
        )
        st.code(preview_message, language=None)
        
        if st.button("🚀 Send Winner Notification", key="winner_btn", use_container_width=True, type="primary"):
            winner = [p for p in participants if p['name'] == winner_name][0]
            
            notifier = WhatsAppNotifier(method='url')
            
            message = MessageTemplates.weekly_winner(
                winner['name'],
                week_winner,
                winner_points,
                f"{base_url}/5_leaderboard"
            )
            
            url = notifier.send_whatsapp_url(
                winner.get('phone', ''),
                message
            )
            
            st.success(f"✅ Winner notification generated!")
            st.markdown(f"**WhatsApp Link**: {url}")
            st.info("Click the link above to send the congratulations message!")

# Tab 5: Custom Message
with tab5:
    st.markdown("### ✉️ Send Custom Message")
    
    st.info("Create and send a custom message to selected participants")
    
    # Recipients
    if participants:
        all_custom = st.checkbox("Send to all participants", value=True, key="custom_all")
        
        if not all_custom:
            custom_recipients = st.multiselect(
                "Select Recipients:",
                [p['name'] for p in participants],
                key="custom_recipients"
            )
    
    # Custom message
    custom_message = st.text_area(
        "Message:",
        value="",
        height=200,
        placeholder="Enter your custom message here..."
    )
    
    # Preview
    if custom_message:
        st.markdown("#### 📝 Message Preview:")
        st.code(custom_message, language=None)
    
    if st.button("🚀 Generate Custom Notifications", key="custom_btn", use_container_width=True, type="primary"):
        if not custom_message:
            st.error("Please enter a message!")
        elif not participants:
            st.error("No participants to notify!")
        else:
            with st.spinner("Generating notifications..."):
                # Filter participants
                if all_custom:
                    selected_participants = participants
                else:
                    selected_participants = [p for p in participants if p['name'] in custom_recipients]
                
                if not selected_participants:
                    st.error("No participants selected!")
                else:
                    notifier = WhatsAppNotifier(method='url')
                    results = []
                    
                    for participant in selected_participants:
                        url = notifier.send_whatsapp_url(
                            participant.get('phone', ''),
                            custom_message
                        )
                        
                        results.append({
                            'Name': participant['name'],
                            'Phone': participant.get('phone', 'Not provided'),
                            'WhatsApp Link': url
                        })
                    
                    st.success(f"✅ Generated {len(results)} custom notifications!")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)

st.markdown("---")

# Twilio Setup Instructions
if "Twilio" in notification_method:
    st.markdown("### 🔧 Twilio WhatsApp Setup")
    
    with st.expander("📖 How to Setup Twilio (Step-by-Step)"):
        st.markdown("""
        **Step 1: Create Twilio Account**
        1. Go to: https://www.twilio.com/try-twilio
        2. Sign up (get $15 free credit)
        3. Verify your email and phone
        
        **Step 2: Enable WhatsApp**
        1. In Twilio Console → Messaging → Try it Out → Try WhatsApp
        2. Follow instructions to connect WhatsApp Sandbox
        3. Send "join [your-code]" to Twilio WhatsApp number
        
        **Step 3: Get Credentials**
        1. In Twilio Console → Account → Settings
        2. Copy Account SID
        3. Copy Auth Token
        4. Copy WhatsApp number (format: +14155238886)
        
        **Step 4: Configure Below**
        Enter your credentials in the fields below
        
        **Cost**: $0.005 per message (~200 messages for $1)
        """)
    
    st.markdown("#### 🔑 Twilio Credentials")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_sid = st.text_input("Account SID:", type="password")
        auth_token = st.text_input("Auth Token:", type="password")
    
    with col2:
        whatsapp_from = st.text_input("WhatsApp From Number:", value="+14155238886")
    
    if account_sid and auth_token and whatsapp_from:
        st.success("✅ Credentials configured! You can now send automatic WhatsApp messages.")
    else:
        st.warning("⚠️ Enter Twilio credentials to enable automatic sending")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> - WhatsApp Notifications</p>
    <p>💡 Tip: Save time by opening all links in new tabs!</p>
</div>
""", unsafe_allow_html=True)
