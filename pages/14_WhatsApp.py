"""
WhatsApp Notifications Admin Page
Send notifications to participants via WhatsApp Web URLs
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

def display_bulk_send_interface(results, title="Individual Links"):
    """Display bulk send interface with buttons and individual links"""
    
    st.markdown("### 🚀 Bulk Send")
    
    # Create HTML with JavaScript bulk opener
    links_array = [r['WhatsApp Link'] for r in results]
    links_js = str(links_array).replace("'", '"')
    
    bulk_send_html = f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <button onclick="openAllWhatsApp()" 
                style="background: #25D366; color: white; padding: 1rem 2rem; 
                       border: none; border-radius: 8px; cursor: pointer; 
                       font-size: 1.1rem; font-weight: bold; width: 100%;">
            📤 Open All {len(results)} WhatsApp Chats
        </button>
        <p style="text-align: center; margin-top: 0.5rem; color: #6c757d; font-size: 0.9rem;">
            Opens all WhatsApp links with 0.5s delay (Allow popups!)
        </p>
    </div>
    
    <script>
    function openAllWhatsApp() {{
        const links = {links_js};
        const delay = 500; // 500ms delay between tabs
        
        links.forEach((link, index) => {{
            setTimeout(() => {{
                window.open(link, '_blank');
            }}, index * delay);
        }});
        
        alert('Opening ' + links.length + ' WhatsApp chats!\\n\\nAllow popups if blocked.');
    }}
    </script>
    """
    
    st.markdown(bulk_send_html, unsafe_allow_html=True)
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        links_text = "\n".join([f"{r['Name']}: {r['WhatsApp Link']}" for r in results])
        st.download_button(
            "💾 Download TXT",
            data=links_text,
            file_name=f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            width='stretch'
        )
    
    with col2:
        # HTML file
        html_links = "\n".join([f'        <li><a href="{r["WhatsApp Link"]}" target="_blank">{r["Name"]}</a></li>' for r in results])
        html_content = f"""<!DOCTYPE html>
<html><head><title>WhatsApp Links</title></head>
<body>
<h1>WhatsApp Bulk Send - {len(results)} people</h1>
<button onclick="openAll()" style="padding: 15px; background: #25D366; color: white; border: none;">Open All</button>
<ul>
{html_links}
</ul>
<script>
function openAll() {{ {links_js}.forEach((l, i) => setTimeout(() => window.open(l, '_blank'), i * 500)); }}
</script>
</body></html>"""
        
        st.download_button(
            "🌐 Download HTML",
            data=html_content,
            file_name=f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            width='stretch'
        )
    
    st.markdown("---")
    st.markdown(f"### 📲 {title}")
    st.caption("Click individually if bulk doesn't work")
    
    for idx, result in enumerate(results, 1):
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"**{idx}. {result['Name']}**")
            st.caption(f"📞 {result['Phone']}")
        with col2:
            st.markdown(f"[🟢 Open WhatsApp]({result['WhatsApp Link']})")
        if idx < len(results):
            st.markdown("---")
    
    with st.expander("📋 View Data Table"):
        df = pd.DataFrame(results)
        st.dataframe(df, width='stretch')

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
    st.sidebar.image("nikkang_logo.png", width='stretch')
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📱 WhatsApp Notifications</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Send notifications to participants via WhatsApp
    </p>
</div>
""", unsafe_allow_html=True)

dm = DataManager()

# Base URL for links
base_url = st.text_input(
    "App Base URL:",
    value="https://nikkang-epl.streamlit.app",
    help="Base URL for your Streamlit app"
)

# Message templates
class MessageTemplates:
    @staticmethod
    def prediction_reminder(name, week, deadline, prediction_url):
        return f"""🎯 *Nikkang KK EPL Prediction Reminder*

Hi {name}! 👋

⚽ Week {week} predictions are now open!

⏰ *Deadline:* {deadline}

📝 Submit your predictions here:
{prediction_url}

Good luck! 🍀

_Nikkang KK Admin Team_"""

    @staticmethod
    def welcome_message(name, registration_url):
        return f"""👋 *Welcome to Nikkang KK EPL Prediction League!*

Hi {name}! 🎉

Thanks for joining our Premier League prediction competition!

🔗 *Your Personal Link:*
{registration_url}

📖 *How to Play:*
• Predict 10 matches each week
• Choose your Game of the Week
• Earn points for exact scores & correct results
• Compete across 4 rounds

Good luck this season! ⚽

_Nikkang KK Admin Team_"""

    @staticmethod
    def results_posted(name, week, url):
        return f"""📊 *Week {week} Results Are In!*

Hi {name}!

The results for Week {week} have been posted! 🎉

See how you did:
{url}

Keep up the predictions! 💪

_Nikkang KK Admin Team_"""

    @staticmethod
    def weekly_winner(name, week, points, url):
        return f"""🏆 *Congratulations Week {week} Winner!*

