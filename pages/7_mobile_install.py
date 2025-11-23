"""
Mobile App Installation Instructions
Shows users how to install the web app as a mobile app
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Install as App - Nikkang KK",
    page_icon="📱",
    layout="wide"
)

# Import branding utility if available
try:
    from utils.branding import (
        setup_page,
        display_page_header,
        display_footer,
        inject_custom_css
    )
    inject_custom_css()
except:
    pass

# Custom CSS for this page
st.markdown("""
<style>
    .install-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .step-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 40px;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    
    .benefit-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #28a745;
    }
    
    .screenshot-placeholder {
        background: #e9ecef;
        border: 2px dashed #adb5bd;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        color: #6c757d;
        margin: 1rem 0;
    }
    
    .platform-tab {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        margin: 0.25rem;
        background: #f8f9fa;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .platform-tab:hover {
        background: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Page header
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📱 Install as Mobile App</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Get the full app experience on your phone!
    </p>
</div>
""", unsafe_allow_html=True)

# Benefits section
st.markdown("## ✨ Why Install as an App?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="benefit-item">
        <h3>🚀 Faster Access</h3>
        <p>Launch directly from your home screen - no browser needed!</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="benefit-item">
        <h3>📱 Full Screen</h3>
        <p>Enjoy a native app experience without browser bars!</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="benefit-item">
        <h3>🎯 Easy to Find</h3>
        <p>App icon on your home screen - always at your fingertips!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Platform selection
st.markdown("## 📲 Choose Your Device")

platform = st.radio(
    "",
    ["📱 iPhone / iPad (iOS)", "🤖 Android Phone / Tablet"],
    horizontal=True
)

st.markdown("---")

# iPhone/iPad Instructions
if "iPhone" in platform or "iPad" in platform:
    st.markdown("## 🍎 Install on iPhone/iPad")
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">1</span>Open Safari Browser</h3>
        <p>Make sure you're using <strong>Safari</strong> (not Chrome or other browsers)</p>
        <p>Go to: <code>https://nikkang-kk-epl.streamlit.app</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">2</span>Tap the Share Button</h3>
        <p>Look for the <strong>Share</strong> icon at the bottom of Safari</p>
        <p>It looks like a square with an arrow pointing up: <strong>⬆️</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual representation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔍 The Share button is usually at the bottom center or bottom right of Safari")
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">3</span>Select "Add to Home Screen"</h3>
        <p>Scroll down in the share menu and tap: <strong>"Add to Home Screen"</strong></p>
        <p>You may need to scroll down to find this option</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">4</span>Customize Name (Optional)</h3>
        <p>You can change the app name if you want</p>
        <p>Suggested name: <strong>"Nikkang KK"</strong> or <strong>"EPL Predictions"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">5</span>Tap "Add"</h3>
        <p>Tap the <strong>"Add"</strong> button in the top right corner</p>
        <p>✅ Done! The app icon will appear on your home screen</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional tips
    st.markdown("### 💡 iPhone/iPad Tips")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.success("""
        **✅ Must Use Safari**
        - This only works in Safari browser
        - Chrome/Firefox don't support this on iOS
        """)
        
        st.info("""
        **🔍 Finding the App**
        - Look on your home screen
        - May be on the last page
        - Use Spotlight search if needed
        """)
    
    with tips_col2:
        st.warning("""
        **⚠️ Browser Bars Will Disappear**
        - App opens full screen
        - No Safari address bar
        - Feels like a native app!
        """)
        
        st.success("""
        **🎨 Custom Icon**
        - App will use our logo
        - Looks professional
        - Easy to identify
        """)

# Android Instructions
else:
    st.markdown("## 🤖 Install on Android")
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">1</span>Open Chrome Browser</h3>
        <p>Make sure you're using <strong>Chrome</strong> browser</p>
        <p>Go to: <code>https://nikkang-kk-epl.streamlit.app</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">2</span>Open the Menu</h3>
        <p>Tap the <strong>three dots</strong> (⋮) in the top right corner</p>
        <p>This opens the Chrome menu</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual representation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔍 The menu icon (⋮) is in the top right corner of Chrome")
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">3</span>Select "Add to Home screen" or "Install app"</h3>
        <p>Depending on your Android version, you'll see:</p>
        <ul>
            <li><strong>"Add to Home screen"</strong>, or</li>
            <li><strong>"Install app"</strong></li>
        </ul>
        <p>Tap this option</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">4</span>Confirm Installation</h3>
        <p>A popup will appear asking you to confirm</p>
        <p>You can customize the app name if you want</p>
        <p>Suggested name: <strong>"Nikkang KK"</strong> or <strong>"EPL Predictions"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="install-card">
        <h3><span class="step-number">5</span>Tap "Install" or "Add"</h3>
        <p>Confirm by tapping <strong>"Install"</strong> or <strong>"Add"</strong></p>
        <p>✅ Done! The app icon will appear on your home screen</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional tips
    st.markdown("### 💡 Android Tips")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.success("""
        **✅ Works in Chrome**
        - Best experience in Chrome
        - Also works in Samsung Internet
        - May work in other browsers
        """)
        
        st.info("""
        **🔍 Finding the App**
        - Check your home screen
        - Look in app drawer
        - May be in a folder
        """)
    
    with tips_col2:
        st.warning("""
        **⚠️ Full Screen Experience**
        - No browser address bar
        - Full screen app
        - Native app feel!
        """)
        
        st.success("""
        **🎨 Custom Icon**
        - App uses our logo
        - Professional appearance
        - Easy to recognize
        """)

st.markdown("---")

# Video tutorials section
st.markdown("## 🎥 Video Tutorials (Optional)")

vid_col1, vid_col2 = st.columns(2)

with vid_col1:
    st.markdown("""
    <div class="install-card">
        <h3>📱 iPhone Tutorial</h3>
        <p>Need a visual guide?</p>
        <p>Search YouTube for: <strong>"Add to Home Screen iPhone Safari"</strong></p>
        <p>Or visit Apple Support for official instructions</p>
    </div>
    """, unsafe_allow_html=True)

with vid_col2:
    st.markdown("""
    <div class="install-card">
        <h3>🤖 Android Tutorial</h3>
        <p>Need a visual guide?</p>
        <p>Search YouTube for: <strong>"Install PWA Android Chrome"</strong></p>
        <p>Or visit Google Support for official instructions</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Troubleshooting section
st.markdown("## 🔧 Troubleshooting")

with st.expander("❓ I don't see the 'Add to Home Screen' option"):
    st.markdown("""
    **iPhone/iPad:**
    - Make sure you're using **Safari** browser (not Chrome)
    - Scroll down in the Share menu - the option might be below
    - Try reloading the page
    
    **Android:**
    - Make sure you're using **Chrome** browser
    - Look in the three-dot menu (⋮) at the top right
    - Try "Install app" instead of "Add to Home screen"
    - Some browsers don't support this feature
    """)

with st.expander("❓ The icon disappeared from my home screen"):
    st.markdown("""
    - Check if it moved to another page/folder
    - Use search (swipe down on home screen) to find it
    - If really gone, just re-install using the steps above
    - It only takes 30 seconds!
    """)

with st.expander("❓ App won't open or shows error"):
    st.markdown("""
    - Make sure you have internet connection
    - Try closing and reopening the app
    - If still not working, delete the icon and reinstall
    - Clear your browser cache and try again
    """)

with st.expander("❓ Can I use this on desktop/laptop?"):
    st.markdown("""
    **Yes!** While this feature is designed for mobile, you can also:
    
    **Desktop Chrome:**
    - Look for "Install" icon in address bar
    - Or Menu → More Tools → Create Shortcut
    - Check "Open as window"
    
    **Desktop Edge:**
    - Look for "Install" icon in address bar
    - Or Menu → Apps → Install this site as an app
    
    This creates a standalone app window without browser bars!
    """)

with st.expander("❓ Will this use a lot of storage?"):
    st.markdown("""
    **No!** This is a web app shortcut:
    - Uses almost no storage (< 1 MB)
    - Not a full download like App Store apps
    - Data stays on the server
    - Just a fast shortcut to the website
    """)

st.markdown("---")

# What happens after installation
st.markdown("## 🎉 After Installation")

after_col1, after_col2, after_col3 = st.columns(3)

with after_col1:
    st.markdown("""
    <div class="benefit-item">
        <h3>1️⃣ Find the Icon</h3>
        <p>Look for the Nikkang KK icon on your home screen</p>
    </div>
    """, unsafe_allow_html=True)

with after_col2:
    st.markdown("""
    <div class="benefit-item">
        <h3>2️⃣ Tap to Open</h3>
        <p>Opens full screen like a real app!</p>
    </div>
    """, unsafe_allow_html=True)

with after_col3:
    st.markdown("""
    <div class="benefit-item">
        <h3>3️⃣ Enjoy!</h3>
        <p>Make predictions, check leaderboard, win prizes!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick access section
st.markdown("## 🔗 Quick Access")

st.info("""
**Don't want to install?** No problem!

You can always access the competition at:
**https://nikkang-kk-epl.streamlit.app**

Just bookmark this page in your browser for easy access!
""")

# QR Code section
st.markdown("## 📱 Share with Friends")

st.markdown("""
Want to help others join? Share this page or the main app URL:

**Main App**: `https://nikkang-kk-epl.streamlit.app`

**This Install Guide**: `https://nikkang-kk-epl.streamlit.app/7_mobile_install`

Or generate a QR code at: **qr-code-generator.com**
""")

# Call to action
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
    <h2 style="color: white; margin: 0;">Ready to Install?</h2>
    <p style="color: #f0f0f0; font-size: 1.1rem; margin: 1rem 0;">
        Follow the steps above and get the best mobile experience!
    </p>
    <p style="font-size: 0.9rem; margin: 0;">
        Takes less than 1 minute • Works offline • Looks professional
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p>Need help? Contact your admin or visit the Help section</p>
</div>
""", unsafe_allow_html=True)
