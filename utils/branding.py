"""
Branding Utility for Nikkang KK EPL Prediction Competition
Provides consistent logo and styling across all pages
"""

import streamlit as st
from pathlib import Path

# Color scheme
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'text': '#212529',
    'muted': '#6c757d'
}

def inject_custom_css():
    """Inject custom CSS for consistent styling"""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        .main-header {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            color: #f0f0f0;
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
            padding-top: 0 !important;
        }
        
        /* Remove default padding from sidebar */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }
        
        .sidebar-logo-container {
            text-align: center;
            padding: 1rem;
            margin: 0 0 1rem 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Logo sizing */
        .logo-main {
            max-width: 350px;
            width: 100%;
            height: auto;
            margin: 1.5rem auto;
            display: block;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
        }
        
        .logo-sidebar {
            max-width: 100%;
            height: auto;
            margin: 0 auto;
            display: block;
        }
        
        /* Cards */
        .stats-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
        }
        
        .stats-card h3 {
            color: #667eea;
            margin-top: 0;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        /* Buttons - Enhanced for mobile */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
            min-height: 44px !important;  /* Apple's recommended touch target */
            padding: 12px 24px !important;
            font-size: 16px !important;  /* Prevents zoom on iOS */
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Mobile-specific button improvements */
        @media (max-width: 768px) {
            .stButton > button {
                min-height: 48px !important;
                width: 100% !important;
                margin: 8px 0 !important;
                font-size: 18px !important;
            }
        }
        
        /* Tables */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Success/Info boxes */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem 0 1rem 0;
            color: #6c757d;
            font-size: 0.9rem;
            border-top: 2px solid #dee2e6;
            margin-top: 3rem;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #667eea;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 600;
            min-height: 44px;  /* Touch target */
        }
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {
            /* Larger touch targets for mobile */
            .stRadio > div {
                gap: 16px !important;
            }
            
            .stRadio > div > label {
                min-height: 48px !important;
                padding: 12px !important;
                font-size: 16px !important;
            }
            
            .stCheckbox > label {
                min-height: 48px !important;
                padding: 12px !important;
                font-size: 16px !important;
            }
            
            /* Text inputs - prevent zoom on iOS */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > select {
                font-size: 16px !important;
                min-height: 48px !important;
                padding: 12px !important;
            }
            
            /* Date inputs */
            .stDateInput > div > div > input {
                font-size: 16px !important;
                min-height: 48px !important;
            }
            
            /* Dropdown/Select */
            .stSelectbox > div > div {
                min-height: 48px !important;
            }
            
            /* Number input buttons */
            .stNumberInput button {
                min-width: 48px !important;
                min-height: 48px !important;
            }
            
            /* Slider */
            .stSlider > div > div > div {
                height: 48px !important;
            }
            
            /* Headers - smaller on mobile */
            .main-header h1 {
                font-size: 1.8rem !important;
            }
            
            .main-header p {
                font-size: 1rem !important;
            }
            
            /* Reduce padding on mobile */
            .stats-card {
                padding: 1rem !important;
            }
            
            /* Stack columns on mobile */
            [data-testid="column"] {
                min-width: 100% !important;
            }
            
            /* Metrics - stack on mobile */
            [data-testid="stMetric"] {
                min-width: 100% !important;
                margin: 8px 0 !important;
            }
            
            /* Tables - horizontal scroll */
            .dataframe {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }
            
            /* Sidebar - full width when open on mobile */
            [data-testid="stSidebar"] {
                width: 100% !important;
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                min-height: 48px !important;
                padding: 12px !important;
                font-size: 16px !important;
            }
            
            /* Tabs - larger on mobile */
            .stTabs [data-baseweb="tab"] {
                padding: 14px 24px !important;
                font-size: 16px !important;
                min-height: 48px !important;
            }
        }
        
        /* Prevent text size adjustment on orientation change */
        html {
            -webkit-text-size-adjust: 100%;
            -moz-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Remove tap highlight on mobile */
        * {
            -webkit-tap-highlight-color: transparent;
        }
        
        /* Better focus for accessibility */
        button:focus,
        input:focus,
        select:focus,
        textarea:focus {
            outline: 2px solid #667eea;
            outline-offset: 2px;
        }
    </style>
    """, unsafe_allow_html=True)

def check_logo_exists():
    """Check if logo file exists"""
    return Path("nikkang_logo.png").exists()

def display_sidebar_logo():
    """Display logo in sidebar with fallback - ALWAYS at the top"""
    if check_logo_exists():
        # Add some top padding for better positioning
        st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
        st.sidebar.image("nikkang_logo.png", use_container_width=True, output_format="PNG")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback text logo
        st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown("""
        <div class="sidebar-logo-container">
            <h2 style="color: #667eea; margin: 0; font-size: 1.8rem;">⚽</h2>
            <h3 style="color: #667eea; margin: 0.5rem 0 0 0;">NIKKANG KK</h3>
            <p style="color: #6c757d; font-size: 0.85rem; margin: 0.25rem 0 0 0;">EPL Prediction League</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")

def display_main_logo(title=None, subtitle=None):
    """
    Display logo in main page header
    
    Args:
        title: Optional custom title
        subtitle: Optional custom subtitle
    """
    # Logo centered
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if check_logo_exists():
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.image("nikkang_logo.png", use_container_width=True, output_format="PNG")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="color: #667eea; font-size: 3rem; margin: 0;">⚽ NIKKANG KK</h1>
                <p style="color: #6c757d; font-size: 1.3rem; margin: 0.5rem 0 0 0;">EPL Prediction League</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Header with title
    if title:
        st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)