🎉 *{name}* 🎉

You're the champion of Week {week} with *{points} points*!

Amazing predictions! Keep it up! 💪

Check the leaderboard:
{url}

_Nikkang KK Admin Team_"""

# WhatsApp Notifier
class WhatsAppNotifier:
    def __init__(self, method='url'):
        self.method = method
    
    def send_whatsapp_url(self, phone_or_group, message):
        """Generate WhatsApp Web URL for individual or group"""
        import urllib.parse
        
        # Check if it's a full invite link
        if 'chat.whatsapp.com' in phone_or_group:
            # For group invite links, just return the link itself
            # Message must be copied separately (WhatsApp limitation)
            return phone_or_group
        
        # Clean phone number (for individuals)
        if '@g.us' not in phone_or_group:
            clean_phone = phone_or_group.replace('+', '').replace(' ', '').replace('-', '')
        else:
            clean_phone = phone_or_group  # Keep group ID as-is
        
        # Encode message
        encoded_message = urllib.parse.quote(message)
        
        # Return WhatsApp URL
        return f"https://wa.me/{clean_phone}?text={encoded_message}"

def show_group_option_ui(tab_key):
    """Show UI for group send option - returns (is_group, group_id_or_none)"""
    send_to = st.radio(
        "Choose recipient type:",
        ["📱 Individual WhatsApp", "👥 WhatsApp Group"],
        key=f"{tab_key}_send_to",
        horizontal=True
    )
    
    if send_to == "👥 WhatsApp Group":
        st.info("💡 Send one message to your WhatsApp group")
        
        # Hardcoded group link
        default_group_link = "https://chat.whatsapp.com/2EnBnKZ2uiNJ26VpDWgOPH"
        
        # Initialize group_id with default
        group_id = default_group_link
        
        st.success("✅ Group link configured: Nikkang KK EPL Group")
        
        with st.expander("🔧 Advanced: Use Different Group (Optional)"):
            st.markdown("""
            **Default group is already set!** 
            
            Only change this if you want to send to a different group:
            """)
            
            custom_group_input = st.text_input(
                "Custom Group Link or Phone:",
                placeholder="Leave blank to use default group",
                help="Optional - only fill if sending to different group",
                key=f"{tab_key}_custom_group_id"
            )
            
            if custom_group_input:
                # Use custom input
                if "chat.whatsapp.com" in custom_group_input or "wa.me" in custom_group_input:
                    group_id = custom_group_input
                else:
                    group_id = custom_group_input.replace('+', '').replace(' ', '').replace('-', '')
        
        return True, group_id
    
    return False, None

def show_group_send_buttons(group_id, message, button_key, filename="group_message"):
    """Show both WhatsApp link and copy message buttons"""
    
    # Check if it's a group invite link
    is_invite_link = 'chat.whatsapp.com' in group_id if group_id else False
    
    if is_invite_link:
        # For invite links, emphasize copy/paste method
        st.success("✅ **Your edits are ready!** Follow the steps below:")
        
        # Step 1: Copy
        st.markdown("### 📋 Step 1: Copy Your Message")
        st.caption("👇 **Mobile:** Tap & hold, then tap 'Select All' → 'Copy'")
        st.caption("👇 **Desktop:** Click inside, press Ctrl+A (select all), then Ctrl+C (copy)")
        
        st.text_area(
            "Your message (with your edits):",
            value=message,
            height=200,
            key=f"{button_key}_copy_area",
            label_visibility="collapsed"
        )
        
        st.caption(f"📏 Message length: {len(message)} characters")
        
        # Step 2: Open WhatsApp
        st.markdown("---")
        st.markdown("### 🟢 Step 2: Open WhatsApp Group")
        
        notifier = WhatsAppNotifier(method='url')
        url = notifier.send_whatsapp_url(group_id, message)
        
        st.markdown(f"[🟢 **Click to Open WhatsApp Group**]({url})")
        st.caption("After copying above, click this link to open your group")
        
        # Step 3: Paste
        st.markdown("---")
        st.markdown("### 📝 Step 3: Paste & Send")
        st.caption("**Mobile:** Tap & hold in message field → Tap 'Paste' → Tap Send")
        st.caption("**Desktop:** Press Ctrl+V (or Cmd+V) → Press Enter")
        
    else:
        # For phone numbers, both methods work
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Generate WhatsApp Link", key=f"{button_key}_link", width='stretch', type="primary"):
                if not group_id:
                    st.warning("⚠️ No group phone entered. Use copy method instead →")
                else:
                    notifier = WhatsAppNotifier(method='url')
                    url = notifier.send_whatsapp_url(group_id, message)
                    
                    st.success("✅ Link generated!")
                    st.markdown(f"### 📲 [🟢 Open WhatsApp]({url})")
        
        with col2:
            st.markdown("### 📋 Copy Message")
        
        st.text_area(
            "Your message:",
            value=message,
            height=200,
            key=f"{button_key}_view2",
            label_visibility="collapsed"
        )
        st.caption(f"📏 {len(message)} characters")

# Info box
st.info("""
📱 **WhatsApp Web URLs (FREE)**

