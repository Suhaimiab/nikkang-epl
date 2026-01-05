"""
Forgot Password Page - Participant Password Reset
Nikkang KK EPL Prediction Competition
FIXED VERSION - Shows reset code properly in fallback mode
"""

import streamlit as st
from utils.password_reset import (
    init_reset_session,
    reset_session,
    find_participant_by_email,
    find_participant_by_nickname,
    create_reset_token,
    verify_reset_token,
    reset_password_with_token,
    send_reset_email,
    validate_password_strength,
    TOKEN_VALIDITY_MINUTES
)

# Page config
st.set_page_config(
    page_title="Forgot Password - Nikkang KK EPL",
    page_icon="🔐",
    layout="centered"
)

# Initialize session
init_reset_session()

# Header
st.title("🔐 Forgot Password")
st.markdown("---")


def show_request_form():
    """Step 1: Request password reset"""
    
    st.info("📧 Enter your registered email or nickname to receive a password reset code")
    
    with st.form("password_reset_request"):
        # Option to use email or nickname
        lookup_method = st.radio(
            "How would you like to identify your account?",
            ["Email Address", "Nickname"],
            horizontal=True
        )
        
        if lookup_method == "Email Address":
            identifier = st.text_input(
                "📧 Registered Email",
                placeholder="your.email@example.com",
                help="Enter the email address you used during registration"
            )
        else:
            identifier = st.text_input(
                "👤 Nickname",
                placeholder="Your nickname",
                help="Enter your display name/nickname"
            )
        
        submit = st.form_submit_button("🔍 Request Reset Code", use_container_width=True)
        
        if submit:
            if not identifier:
                st.error("Please enter your email or nickname")
                st.stop()
            
            identifier = identifier.strip()
            
            # Find participant
            if lookup_method == "Email Address":
                participant = find_participant_by_email(identifier)
                email_to_use = identifier
            else:
                participant = find_participant_by_nickname(identifier)
                if participant:
                    _, data = participant
                    email_to_use = data.get('email', '')
                else:
                    email_to_use = None
            
            if not participant:
                st.error(f"❌ No account found with that {lookup_method.lower()}")
                st.info("💡 Make sure you're using the same email/nickname you registered with")
                st.stop()
            
            user_id, user_data = participant
            participant_name = user_data.get('display_name', user_data.get('name', 'Participant'))
            
            if not email_to_use or '@' not in email_to_use:
                st.error("❌ No valid email found for this account. Please contact admin.")
                st.stop()
            
            # Create reset token
            token = create_reset_token(email_to_use)
            
            if not token:
                st.error("❌ Failed to create reset token. Please try again.")
                st.stop()
            
            # Try to send email
            email_sent = send_reset_email(email_to_use, token, participant_name)
            
            # Store data in session for next step
            st.session_state.reset_email = email_to_use
            st.session_state.reset_token = token  # Store token for display
            st.session_state.reset_token_sent = True
            st.session_state.email_sent = email_sent
            st.session_state.reset_step = 'show_code'
            st.rerun()