def display_page_header(icon, title, subtitle=None):
    """
    Display a consistent page header
    
    Args:
        icon: Emoji icon for the page
        title: Page title
        subtitle: Optional subtitle
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>{icon} {title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def display_footer():
    """Display consistent footer across pages"""
    st.markdown("""
    <div class="footer">
        <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
        <p style="font-size: 0.85rem;">Powered by Streamlit & Football-Data.org</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem; color: #adb5bd;">
            © 2025 Nikkang KK. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_stat_card(title, content, icon="📊"):
    """
    Create a styled statistics card
    
    Args:
        title: Card title
        content: Card content (can be HTML)
        icon: Optional icon
    """
    st.markdown(f"""
    <div class="stats-card">
        <h3>{icon} {title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

def display_sidebar_stats():
    """Display quick stats in sidebar"""
    st.sidebar.markdown("### 📊 Quick Stats")
    
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        participants = dm.load_participants()
        matches = dm.load_matches()
        
        st.sidebar.metric("👥 Participants", len(participants))
        st.sidebar.metric("⚽ Matches", len(matches))
        
        if matches:
            current_week = max([m.get('week', 0) for m in matches])
            st.sidebar.metric("📅 Current Week", f"Week {current_week}")
    except:
        st.sidebar.info("📊 Stats loading...")
    
    st.sidebar.markdown("---")

def display_sidebar_navigation():
    """Display navigation buttons in sidebar"""
    st.sidebar.markdown("### 🎯 Quick Navigation")
    
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/1_home.py")
    
    if st.sidebar.button("📝 Register", use_container_width=True):
        st.switch_page("pages/2_register.py")
    
    if st.sidebar.button("🎯 Predictions", use_container_width=True):
        st.switch_page("pages/3_predictions.py")
    
    if st.sidebar.button("📊 Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")
    
    st.sidebar.markdown("---")

def setup_page(page_title, page_icon="⚽", layout="wide"):
    """
    Setup page with consistent configuration and branding
    
    Args:
        page_title: Title for the page
        page_icon: Icon for browser tab
        layout: Streamlit layout ("wide" or "centered")
    
    Returns:
        None
    """
    # This should be called at the very top of each page file
    # before any other Streamlit commands
    st.set_page_config(
        page_title=f"{page_title} - Nikkang KK",
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    
    # Inject CSS
    inject_custom_css()
    
    # Display sidebar elements
    display_sidebar_logo()

def show_success_message(message, icon="✅"):
    """Display styled success message"""
    st.success(f"{icon} {message}")

def show_error_message(message, icon="❌"):
    """Display styled error message"""
    st.error(f"{icon} {message}")

def show_info_message(message, icon="ℹ️"):
    """Display styled info message"""
    st.info(f"{icon} {message}")

def show_warning_message(message, icon="⚠️"):
    """Display styled warning message"""
    st.warning(f"{icon} {message}")

# Color utilities
def get_color(color_name):
    """Get color from theme"""
    return COLORS.get(color_name, COLORS['primary'])

def get_gradient_css(color1='primary', color2='secondary'):
    """Get gradient CSS"""
    c1 = COLORS.get(color1, COLORS['primary'])
    c2 = COLORS.get(color2, COLORS['secondary'])
    return f"linear-gradient(135deg, {c1} 0%, {c2} 100%)"