Generate clickable links that open WhatsApp with pre-filled messages.
Click each link to send messages one by one, or use bulk send to open all at once!
""")

st.markdown("---")

# Load participants
participants = dm.get_all_participants()

# Tabs for different notification types
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Prediction Reminders",
    "👋 Welcome Messages",
    "📊 Results Posted",
    "🏆 Weekly Winners",
    "🎯 KK Champions",
    "✉️ Custom Message"
])

# Tab 1: Prediction Reminders
with tab1:
    st.markdown("### 📋 Send Prediction Reminders")
    
    # Get current week from settings
    current_week = dm.get_current_week()
    
    col1, col2 = st.columns(2)
    
    with col1:
        week_number = st.number_input("Week Number:", min_value=1, max_value=38, value=current_week)
    
    with col2:
        deadline = st.text_input("Deadline:", value="Saturday, 10:00 PM")
    
    # Send option: Individual or Group
    st.markdown("#### 📤 Send To:")
    is_group, group_id = show_group_option_ui("reminder")
    
    if is_group:
        
        # Editable group message template
        st.markdown("#### ✏️ Edit Group Message")
        
        default_group_reminder = f"""🎯 *Nikkang KK EPL Prediction Reminder*

Hi everyone! 👋

⚽ Week {week_number} predictions are now open!

⏰ *Deadline:* {deadline}

📱 *Predictions Page:*
{base_url}

Please proceed to Prediction Page. Enter your nickname and last 4 digits of your phone number.

Good luck to all! 🍀

_Nikkang KK Admin Team_"""
        
        group_reminder_template = st.text_area(
            "Group Message:",
            value=default_group_reminder,
            height=250,
            key="group_reminder_msg",
            help="Edit this message as needed. Changes are saved automatically as you type."
        )
        
        # Add a button to trigger update (especially useful on mobile)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 **Mobile?** Tap 'Done Editing' button after making changes →")
        with col2:
            if st.button("✅ Done Editing", key="done_edit_reminder", width='stretch'):
                st.success("✅ Edits saved!")
        
        st.markdown("---")
        st.markdown("### 📤 Send to Group")
        
        # Group send buttons
        show_group_send_buttons(group_id, group_reminder_template, "group_reminder", f"reminder_week{week_number}")
    
    else:  # Individual WhatsApp
        # Editable message template
        st.markdown("#### ✏️ Edit Message Template")
        
        default_reminder = f"""🎯 *Nikkang KK EPL Prediction Reminder*

Hi {{name}}! 👋

⚽ Week {week_number} predictions are now open!

⏰ *Deadline:* {deadline}

📝 Submit your predictions here:
{{prediction_url}}

Good luck! 🍀

