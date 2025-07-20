import streamlit as st
import os
from datetime import datetime
import io

# Import our custom modules
from auth import init_auth, check_authentication
from database import init_database, get_user_documents, save_document, save_qa_interaction
from pdf_processor import extract_text_from_pdf, validate_pdf
from gemini_service import generate_summary, answer_question, check_gemini_service
from utils import format_file_size, truncate_text
from performance_optimizer import display_performance_dashboard, apply_speed_optimizations
from navbar import render_navbar, get_user_info

# Page configuration
st.set_page_config(
    page_title="IntelliDoc AI - Smart PDF Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    # Apply performance optimizations
    apply_speed_optimizations()
    
    # Initialize database
    init_database()
    
    # Initialize authentication
    init_auth()
    
    # Check if user is authenticated
    if not check_authentication():
        show_authentication_page()
        return
    
    # Main application interface
    show_main_application()

def show_authentication_page():
    """Display authentication interface"""
    st.title("🔐 AI PDF Summarizer & Q&A")
    st.subheader("Secure Access Required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("Please authenticate to access the application")
        
        # Simple authentication message
        st.markdown("""
        **Features:**
        - 📄 Upload and analyze PDF documents
        - 🤖 AI-powered summarization
        - ❓ Interactive Q&A with your documents
        - 🔒 Secure multi-user support
        - 📊 Document history and management
        """)

def show_main_application():
    """Display the main application interface"""
    user_id = st.session_state.get('user_id')
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 IntelliDoc AI")
        st.write(f"👤 User: {user_id}")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Upload & Analyze", "Document History", "Settings"]
        )
        
        st.divider()
        
        # Quick stats
        user_docs = get_user_documents(user_id)
        st.metric("Your Documents", len(user_docs))
        
        # Performance dashboard
        display_performance_dashboard()
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    if page == "Upload & Analyze":
        show_upload_analyze_page(user_id)
    elif page == "Document History":
        show_document_history_page(user_id)
    elif page == "Settings":
        show_settings_page()

def show_upload_analyze_page(user_id):
    """Display the upload and analyze page"""
    # Render navbar
    render_navbar()
    
    st.title("📄 Upload & Analyze PDF")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to analyze and ask questions about"
    )
    
    if uploaded_file is not None:
        # Validate PDF
        if not validate_pdf(uploaded_file):
            st.error("Invalid PDF file. Please upload a valid PDF document.")
            return
            
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", format_file_size(uploaded_file.size))
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Process PDF (optimized)  
        try:
            with st.spinner("⚡ Extracting text from PDF..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
                
            if not extracted_text.strip():
                st.error("No text could be extracted from this PDF. The file might contain only images or be corrupted.")
                return
                
            st.success(f"✅ Extracted {len(extracted_text)} characters ({len(extracted_text.split())} words)")
            
            # Show extracted text preview
            with st.expander("📖 Preview Extracted Text"):
                st.text_area(
                    "Extracted Content (first 1000 characters):",
                    value=truncate_text(extracted_text, 1000),
                    height=200,
                    disabled=True
            )
            
            # Summary options
            st.subheader("📝 Generate AI Summary")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                summary_length = st.selectbox(
                    "Summary Style:",
                    ["short", "medium", "long"],
                    index=1,
                    help="Short: 2-3 sentences | Medium: 1-2 paragraphs | Long: 3-4 paragraphs"
                )
            
            with col2:
                generate_summary_btn = st.button(
                    "🚀 Generate Summary",
                    type="primary",
                    use_container_width=True,
                    help="Uses free Gemini AI for fast, accurate summaries"
            )
            
            if generate_summary_btn:
                try:
                    # Check if Gemini is available
                    if not check_gemini_service():
                        st.error("Gemini AI service is not available. Please check your API key.")
                        return
                    
                    summary = generate_summary(extracted_text, summary_length)
                    
                    # Save document to database
                    doc_id = save_document(
                        user_id=user_id,
                        filename=uploaded_file.name,
                        content=extracted_text,
                        summary=summary,
                        file_size=uploaded_file.size
                    )
                    
                    st.session_state['current_doc_id'] = doc_id
                    st.session_state['current_doc_content'] = extracted_text
                    st.session_state['current_summary'] = summary
                    
                    # Display summary
                    st.subheader("📋 Generated Summary")
                    st.write(summary)
                    
                    # Download summary option
                    st.download_button(
                        label="📥 Download Summary",
                        data=summary,
                        file_name=f"{uploaded_file.name}_summary.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Failed to generate summary: {str(e)}")
                    return
            
            # Q&A Section
            if 'current_doc_content' in st.session_state:
                st.divider()
                st.subheader("❓ Ask Questions About This Document")
                
                # Display previous Q&A if any
                if 'qa_history' not in st.session_state:
                    st.session_state['qa_history'] = []
                
                # Question input
                question = st.text_input(
                    "Your Question:",
                    placeholder="What is the main topic of this document?",
                    help="Ask any question about the document content"
                )
                
                if st.button("🔍 Get Answer", type="secondary"):
                    if question.strip():
                        try:
                            answer = answer_question(
                                st.session_state['current_doc_content'],
                                question
                            )
                            
                            # Save Q&A interaction
                            save_qa_interaction(
                                st.session_state['current_doc_id'],
                                question,
                                answer
                            )
                            
                            # Add to session history
                            st.session_state['qa_history'].append({
                                'question': question,
                                'answer': answer,
                                'timestamp': datetime.now()
                            })
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Failed to generate answer: {str(e)}")
                    else:
                        st.warning("Please enter a question.")
                
                # Display Q&A history
                if st.session_state['qa_history']:
                    st.subheader("💬 Q&A History")
                    for i, qa in enumerate(reversed(st.session_state['qa_history'])):
                        with st.container():
                            st.markdown(f"**Q{len(st.session_state['qa_history'])-i}:** {qa['question']}")
                            st.markdown(f"**A:** {qa['answer']}")
                            st.caption(f"Asked at {qa['timestamp'].strftime('%H:%M:%S')}")
                            st.divider()
                
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

def show_document_history_page(user_id):
    """Display user's document history"""
    st.title("📚 Document History")
    
    documents = get_user_documents(user_id)
    
    if not documents:
        st.info("No documents found. Upload a PDF to get started!")
        return
    
    for doc in documents:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{doc['filename']}**")
                st.caption(f"Uploaded: {doc['created_at'].strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.metric("Size", format_file_size(doc['file_size']))
            
            with col3:
                if doc['summary']:
                    st.success("✅ Summarized")
                else:
                    st.warning("⏳ No summary")
            
            with col4:
                if st.button("👁️", key=f"view_{doc['id']}", help="View document"):
                    st.session_state['viewing_doc'] = doc['id']
                    st.rerun()
            
            # Show document details if selected
            if st.session_state.get('viewing_doc') == doc['id']:
                st.subheader(f"📄 {doc['filename']}")
                
                if doc['summary']:
                    st.markdown("**Summary:**")
                    st.write(doc['summary'])
                    
                    # Download option
                    st.download_button(
                        label="📥 Download Summary",
                        data=doc['summary'],
                        file_name=f"{doc['filename']}_summary.txt",
                        mime="text/plain",
                        key=f"download_{doc['id']}"
                    )
                
                with st.expander("📖 Full Content"):
                    st.text_area(
                        "Document Content:",
                        value=doc['content'],
                        height=300,
                        disabled=True,
                        key=f"content_{doc['id']}"
                    )
                
                if st.button("❌ Close", key=f"close_{doc['id']}"):
                    if 'viewing_doc' in st.session_state:
                        del st.session_state['viewing_doc']
                    st.rerun()
            
            st.divider()

def show_settings_page():
    """Display application settings"""
    st.title("⚙️ Settings")
    
    st.subheader("🔧 Application Settings")
    
    # Theme selection (informational only since we use default styling)
    st.selectbox(
        "Theme:",
        ["Light (Default)", "Dark"],
        disabled=True,
        help="Theme customization is handled by Streamlit's default settings"
    )
    
    # Summary preferences
    st.subheader("📝 Summary Preferences")
    default_length = st.selectbox(
        "Default Summary Length:",
        ["short", "medium", "long"],
        index=1
    )
    
    # Save preferences (in a real app, this would save to database)
    if st.button("💾 Save Preferences"):
        st.session_state['default_summary_length'] = default_length
        st.success("Preferences saved!")
    
    st.divider()
    
    st.subheader("ℹ️ Application Info")
    st.info("""
    **AI PDF Summarizer & Q&A v1.0**
    
    Features:
    - Secure multi-user authentication
    - PDF text extraction using PyMuPDF
    - AI-powered summarization with OpenAI
    - Interactive document Q&A
    - Document history and management
    - Secure data isolation between users
    """)

if __name__ == "__main__":
    main()
