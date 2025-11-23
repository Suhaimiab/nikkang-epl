"""
Registration Page - Participant Registration
"""

import streamlit as st
from utils.config import setup_page, apply_custom_css, TEAMS
from utils.data_manager import DataManager
from utils.whatsapp import generate_participant_link, generate_whatsapp_message, get_whatsapp_url

setup_page()
apply_custom_css()

dm = DataManager()

st.title("📝 Participant Registration")

st.markdown("---")

# Registration form
st.subheader("Register New Participant")

with st.form("registration_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name*", placeholder="Enter your full name")
        email = st.text_input("Email*", placeholder="your.email@example.com")
    
    with col2:
        phone = st.text_input("WhatsApp Number*", placeholder="+60123456789")
        team = st.selectbox("Favorite EPL Team", [""] + TEAMS)
    
    submit = st.form_submit_button("✅ Register", use_container_width=True)
    
    if submit:
        if not name or not email or not phone:
            st.error("❌ Please fill in all required fields (Name, Email, Phone)")
        else:
            # Add participant
            participant_id = dm.add_participant(name, email, phone, team)
            
            if participant_id:
                st.success(f"✅ Registration successful! Welcome, {name}!")
                
                # Generate link and message
                current_week = dm.get_current_week()
                link = generate_participant_link(participant_id, base_url="http://localhost:8501")
                
                participant = dm.get_participant(participant_id)
                message = generate_whatsapp_message(participant, link, current_week)
                
                # Display information
                st.markdown("---")
                st.subheader("📱 Your Personal Prediction Link")
                
                st.info("**Important:** Save this link! You'll need it to submit predictions each week.")
                
                st.code(link, language=None)
                
                # WhatsApp section
                st.markdown("---")
                st.subheader("💬 WhatsApp Message")
                
                st.text_area("Copy and send this message:", message, height=200)
                
                whatsapp_url = get_whatsapp_url(phone, message)
                st.link_button("📱 Open WhatsApp", whatsapp_url, use_container_width=True)
                
                st.success("✅ Link and message ready! Send it via WhatsApp.")
            else:
                st.error("❌ This email is already registered. Please use a different email.")

st.markdown("---")

# List of registered participants
st.subheader("👥 Registered Participants")

participants = dm.load_participants()

if participants:
    st.info(f"Total Participants: **{len(participants)}**")
    
    # Search/filter
    search = st.text_input("🔍 Search by name or email", "")
    
    # Display participants
    filtered = {k: v for k, v in participants.items() 
                if search.lower() in v['name'].lower() or search.lower() in v['email'].lower()}
    
    if filtered:
        for pid, p in filtered.items():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="participant-card">
                        <strong>{p['name']}</strong><br>
                        <small>📧 {p['email']}</small><br>
                        <small>📱 {p['phone']}</small><br>
                        <small>⚽ Team: {p.get('team', 'Not selected')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"📋 Copy Link", key=f"copy_{pid}"):
                        link = generate_participant_link(pid, base_url="http://localhost:8501")
                        st.code(link, language=None)
                        st.caption("Link copied! Share with participant.")
                
                with col3:
                    if st.button(f"💬 WhatsApp", key=f"wa_{pid}"):
                        current_week = dm.get_current_week()
                        link = generate_participant_link(pid, base_url="http://localhost:8501")
                        message = generate_whatsapp_message(p, link, current_week)
                        whatsapp_url = get_whatsapp_url(p['phone'], message)
                        st.link_button("Open WhatsApp", whatsapp_url, key=f"wa_link_{pid}")
    else:
        st.warning("No participants found matching your search.")
else:
    st.info("No participants registered yet. Be the first to register!")

st.markdown("---")

# Bulk actions
st.subheader("⚙️ Bulk Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Generate All Links", use_container_width=True):
        participants = dm.load_participants()
        current_week = dm.get_current_week()
        
        all_links = []
        for pid, p in participants.items():
            link = generate_participant_link(pid, current_week, base_url="http://localhost:8501")
            all_links.append(f"**{p['name']}**\n{link}\n📱 {p['phone']}\n")
        
        links_text = "\n".join(all_links)
        
        st.text_area("All Participant Links", links_text, height=300)
        st.success("✅ All links generated! Copy and share.")

with col2:
    if st.button("💬 Generate WhatsApp Messages", use_container_width=True):
        participants = dm.load_participants()
        current_week = dm.get_current_week()
        
        all_messages = []
        for pid, p in participants.items():
            link = generate_participant_link(pid, current_week, base_url="http://localhost:8501")
            message = generate_whatsapp_message(p, link, current_week)
            all_messages.append(f"--- {p['name']} ({p['phone']}) ---\n{message}\n")
        
        messages_text = "\n\n".join(all_messages)
        
        st.text_area("All WhatsApp Messages", messages_text, height=300)
        st.success("✅ All messages generated! Copy and send individually.")

st.markdown("---")
st.caption("Nikkang KK - EPL Prediction Competition 2025/26")