_Nikkang KK Admin Team_"""
        
        reminder_template = st.text_area(
            "Message Template:",
            value=default_reminder,
            height=250,
            help="Use {name} and {prediction_url} as placeholders. They will be replaced for each participant.",
            key="individual_reminder_msg"
        )
        
        st.caption("💡 Use `{name}` for participant name and `{prediction_url}` for their link")
        
        # Participant selection
        if participants:
            all_participants = st.checkbox("Send to all participants", value=True, key="reminder_all")
            
            if not all_participants:
                selected_names = st.multiselect(
                    "Select Participants:",
                    [p.get('name', 'Unknown') for p in participants]
                )
            else:
                st.info(f"Will send to all {len(participants)} participants")
                selected_names = []
        else:
            st.warning("No participants registered yet!")
        
        # Preview with sample data
        with st.expander("👁️ Preview Message"):
            preview = reminder_template.replace("{name}", "John Doe").replace("{prediction_url}", f"{base_url}?user_id=ABC123")
            st.code(preview, language=None)
        
        # Generate notifications
        if st.button("🚀 Generate Notifications", key="reminder_btn", width='stretch', type="primary"):
            if not participants:
                st.error("No participants to notify!")
            else:
                with st.spinner("Generating notifications..."):
                    # Filter participants
                    if all_participants:
                        selected_participants = participants
                    else:
                        selected_participants = [p for p in participants if p.get('name') in selected_names]
                    
                    if not selected_participants:
                        st.error("No participants selected!")
                    else:
                        notifier = WhatsAppNotifier(method='url')
                        results = []
                        
                        for participant in selected_participants:
                            prediction_url = f"{base_url}?user_id={participant.get('id', 'unknown')}"
                            
                            # Replace placeholders
                            message = reminder_template.replace("{name}", participant.get('name', 'Participant'))
                            message = message.replace("{prediction_url}", prediction_url)
                            
                            url = notifier.send_whatsapp_url(
                                participant.get('phone', ''), 
                                message
                            )
                            
                            results.append({
                                'Name': participant.get('name', 'Unknown'),
                                'Phone': participant.get('phone', 'Not provided'),
                                'WhatsApp Link': url
                            })
                        
                        st.success(f"✅ Generated {len(results)} reminder links!")
                        
                        # Show individual links (no bulk send option)
                        st.markdown("### 📲 Individual Links")
                        st.info("💡 Tip: Use Group send for everyone at once, or click individual links below for specific people")
                        
                        for idx, result in enumerate(results, 1):
                            col1, col2 = st.columns([3, 2])
                            with col1:
                                st.markdown(f"**{idx}. {result['Name']}**")
                                st.caption(f"📞 {result['Phone']}")
                            with col2:
                                st.markdown(f"[🟢 Send WhatsApp]({result['WhatsApp Link']})")
                            if idx < len(results):
                                st.markdown("---")

# Tab 2: Welcome Messages (AUTOMATED - NOT EDITABLE)
with tab2:
    st.markdown("### 👋 Send Welcome Messages")
    st.info("📌 Standard welcome message - automatically personalized with participant details")
    
    if participants:
        # Select new participants
        new_participants = st.multiselect(
            "Select New Participants to Welcome:",
            [p.get('name', 'Unknown') for p in participants],
            help="Select participants who just registered"
        )
        
        # Preview with first selected participant
        if new_participants:
            sample_participant = next((p for p in participants if p.get('name') == new_participants[0]), None)
            
            if sample_participant:
                sample_url = f"{base_url}?user_id={sample_participant.get('id', 'ABC123')}"
                sample_team = sample_participant.get('team', 'Not selected')
                sample_email = sample_participant.get('email', 'email@example.com')
                
                # Standard welcome message (NOT EDITABLE)
                sample_message = f"""👋 *Welcome to Nikkang KK EPL Prediction League!*

Hi {new_participants[0]}! 🎉

Thanks for joining our Premier League prediction competition!

👤 *Your Details:*
📧 Email: {sample_email}
⚽ Favorite Team: {sample_team}

🔗 *Your Personal Prediction Link:*
{sample_url}

📖 *How to Play:*
• Predict 10 matches each week
• Choose your Game of the Week (double points!)
• Exact Score (KK) = 6 pts (10 for GOTW)
• Correct Result = 3 pts (5 for GOTW)
• Competition runs in 4 rounds

🏆 *What You Can Win:*
• Weekly Winner recognition
• Round Champion titles
• Season Grand Champion
• KK Master (Most exact scores)

📱 *Quick Links:*
• Make Predictions: {base_url}
• View Leaderboard: {base_url}
• Check Results: {base_url}/4_Results

Good luck this season! May the best predictor win! ⚽🔥

_Nikkang KK Admin Team_"""
                
                with st.expander("👁️ Preview Message (Sample)"):
                    st.code(sample_message, language=None)
        
        if st.button("🚀 Generate Welcome Messages", key="welcome_btn", width='stretch', type="primary"):
            if not new_participants:
                st.error("Please select participants!")
            else:
                with st.spinner("Generating personalized welcome messages..."):
                    notifier = WhatsAppNotifier(method='url')
                    results = []
                    
                    for participant in participants:
                        if participant.get('name') in new_participants:
                            p_name = participant.get('name', 'Participant')
                            p_id = participant.get('id', 'unknown')
                            p_email = participant.get('email', 'email@example.com')
                            p_team = participant.get('team', 'Not selected')
                            registration_url = f"{base_url}?user_id={p_id}"
                            
                            # Standard welcome message with participant details
                            message = f"""👋 *Welcome to Nikkang KK EPL Prediction League!*

Hi {p_name}! 🎉

Thanks for joining our Premier League prediction competition!

👤 *Your Details:*
📧 Email: {p_email}
⚽ Favorite Team: {p_team}

🔗 *Your Personal Prediction Link:*
{registration_url}

📖 *How to Play:*
• Predict 10 matches each week
• Choose your Game of the Week (double points!)
• Exact Score (KK) = 6 pts (10 for GOTW)
• Correct Result = 3 pts (5 for GOTW)
• Competition runs in 4 rounds

🏆 *What You Can Win:*
• Weekly Winner recognition
• Round Champion titles
• Season Grand Champion
• KK Master (Most exact scores)

📱 *Quick Links:*
• Make Predictions: {base_url}
• View Leaderboard: {base_url}
• Check Results: {base_url}/4_Results

Good luck this season! May the best predictor win! ⚽🔥

