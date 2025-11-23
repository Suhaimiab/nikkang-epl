"""
WhatsApp messaging and link generation utilities
"""

import urllib.parse

def generate_participant_link(participant_id: str, week: int = None, base_url: str = "http://localhost:8501") -> str:
    """Generate unique participant link"""
    link = f"{base_url}/?id={participant_id}"
    if week:
        link += f"&week={week}"
    return link

def generate_whatsapp_message(participant: dict, link: str, current_week: int = 1) -> str:
    """Generate WhatsApp message for participant"""
    msg = f"""🏆 *NIKKANG KK - EPL PREDICTIONS*

Welcome {participant['name']}! 🎉

You're registered for the EPL prediction competition.

📱 *Your Personal Prediction Link:*
{link}

Use this link to submit your predictions each week.
Bookmark it for easy access!

Current Week: {current_week}
Deadline: Before first match kicks off

Good luck! 🍀"""
    
    return msg

def get_whatsapp_url(phone: str, message: str) -> str:
    """Generate WhatsApp URL with pre-filled message"""
    # Clean phone number
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # URL encode message
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp URL
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    return whatsapp_url

def copy_to_clipboard_button(text: str, label: str = "📋 Copy to Clipboard"):
    """Create a button that copies text to clipboard"""
    import streamlit as st
    
    # Using Streamlit's copy button (available in newer versions)
    st.code(text, language=None)
    
    # Fallback: display for manual copy
    st.caption("👆 Click to select and copy")
