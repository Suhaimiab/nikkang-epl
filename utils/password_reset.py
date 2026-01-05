"""
Password Reset System for Nikkang KK EPL Prediction App
Handles forgot password with email validation and temporary password generation
"""

import streamlit as st
import hashlib
import json
import secrets
import string
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PARTICIPANTS_FILE = Path("nikkang_data/participants.json")
RESET_TOKENS_FILE = Path("nikkang_data/password_reset_tokens.json")

# Token validity duration (30 minutes)
TOKEN_VALIDITY_MINUTES = 30


def generate_reset_token() -> str:
    """Generate a secure 6-digit reset code"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def generate_temporary_password(length: int = 10) -> str:
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_participants() -> dict:
    """Load participants from JSON file"""
    if PARTICIPANTS_FILE.exists():
        try:
            with open(PARTICIPANTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading participants: {e}")
            return {}
    return {}


def save_participants(participants: dict) -> bool:
    """Save participants to JSON file"""
    try:
        PARTICIPANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PARTICIPANTS_FILE, 'w') as f:
            json.dump(participants, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving participants: {e}")
        return False


def load_reset_tokens() -> dict:
    """Load password reset tokens"""
    if RESET_TOKENS_FILE.exists():
        try:
            with open(RESET_TOKENS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_reset_tokens(tokens: dict) -> bool:
    """Save password reset tokens"""
    try:
        RESET_TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RESET_TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        return True
    except:
        return False


def cleanup_expired_tokens():
    """Remove expired reset tokens"""
    tokens = load_reset_tokens()
    current_time = datetime.now()
    
    # Remove expired tokens
    valid_tokens = {}
    for email, token_data in tokens.items():
        expiry = datetime.fromisoformat(token_data['expires_at'])
        if expiry > current_time:
            valid_tokens[email] = token_data
    
    if len(valid_tokens) < len(tokens):
        save_reset_tokens(valid_tokens)


def find_participant_by_email(email: str) -> Optional[tuple]:
    """Find participant by email address"""
    participants = load_participants()
    email_lower = email.lower().strip()
    
    for user_id, data in participants.items():
        participant_email = data.get('email', '').lower().strip()
        if participant_email == email_lower:
            return user_id, data
    
    return None


def find_participant_by_nickname(nickname: str) -> Optional[tuple]:
    """Find participant by nickname"""
    participants = load_participants()
    nickname_lower = nickname.lower().strip()
    
    for user_id, data in participants.items():
        display_name = data.get('display_name', '').lower().strip()
        name = data.get('name', '').lower().strip()
        
        if display_name == nickname_lower or name == nickname_lower:
            return user_id, data
    
    return None


def create_reset_token(email: str) -> Optional[str]:
    """Create a password reset token for email"""
    # Verify email exists
    participant = find_participant_by_email(email)
    if not participant:
        return None
    
    # Generate token
    token = generate_reset_token()
    
    # Save token with expiry
    tokens = load_reset_tokens()
    expiry_time = datetime.now() + timedelta(minutes=TOKEN_VALIDITY_MINUTES)
    
    tokens[email.lower().strip()] = {
        'token': token,
        'created_at': datetime.now().isoformat(),
        'expires_at': expiry_time.isoformat(),
        'used': False
    }
    
    save_reset_tokens(tokens)
    return token


def verify_reset_token(email: str, token: str) -> bool:
    """Verify if reset token is valid"""
    cleanup_expired_tokens()
    
    tokens = load_reset_tokens()
    email_lower = email.lower().strip()
    
    if email_lower not in tokens:
        return False
    
    token_data = tokens[email_lower]
    
    # Check if already used
    if token_data.get('used', False):
        return False
    
    # Check if expired
    expiry = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expiry:
        return False
    
    # Verify token matches
    return token_data['token'] == token


def mark_token_as_used(email: str):
    """Mark reset token as used"""
    tokens = load_reset_tokens()
    email_lower = email.lower().strip()
    
    if email_lower in tokens:
        tokens[email_lower]['used'] = True
        save_reset_tokens(tokens)


def reset_password_with_token(email: str, token: str, new_password: str) -> bool:
    """Reset password using verification token"""
    # Verify token
    if not verify_reset_token(email, token):
        return False
    
    # Find participant
    participant = find_participant_by_email(email)
    if not participant:
        return False
    
    user_id, _ = participant
    
    # Update password
    participants = load_participants()
    participants[user_id]['password_hash'] = hash_password(new_password)
    participants[user_id]['password_changed_at'] = datetime.now().isoformat()
    
    if save_participants(participants):
        # Mark token as used
        mark_token_as_used(email)
        return True
    
    return False


def send_reset_email(email: str, token: str, participant_name: str) -> bool:
    """
    Send password reset email
    Configure your SMTP settings in Streamlit secrets or environment variables
    """
    
    # Get email configuration from Streamlit secrets
    try:
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        smtp_username = st.secrets.get("SMTP_USERNAME", "")
        smtp_password = st.secrets.get("SMTP_PASSWORD", "")
        from_email = st.secrets.get("FROM_EMAIL", smtp_username)
        
        if not smtp_username or not smtp_password:
            st.warning("⚠️ Email not configured. Show reset code to user instead.")
            return False
            
    except:
        st.warning("⚠️ Email configuration not found in secrets.")
        return False
    
    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Nikkang KK EPL - Password Reset Code"
    msg['From'] = from_email
    msg['To'] = email
    
    # Email body
    text = f"""
    Hi {participant_name},
    
    You requested to reset your password for Nikkang KK EPL Prediction Competition.
    
    Your password reset code is: {token}
    
    This code will expire in {TOKEN_VALIDITY_MINUTES} minutes.
    
    If you didn't request this reset, please ignore this email.
    
    Best regards,
    Nikkang KK EPL Team
    """
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2E7D32;">🔐 Password Reset Request</h2>
          
          <p>Hi <strong>{participant_name}</strong>,</p>
          
          <p>You requested to reset your password for <strong>Nikkang KK EPL Prediction Competition</strong>.</p>
          
          <div style="background-color: #E8F5E9; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #666;">Your reset code is:</p>
            <h1 style="margin: 10px 0; color: #2E7D32; font-size: 36px; letter-spacing: 5px;">{token}</h1>
          </div>
          
          <p style="color: #666; font-size: 14px;">
            ⏰ This code will expire in <strong>{TOKEN_VALIDITY_MINUTES} minutes</strong>.
          </p>
          
          <p style="color: #666; font-size: 14px;">
            If you didn't request this reset, please ignore this email and your password will remain unchanged.
          </p>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
          
          <p style="color: #999; font-size: 12px; text-align: center;">
            Nikkang KK EPL Prediction Competition<br>
            This is an automated message, please do not reply.
          </p>
        </div>
      </body>
    </html>
    """
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False


def validate_password_strength(password: str) -> tuple:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


# Session state helpers
def init_reset_session():
    """Initialize session state for password reset"""
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 'request'  # request, verify, complete
    if 'reset_email' not in st.session_state:
        st.session_state.reset_email = ''
    if 'reset_token_sent' not in st.session_state:
        st.session_state.reset_token_sent = False


def reset_session():
    """Clear password reset session"""
    st.session_state.reset_step = 'request'
    st.session_state.reset_email = ''
    st.session_state.reset_token_sent = False