_Nikkang KK Admin Team_"""
                            
                            url = notifier.send_whatsapp_url(
                                participant.get('phone', ''),
                                message
                            )
                            
                            results.append({
                                'Name': p_name,
                                'Phone': participant.get('phone', 'Not provided'),
                                'Email': p_email,
                                'Team': p_team,
                                'WhatsApp Link': url
                            })
                    
                    st.success(f"✅ Generated {len(results)} personalized welcome messages!")
                    display_bulk_send_interface(results, "Welcome Messages")
    else:
        st.warning("No participants registered yet!")

# Tab 3: Results Posted (AUTOMATED WITH LEADERBOARD DATA)
with tab3:
    st.markdown("### 📊 Weekly Results Notifications")
    st.info("📌 Automated message with complete scoring breakdown from leaderboard")
    
    # Get current week from settings
    current_week_results = dm.get_current_week()
    results_week = st.number_input("Week Number:", min_value=1, max_value=38, value=current_week_results, key="results_week")
    
    # Determine which stage this week belongs to
    if results_week <= 10:
        current_round = 1
        round_weeks = "1-10"
    elif results_week <= 20:
        current_round = 2
        round_weeks = "11-20"
    elif results_week <= 30:
        current_round = 3
        round_weeks = "21-30"
    else:
        current_round = 4
        round_weeks = "31-38"
    
    st.info(f"Week {results_week} is in **Stage {current_round}** (Weeks {round_weeks})")
    
    # Send option: Individual or Group
    st.markdown("#### 📤 Send To:")
    is_group, group_id = show_group_option_ui("results")
    
    if is_group:
        # GROUP SUMMARY MESSAGE
        st.markdown("#### ✏️ Edit Group Summary Message")
        
        default_group_results = f"""📊 *Week {results_week} Results Summary*

Hi everyone! 👋

The results for Week {results_week} (Stage {current_round}) are in! 🎉

Check your personal DM for your detailed breakdown!

View full leaderboard:
{base_url}