def show_code_display():
    """Step 1.5: Show reset code (fallback mode) or email confirmation"""
    
    email = st.session_state.reset_email
    token = st.session_state.get('reset_token', '******')
    email_sent = st.session_state.get('email_sent', False)
    
    if email_sent:
        # Email was sent successfully
        st.success(f"✅ Reset code sent to {email}")
        st.info(f"📧 Check your email for the 6-digit reset code (valid for {TOKEN_VALIDITY_MINUTES} minutes)")
    else:
        # Email NOT sent - show code on screen (fallback)
        st.warning("⚠️ Email delivery is not configured")
        st.success("✅ Reset code generated successfully!")
        
        # Display code in a prominent box
        st.markdown("---")
        st.markdown("### 🔑 Your Reset Code:")
        st.markdown(f"""
        <div style='background-color: #E8F5E9; padding: 30px; border-radius: 10px; text-align: center; border: 2px solid #4CAF50;'>
            <p style='margin: 0; font-size: 16px; color: #666;'>Enter this code in the next step:</p>
            <h1 style='margin: 15px 0; color: #2E7D32; font-size: 48px; letter-spacing: 10px; font-family: monospace;'>{token}</h1>
            <p style='margin: 0; font-size: 14px; color: #666;'>⏰ Valid for {TOKEN_VALIDITY_MINUTES} minutes</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        st.info("💡 **TIP:** Screenshot or write down this code before proceeding")
    
    st.markdown("---")
    
    # Button to continue (outside any form)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Continue to Reset Password", type="primary", use_container_width=True, key="continue_btn"):
            st.session_state.reset_step = 'verify'
            st.rerun()
    
    st.markdown("---")
    if st.button("🔙 Start Over", use_container_width=False, key="back_btn"):
        reset_session()
        st.rerun()


def show_verification_form():
    """Step 2: Verify token and reset password"""
    
    email = st.session_state.reset_email
    
    st.success(f"📧 Reset code sent to: {email}")
    st.info("🔑 Enter the 6-digit code you received and create a new password")
    
    with st.form("verify_and_reset"):
        # Reset code input
        reset_code = st.text_input(
            "🔢 6-Digit Reset Code",
            max_chars=6,
            placeholder="123456",
            help=f"Check your email or screen above for the reset code (valid for {TOKEN_VALIDITY_MINUTES} minutes)"
        )
        
        st.markdown("---")
        st.markdown("### 🆕 Create New Password")
        
        # New password
        new_password = st.text_input(
            "🔒 New Password",
            type="password",
            help="Must be at least 8 characters with uppercase, lowercase, and numbers"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirm New Password",
            type="password"
        )
        
        # Password strength indicator
        if new_password:
            is_valid, message = validate_password_strength(new_password)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.warning(f"⚠️ {message}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("✅ Reset Password", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            reset_session()
            st.rerun()
        
        if submit:
            # Validation
            if not reset_code or len(reset_code) != 6:
                st.error("❌ Please enter the 6-digit reset code")
                st.stop()
            
            if not new_password or not confirm_password:
                st.error("❌ Please enter and confirm your new password")
                st.stop()
            
            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
                st.stop()
            
            # Validate password strength
            is_valid, message = validate_password_strength(new_password)
            if not is_valid:
                st.error(f"❌ {message}")
                st.stop()
            
            # Verify token and reset password
            success = reset_password_with_token(email, reset_code, new_password)
            
            if success:
                st.session_state.reset_step = 'complete'
                st.rerun()
            else:
                st.error("❌ Invalid or expired reset code")
                st.info("💡 Click button below to request a new code")
    
    # Button outside form for requesting new code
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Request New Code", use_container_width=True, key="request_new"):
            reset_session()
            st.rerun()


def show_completion():
    """Step 3: Password reset complete"""
    
    st.balloons()
    
    st.success("🎉 Password Reset Successful!")
    
    st.markdown("""
    ### ✅ Your password has been updated
    
    You can now login with your new password.
    """)
    
    st.info("📱 Go to the **Predictions** page to login with your new password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Go to Home", use_container_width=True):
            reset_session()
            st.switch_page("app.py")
    
    with col2:
        if st.button("📊 Go to Predictions", use_container_width=True):
            reset_session()
            st.switch_page("pages/3_Predictions.py")
    
    st.markdown("---")
    
    if st.button("🔄 Reset Another Password"):
        reset_session()
        st.rerun()


# Main flow
if st.session_state.reset_step == 'request':
    show_request_form()

elif st.session_state.reset_step == 'show_code':
    show_code_display()

elif st.session_state.reset_step == 'verify':
    show_verification_form()

elif st.session_state.reset_step == 'complete':
    show_completion()

# Help section
st.markdown("---")

with st.expander("❓ Help & Troubleshooting"):
    st.markdown(f"""
    ### Common Issues:
    
    **"No account found"**
    - Make sure you're using the email/nickname you registered with
    - Check for typos in your email address
    - Contact admin if you're still having issues
    
    **"Invalid or expired reset code"**
    - Reset codes expire after {TOKEN_VALIDITY_MINUTES} minutes
    - Make sure you entered the code correctly (6 digits)
    - Request a new code if yours has expired
    
    **"Email not received"**
    - Code is displayed on screen above (no email needed!)
    - If email was supposed to be sent, check spam/junk folder
    - Use the code shown on screen instead
    
    **"Password requirements not met"**
    - Minimum 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one number (0-9)
    
    ### Need More Help?
    
    Contact admin via WhatsApp or email for assistance.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>🔐 Secure Password Reset | Nikkang KK EPL Prediction Competition</p>
</div>
""", unsafe_allow_html=True)
