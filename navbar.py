import streamlit as st

def render_navbar():
    """Render the top navigation bar with IntelliDoc AI branding and user options"""
    
    # Custom CSS for navbar styling
    st.markdown("""
    <style>
    .navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 0px 0px 15px 15px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .navbar-brand {
        font-size: 28px;
        font-weight: bold;
        color: white !important;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .navbar-brand:hover {
        color: #f0f0f0 !important;
        text-decoration: none;
    }
    
    .navbar-actions {
        display: flex;
        gap: 15px;
        align-items: center;
    }
    
    .navbar-btn {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .navbar-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        color: white;
        text-decoration: none;
        transform: translateY(-1px);
    }
    
    .dark-mode-toggle {
        background: none;
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 6px 12px;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .dark-mode-toggle:hover {
        border-color: white;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* File upload styling */
    .file-info {
        font-size: 14px !important;
        padding: 12px;
        background: rgba(0, 0, 0, 0.03);
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    
    .file-info h4 {
        font-size: 16px !important;
        margin-bottom: 8px;
        color: #333;
    }
    
    .file-info p {
        margin: 4px 0;
        color: #666;
    }
    
    /* Dark mode styles */
    .dark-mode {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .dark-mode .stApp {
        background-color: #1e1e1e;
    }
    
    .dark-mode .stSidebar {
        background-color: #2d2d2d;
    }
    
    /* Light mode (default) */
    .light-mode {
        background-color: #ffffff;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize dark mode state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Create navbar HTML
    navbar_html = f"""
    <div class="navbar">
        <div class="navbar-brand">
            🧠 IntelliDoc AI
        </div>
        <div class="navbar-actions">
            <span style="color: rgba(255, 255, 255, 0.8); font-size: 14px;">
                Smart PDF Analysis & Q&A
            </span>
        </div>
    </div>
    """
    
    st.markdown(navbar_html, unsafe_allow_html=True)
    
    # Action buttons in a separate row for better mobile compatibility
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("👤 Sign In", key="signin_btn", help="Access your account"):
            show_signin_modal()
    
    with col2:
        dark_mode_label = "🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"
        if st.button(dark_mode_label, key="dark_mode_btn", help="Toggle dark/light mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            # Optimized rerun - only update state without full page reload
            st.session_state.theme_changed = True
    
    with col3:
        if st.button("📊 Dashboard", key="dashboard_btn", help="View analytics"):
            st.info("Dashboard feature coming soon!")
    
    with col4:
        if st.button("❓ Help", key="help_btn", help="Get help and support"):
            show_help_modal()
    
    # Apply dark mode styling with optimized performance
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        :root {
            --dark-bg: #0f0f0f;
            --dark-surface: #1a1a1a;
            --dark-surface-2: rgba(255, 255, 255, 0.05);
            --dark-border: rgba(255, 255, 255, 0.1);
            --dark-text: #FFFFFF;
            --dark-text-muted: rgba(255, 255, 255, 0.7);
        }
        
        .stApp {
            background-color: var(--dark-bg) !important;
            color: var(--dark-text) !important;
        }
        
        .stSidebar {
            background-color: var(--dark-surface) !important;
        }
        
        /* Navbar buttons with transparency */
        .stButton > button {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Sidebar components */
        .stSidebar .stSelectbox > div > div {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        .stSidebar .stTextInput > div > div > input {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        .stSidebar .stButton > button {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        .stSidebar .stMetric {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            padding: 12px !important;
            border-radius: 8px !important;
            border: 1px solid var(--dark-border) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stSidebar .stMetric [data-testid="metric-container"] {
            background: transparent !important;
            color: var(--dark-text) !important;
        }
        
        .stSidebar .stMetric label {
            color: var(--dark-text-muted) !important;
        }
        
        .stSidebar .stMetric [data-testid="metric-container"] > div {
            color: var(--dark-text) !important;
        }
        
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4 {
            color: var(--dark-text) !important;
        }
        
        .stSidebar p, .stSidebar div, .stSidebar span {
            color: var(--dark-text) !important;
        }
        
        /* Main content inputs */
        .stSelectbox > div > div {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        .stTextInput > div > div > input {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        .stTextArea > div > div > textarea {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
        }
        
        /* Expanders */
        .stExpander {
            background: var(--dark-surface-2) !important;
            border: 1px solid var(--dark-border) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stExpander .stMarkdown {
            color: var(--dark-text) !important;
        }
        
        /* File uploader */
        .stFileUploader {
            background: var(--dark-surface-2) !important;
            border: 2px dashed var(--dark-border) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stFileUploader label {
            color: var(--dark-text) !important;
        }
        
        /* File info styling for dark mode */
        .file-info {
            background: var(--dark-surface-2) !important;
            color: var(--dark-text) !important;
            border: 1px solid var(--dark-border) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .file-info h4 {
            color: var(--dark-text) !important;
        }
        
        .file-info p {
            color: var(--dark-text-muted) !important;
        }
        
        /* Alert boxes */
        .stAlert {
            backdrop-filter: blur(10px) !important;
        }
        
        .stInfo {
            background: rgba(59, 130, 246, 0.1) !important;
            color: var(--dark-text) !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
        }
        
        .stSuccess {
            background: rgba(34, 197, 94, 0.1) !important;
            color: var(--dark-text) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
        }
        
        .stWarning {
            background: rgba(251, 191, 36, 0.1) !important;
            color: var(--dark-text) !important;
            border: 1px solid rgba(251, 191, 36, 0.3) !important;
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.1) !important;
            color: var(--dark-text) !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
        }
        
        /* Spinner */
        .stSpinner {
            color: var(--dark-text) !important;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: var(--dark-surface-2) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def show_signin_modal():
    """Display sign-in modal dialog"""
    with st.expander("🔐 Sign In", expanded=True):
        st.markdown("### Welcome back!")
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sign In", type="primary", use_container_width=True):
                    if email and password:
                        st.success("Welcome back! (Demo mode)")
                        st.session_state.user_signed_in = True
                        st.session_state.user_email = email
                    else:
                        st.error("Please fill in all fields")
            
            with col2:
                if st.button("Forgot Password?", use_container_width=True):
                    st.info("Password reset feature coming soon!")
        
        with tab2:
            new_email = st.text_input("Email", placeholder="your@email.com", key="new_email")
            new_password = st.text_input("Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        st.success("Account created! (Demo mode)")
                        st.session_state.user_signed_in = True
                        st.session_state.user_email = new_email
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill in all fields")

def show_help_modal():
    """Display help and support information"""
    with st.expander("❓ Help & Support", expanded=True):
        st.markdown("### How to use IntelliDoc AI")
        
        st.markdown("""
        **📄 Upload PDF**: Click 'Browse files' to upload your PDF document
        
        **📝 Generate Summary**: Choose summary length and click 'Generate Summary'
        - Short: Quick 2-3 sentence overview
        - Medium: Detailed 1-2 paragraph summary  
        - Long: Comprehensive 3-4 paragraph analysis
        
        **❓ Ask Questions**: Type questions about your document for instant answers
        
        **🔍 Smart Processing**: Large documents are automatically split into sections for better accuracy
        
        **⚡ Fast AI**: Powered by Google Gemini for 2-3 second response times
        """)
        
        st.markdown("### 🚀 Features")
        st.markdown("""
        - ✅ Free unlimited document processing
        - ✅ Intelligent text chunking for large files
        - ✅ Multi-format PDF support
        - ✅ Secure document storage
        - ✅ Conversation history
        """)
        
        st.markdown("### 📞 Support")
        st.markdown("Need help? Contact us at support@intellidoc.ai")

def get_user_info():
    """Get current user information"""
    if 'user_signed_in' in st.session_state and st.session_state.user_signed_in:
        return {
            'signed_in': True,
            'email': st.session_state.get('user_email', 'demo@user.com')
        }
    return {'signed_in': False}