_Nikkang KK Admin Team_"""
        
        group_results_msg = st.text_area(
            "Group Summary Message:",
            value=default_group_results,
            height=200,
            key="group_results_msg",
            help="This is a simple announcement. Detailed results sent individually."
        )
        
        with st.expander("👁️ Preview Group Message"):
            st.code(group_results_msg, language=None)
        
        # Group send buttons
        show_group_send_buttons(group_id, group_results_msg, "group_results", f"results_week{results_week}")
        
        st.info("💡 Tip: After group summary, switch to Individual for detailed breakdowns!")
    
    else:
        # INDIVIDUAL DETAILED RESULTS
        # Button to generate results
        if st.button("📊 Generate Results Notifications", key="results_btn", width='stretch', type="primary"):
            if not participants:
                st.error("No participants to notify!")
            else:
                with st.spinner("Calculating scores from leaderboard..."):
                    try:
                        # Get full leaderboard data
                        from utils.data_manager import DataManager
                        dm = DataManager()
                        
                        # Load stage scores
                        import json
                        from pathlib import Path
                        
                        score_file = Path("nikkang_data/round_scores.json")
                        round_scores = {}
                        if score_file.exists():
                            try:
                                with open(score_file, 'r') as f:
                                    round_scores = json.load(f)
                            except:
                                pass
                        
                        # Define rounds
                        ROUNDS = {
                            1: {"weeks": list(range(1, 11)), "key": "round_1"},
                            2: {"weeks": list(range(11, 21)), "key": "round_2"},
                            3: {"weeks": list(range(21, 31)), "key": "round_3"},
                            4: {"weeks": list(range(31, 39)), "key": "round_4"},
                        }
                        
                        notifier = WhatsAppNotifier(method='url')
                        results_list = []
                        
                        for participant in participants:
                            p_id = participant.get('id', '')
                            p_name = participant.get('name', 'Participant')
                        
                            # Calculate weekly points for this specific week
                            predictions = dm.load_predictions()
                            results = dm.load_results()
                            all_matches = dm.get_all_matches()
                            user_preds = predictions.get(p_id, {})
                        
                            weekly_points = 0
                            weekly_kk = 0
                            weekly_correct = 0
                            weekly_matches = 0
                        
                            for match in all_matches:
                                if match.get('week') == results_week:
                                    mid = match.get('id', '')
                                    if mid in results and mid in user_preds:
                                        result = results[mid]
                                        pred = user_preds[mid]
                                        is_gotw = match.get('gotw', False)
                                    
                                        points = dm.calculate_points(
                                            pred.get('home_score', -1), pred.get('away_score', -1),
                                            result.get('home_score', -2), result.get('away_score', -2), is_gotw
                                        )
                                        weekly_points += points
                                        weekly_matches += 1
                                    
                                        if pred.get('home_score') == result.get('home_score') and pred.get('away_score') == result.get('away_score'):
                                            weekly_kk += 1
                                    
                                        if points > 0:
                                            weekly_correct += 1
                        
                            # Calculate stage and season totals
                            season_points = 0
                            season_kk = 0
                            round_points = 0
                            round_kk = 0
                        
                            for round_num in [1, 2, 3, 4]:
                                round_info = ROUNDS[round_num]
                                round_key = round_info['key']
                                is_locked = round_scores.get(f"{round_key}_locked", False)
                            
                                if is_locked:
                                    manual = round_scores.get(round_key, {}).get(p_id, {})
                                    pts = manual.get('points', 0)
                                    kk = manual.get('kk_count', 0)
                                else:
                                    pts = 0
                                    kk = 0
                                    for match in all_matches:
                                        week = match.get('week', 0)
                                        if week in round_info['weeks']:
                                            mid = match.get('id', '')
                                            if mid in results and mid in user_preds:
                                                result = results[mid]
                                                pred = user_preds[mid]
                                                is_gotw = match.get('gotw', False)
                                            
                                                points = dm.calculate_points(
                                                    pred.get('home_score', -1), pred.get('away_score', -1),
                                                    result.get('home_score', -2), result.get('away_score', -2), is_gotw
                                                )
                                                pts += points
                                            
                                                if pred.get('home_score') == result.get('home_score') and pred.get('away_score') == result.get('away_score'):
                                                    kk += 1
                            
                                season_points += pts
                                season_kk += kk
                            
                                if round_num == current_round:
                                    round_points = pts
                                    round_kk = kk
                        
                            # Get ranking
                            all_scores = []
                            for p in participants:
                                pid = p.get('id', '')
                                total = 0
                                for sn in [1, 2, 3, 4]:
                                    si = ROUNDS[sn]
                                    sk = si['key']
                                    isl = round_scores.get(f"{sk}_locked", False)
                                    if isl:
                                        m = round_scores.get(sk, {}).get(pid, {})
                                        total += m.get('points', 0)
                                    else:
                                        for m in all_matches:
                                            w = m.get('week', 0)
                                            if w in si['weeks']:
                                                mid = m.get('id', '')
                                                if mid in results and mid in predictions.get(pid, {}):
                                                    r = results[mid]
                                                    pr = predictions.get(pid, {}).get(mid, {})
                                                    ig = m.get('gotw', False)
                                                    pts = dm.calculate_points(
                                                        pr.get('home_score', -1), pr.get('away_score', -1),
                                                        r.get('home_score', -2), r.get('away_score', -2), ig
                                                    )
                                                    total += pts
                                all_scores.append(total)
                        
                            all_scores.sort(reverse=True)
                            rank = all_scores.index(season_points) + 1 if season_points in all_scores else len(participants)
                        
                            # Generate automated message
                            message = f"""📊 *Week {results_week} Results - Your Performance*

    Hi {p_name}! 👋

    The results for Week {results_week} are in! Here's your complete breakdown:

    ━━━━━━━━━━━━━━━━━━━━━━
    📈 *WEEK {results_week} PERFORMANCE*
    ━━━━━━━━━━━━━━━━━━━━━━
    🏆 Points: {weekly_points}
    🎯 Exact Scores (KK): {weekly_kk}
    ✅ Correct Results: {weekly_correct}/{weekly_matches}

    ━━━━━━━━━━━━━━━━━━━━━━
    📊 *STAGE {current_round} PROGRESS*
    ━━━━━━━━━━━━━━━━━━━━━━
    (Weeks {round_weeks})
    🏆 Round Points: {round_points}
    🎯 Round KK: {round_kk}

    ━━━━━━━━━━━━━━━━━━━━━━
    🏅 *SEASON TOTALS*
    ━━━━━━━━━━━━━━━━━━━━━━
    🏆 Total Points: {season_points}
    📍 Current Rank: #{rank} of {len(participants)}
    🎯 Total KK (Season): {season_kk}

    ━━━━━━━━━━━━━━━━━━━━━━

    {"🎉 Great week! Keep it up!" if weekly_points >= 15 else "💪 Keep pushing for higher scores!"}

    🔗 View full leaderboard:
    {base_url}

    _Nikkang KK Admin Team_"""
                        
                            url = notifier.send_whatsapp_url(
                                participant.get('phone', ''),
                                message
                            )
                        
                            results_list.append({
                                'Name': p_name,
                                'Phone': participant.get('phone', 'Not provided'),
                                'Week Pts': weekly_points,
                                'Week KK': weekly_kk,
                                'Round Pts': round_points,
                                'Season Pts': season_points,
                                'Rank': rank,
                                'WhatsApp Link': url
                            })
                        
                        st.success(f"✅ Generated {len(results_list)} personalized result notifications!")
                        
                        # Show summary stats
                        st.markdown("### 📊 Summary Statistics")
                        import pandas as pd
                        summary_df = pd.DataFrame(results_list)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Avg Week Score", f"{summary_df['Week Pts'].mean():.1f}")
                        with col2:
                            st.metric("Total KK This Week", summary_df['Week KK'].sum())
                        with col3:
                            st.metric("Highest Week Score", summary_df['Week Pts'].max())
                        with col4:
                            st.metric("Participants", len(results_list))
                        
                        # Display bulk send interface
                        display_bulk_send_interface(results_list, "Results Notifications")
                        
                        # Show preview of one message
                        with st.expander("👁️ View Sample Message"):
                            if results_list:
                                sample = results_list[0]
                                # Reconstruct sample message for preview
                                st.code(f"""Sample message for {sample['Name']}:

