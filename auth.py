import streamlit as st
import hashlib
import uuid
from database import create_user

def init_auth():
    """Initialize authentication system"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None

def check_authentication():
    """Check if user is authenticated"""
    # For Replit environment, we'll use a simple authentication method
    # In production, you would integrate with Replit Auth or another auth service
    
    if st.session_state.get('authenticated', False):
        return True
    
    # Try to authenticate user
    return authenticate_user()

def authenticate_user():
    """Handle user authentication"""
    # In a real Replit environment, you would use Replit Auth
    # For this demo, we'll use a simple session-based approach
    
    # Check if we have a session user
    if 'temp_user_id' not in st.session_state:
        # Generate a temporary user ID for the session
        st.session_state['temp_user_id'] = f"user_{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]}"
    
    # For demo purposes, we'll auto-authenticate with the session user ID
    # In production, this would be replaced with proper Replit Auth integration
    user_id = st.session_state['temp_user_id']
    
    try:
        # Create user in database if not exists
        create_user(user_id)
        
        # Set authentication state
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = user_id
        
        return True
        
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

def logout_user():
    """Log out the current user"""
    # Clear authentication state
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    
    # Clear other session data
    keys_to_remove = [
        'current_doc_id',
        'current_doc_content', 
        'current_summary',
        'qa_history',
        'viewing_doc'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def get_current_user():
    """Get the current authenticated user ID"""
    if st.session_state.get('authenticated', False):
        return st.session_state.get('user_id')
    return None

# Note: In a production Replit environment, you would replace the above
# authentication logic with proper Replit Auth integration like this:

"""
# Production Replit Auth Integration Example:
import os
import requests

def authenticate_with_replit():
    # Get Replit user info
    user_id = os.getenv('REPL_OWNER', '')
    repl_id = os.getenv('REPL_ID', '')
    
    if user_id and repl_id:
        # Verify with Replit's authentication system
        # This is a simplified example - actual implementation would depend on Replit's auth API
        
        try:
            # Create user in database
            create_user(user_id)
            
            # Set authentication state
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = user_id
            
            return True
            
        except Exception as e:
            st.error(f"Replit authentication failed: {str(e)}")
            return False
    
    return False
"""

def is_authenticated():
    """Check if current session is authenticated"""
    return st.session_state.get('authenticated', False)

def require_authentication():
    """Decorator/function to require authentication"""
    if not is_authenticated():
        st.error("Authentication required")
        st.stop()

def get_user_display_name():
    """Get a display-friendly username"""
    user_id = get_current_user()
    if user_id:
        # Clean up the user ID for display
        if user_id.startswith('user_'):
            return f"User {user_id[5:].upper()}"
        return user_id
    return "Anonymous"

def generate_session_token():
    """Generate a session token for additional security"""
    if 'session_token' not in st.session_state:
        st.session_state['session_token'] = hashlib.sha256(
            f"{st.session_state.get('user_id', '')}{uuid.uuid4()}".encode()
        ).hexdigest()
    
    return st.session_state['session_token']

def validate_session():
    """Validate current session integrity"""
    try:
        # Check if all required session variables exist
        required_vars = ['authenticated', 'user_id', 'session_token']
        
        for var in required_vars:
            if var not in st.session_state:
                return False
        
        # Additional validation logic can be added here
        # e.g., check session expiry, validate token, etc.
        
        return True
        
    except Exception:
        return False
