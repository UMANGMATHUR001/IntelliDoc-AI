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
        padding: 10px;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .file-info h4 {
        font-size: 16px !important;
        margin-bottom: 5px;
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
            st.rerun()
    
    with col3:
        if st.button("📊 Dashboard", key="dashboard_btn", help="View analytics"):
            st.info("Dashboard feature coming soon!")
    
    with col4:
        if st.button("❓ Help", key="help_btn", help="Get help and support"):
            show_help_modal()
    
    # Apply dark mode styling
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        .stSidebar {
            background-color: #2d2d2d !important;
        }
        .stSidebar .stSelectbox > div > div {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stSidebar .stTextInput > div > div > input {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stSidebar .stTextArea > div > div > textarea {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stSidebar .stButton > button {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stSidebar .stMetric {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #555;
        }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #ffffff !important;
        }
        .stSidebar p, .stSidebar div {
            color: #ffffff !important;
        }
        .stSelectbox > div > div {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stTextInput > div > div > input {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stTextArea > div > div > textarea {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stButton > button {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #555 !important;
        }
        .stButton > button:hover {
            background-color: #4d4d4d !important;
        }
        .stExpander {
            background-color: #2d2d2d !important;
            border: 1px solid #555 !important;
        }
        .stExpander .stMarkdown {
            color: #ffffff !important;
        }
        /* File uploader dark mode */
        .stFileUploader {
            background-color: #3d3d3d !important;
            border: 2px dashed #666 !important;
            border-radius: 10px !important;
        }
        .stFileUploader label {
            color: #ffffff !important;
        }
        /* Info boxes */
        .stInfo {
            background-color: #2d4f5f !important;
            color: #ffffff !important;
            border: 1px solid #4a7c7c !important;
        }
        .stSuccess {
            background-color: #2d5f2d !important;
            color: #ffffff !important;
            border: 1px solid #4a7c4a !important;
        }
        .stWarning {
            background-color: #5f5f2d !important;
            color: #ffffff !important;
            border: 1px solid #7c7c4a !important;
        }
        .stError {
            background-color: #5f2d2d !important;
            color: #ffffff !important;
            border: 1px solid #7c4a4a !important;
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