Week {results_week} Points: {sample['Week Pts']}
Week {results_week} KK: {sample['Week KK']}
Stage {current_round} Points: {sample['Round Pts']}
Season Points: {sample['Season Pts']}
Current Rank: #{sample['Rank']}""", language=None)
                    
                    except Exception as e:
                        st.error(f"Error generating results: {str(e)}")
                        st.info("Make sure results have been entered for this week in Results Management page.")

# Tab 4: Weekly Winners (AUTOMATED - NOT EDITABLE)
with tab4:
    st.markdown("### 🏆 Congratulate Weekly Winners")
    st.info("📌 Standard message - automatically personalized for the winner")
    
    # Get current week from settings
    current_week_winner = dm.get_current_week()
    week_winner = st.number_input("Week Number:", min_value=1, max_value=38, value=current_week_winner, key="winner_week")
    
    if participants:
        winner_name = st.selectbox(
            "Select Week Winner:",
            [p.get('name', 'Unknown') for p in participants]
        )
        
        winner_points = st.number_input("Winner's Points:", min_value=0, value=18)
        
        # Send option: Individual or Group
        st.markdown("#### 📤 Send To:")
        is_group, group_id = show_group_option_ui("winner")
        
        if is_group:
            # GROUP ANNOUNCEMENT
            group_winner_msg = f"""🏆 *Week {week_winner} Winner Announcement!*

Congratulations to *{winner_name}*! 🎉

Amazing performance this week with *{winner_points} points*!

Keep up the great predictions everyone! 💪

View leaderboard:
{base_url}

_Nikkang KK Admin Team_"""
            
            with st.expander("👁️ Preview Group Message"):
                st.code(group_winner_msg, language=None)
            
            # Group send buttons
            show_group_send_buttons(group_id, group_winner_msg, "group_winner", f"winner_week{week_winner}")
        
        else:
            # INDIVIDUAL MESSAGE TO WINNER
            # Standard message template (NOT EDITABLE)
            winner_message = f"""🏆 *Congratulations Week {week_winner} Winner!*

🎉 *{winner_name}* 🎉

You're the champion of Week {week_winner} with *{winner_points} points*!

Amazing predictions! Keep it up! 💪

Check the leaderboard:
{base_url}

_Nikkang KK Admin Team_"""
            
            # Preview
            with st.expander("👁️ Preview Message"):
                st.code(winner_message, language=None)
            
            if st.button("🚀 Send Winner Notification", key="winner_btn", width='stretch', type="primary"):
                winner = next((p for p in participants if p.get('name') == winner_name), None)
                
                if winner:
                    notifier = WhatsAppNotifier(method='url')
                    
                    url = notifier.send_whatsapp_url(
                        winner.get('phone', ''),
                        winner_message
                    )
                    
                    st.success(f"✅ Winner notification generated!")
                    st.markdown(f"### 📲 [🟢 Click Here to Open WhatsApp]({url})")
                    st.caption(f"📞 {winner.get('phone', 'No phone')}")
    else:
        st.warning("No participants registered yet!")

# Tab 5: KK Champions (AUTOMATED - NOT EDITABLE)
with tab5:
    st.markdown("### 🎯 Congratulate KK Champions")
    st.info("📌 Standard message for Kemut Keliling (Exact Score) achievements")
    
    # Get current week from settings
    current_week_kk = dm.get_current_week()
    kk_week = st.number_input("Week Number:", min_value=1, max_value=38, value=current_week_kk, key="kk_week")
    
    if participants:
        kk_champion = st.selectbox(
            "Select KK Champion:",
            [p.get('name', 'Unknown') for p in participants],
            key="kk_champion_select"
        )
        
        kk_count = st.number_input("Number of Exact Scores (KK):", min_value=1, value=3, key="kk_count")
        
        # Send option: Individual or Group
        st.markdown("#### 📤 Send To:")
        is_group, group_id = show_group_option_ui("kk")
        
        if is_group:
            # GROUP ANNOUNCEMENT
            group_kk_msg = f"""🎯 *KK Champion of Week {kk_week}!*

Amazing performance by *{kk_champion}*! 🏅

Scored *{kk_count} exact predictions* this week!

That's the Kemut Keliling (KK) spirit! 🔥

Keep those predictions sharp everyone! 💪

View leaderboard:
{base_url}

_Nikkang KK Admin Team_"""
            
            with st.expander("👁️ Preview Group Message"):
                st.code(group_kk_msg, language=None)
            
            # Group send buttons
            show_group_send_buttons(group_id, group_kk_msg, "group_kk", f"kk_week{kk_week}")
        
        else:
            # INDIVIDUAL MESSAGE TO CHAMPION
            # Standard KK message (NOT EDITABLE)
            kk_message = f"""🎯 *Kemut Keliling Champion!*

🏅 *{kk_champion}* 🏅

Incredible! You scored *{kk_count} exact predictions* in Week {kk_week}!

That's the Kemut Keliling (KK) spirit! Your prediction skills are on fire! 🔥

Keep those exact scores coming! 💪

Check your ranking:
{base_url}

_Nikkang KK Admin Team_"""
            
            # Preview
            with st.expander("👁️ Preview Message"):
                st.code(kk_message, language=None)
            
            if st.button("🚀 Send KK Champion Notification", key="kk_btn", width='stretch', type="primary"):
                champion = next((p for p in participants if p.get('name') == kk_champion), None)
                
                if champion:
                    notifier = WhatsAppNotifier(method='url')
                    
                    url = notifier.send_whatsapp_url(
                        champion.get('phone', ''),
                        kk_message
                    )
                    
                    st.success(f"✅ KK Champion notification generated!")
                    st.markdown(f"### 📲 [🟢 Click Here to Open WhatsApp]({url})")
                    st.caption(f"📞 {champion.get('phone', 'No phone')}")
    else:
        st.warning("No participants registered yet!")

# Tab 6: Custom Message
with tab6:
    st.markdown("### ✉️ Send Custom Message")
    
    # Send option: Individual or Group
    st.markdown("#### 📤 Send To:")
    is_group, group_id = show_group_option_ui("custom")
    
    if is_group:
        # GROUP CUSTOM MESSAGE
        st.markdown("#### ✏️ Your Custom Group Message")
        
        custom_group_message = st.text_area(
            "Group Message:",
            height=250,
            placeholder="Enter your custom message for the group...",
            key="custom_group_msg"
        )
        
        # Preview
        if custom_group_message:
            with st.expander("👁️ Preview Group Message"):
                st.code(custom_group_message, language=None)
            
            # Group send buttons
            show_group_send_buttons(group_id, custom_group_message, "custom_group", "custom_message")
        else:
            st.warning("⚠️ Please enter a message first")
    
    else:
        # INDIVIDUAL CUSTOM MESSAGES
        # Participant selection
        all_custom = st.checkbox("Send to all participants", value=True, key="custom_all")
        
        if not all_custom and participants:
            custom_recipients = st.multiselect(
                "Select Recipients:",
                [p.get('name', 'Unknown') for p in participants]
            )
        else:
            custom_recipients = []
        
        # Custom message
        custom_message = st.text_area(
            "Your Message:",
            height=200,
            placeholder="Enter your custom message here...",
            key="custom_individual_msg"
        )
        
        # Preview
        if custom_message:
            st.markdown("#### 📝 Message Preview:")
            st.code(custom_message, language=None)
        
        if st.button("🚀 Generate Custom Notifications", key="custom_btn", width='stretch', type="primary"):
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
                        selected_participants = [p for p in participants if p.get('name') in custom_recipients]
                    
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
                                'Name': participant.get('name', 'Unknown'),
                                'Phone': participant.get('phone', 'Not provided'),
                                'WhatsApp Link': url
                            })
                        
                        st.success(f"✅ Generated {len(results)} custom message links!")
                        
                        # Show individual links (no bulk send option)
                        st.markdown("### 📲 Individual Links")
                        st.info("💡 Tip: Use Group send for announcements, or click individual links below")
                        
                        for idx, result in enumerate(results, 1):
                            col1, col2 = st.columns([3, 2])
                            with col1:
                                st.markdown(f"**{idx}. {result['Name']}**")
                                st.caption(f"📞 {result['Phone']}")
                            with col2:
                                st.markdown(f"[🟢 Send WhatsApp]({result['WhatsApp Link']})")
                            if idx < len(results):
                                st.markdown("---")

st.markdown("---")

# Tips section
st.markdown("### 💡 Tips for Effective Messaging")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Use Group Send For:**
    - ✅ General announcements
    - ✅ Prediction reminders
    - ✅ Results summaries
    - ✅ Winner celebrations
    - ✅ Quick updates to everyone
    """)

with col2:
    st.markdown("""
    **Use Individual For:**
    - ✅ Personalized data (welcome, results)
    - ✅ Specific people only
    - ✅ Private information
    - ✅ Detailed breakdowns
    - ✅ Unique links needed
    """)

st.markdown("---")
st.caption("Nikkang KK - EPL Prediction Competition 2025/26")
