import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Configure Gemini (free AI service)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

def check_gemini_service() -> bool:
    """Check if Gemini service is available"""
    try:
        if not client:
            st.error("Gemini API key not found. Please add your GEMINI_API_KEY.")
            return False
        
        # Test with a simple request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello"
        )
        return bool(response.text)
    except Exception as e:
        st.error(f"Gemini service check failed: {str(e)}")
        return False

def generate_summary(text: str, length: str = "medium") -> str:
    """Generate optimized summary using Gemini"""
    try:
        if not client:
            raise Exception("Gemini API key not configured")
        
        # Fast text processing - limit size for speed
        max_chars = 2000 if length == "short" else 3000 if length == "medium" else 4000
        
        if len(text) > max_chars:
            processed_text = text[:max_chars]
        else:
            processed_text = text
        
        # Define summary lengths
        length_instructions = {
            "short": "Write a brief 2-3 sentence summary",
            "medium": "Write a concise 1-2 paragraph summary", 
            "long": "Write a detailed 3-4 paragraph summary"
        }
        
        instruction = length_instructions.get(length, length_instructions["medium"])
        prompt = f"{instruction} of this document:\n\n{processed_text}"
        
        # Show progress
        with st.spinner("🤖 Generating summary with Gemini..."):
            start_time = time.time()
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            elapsed_time = time.time() - start_time
            st.success(f"✅ Summary ready in {elapsed_time:.1f}s")
        
        if not response.text or not response.text.strip():
            raise Exception("Empty summary generated")
            
        return response.text.strip()
        
    except Exception as e:
        error_msg = f"Failed to generate summary: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)

def answer_question(document_text: str, question: str) -> str:
    """Fast question answering using Gemini"""
    try:
        if not client:
            raise Exception("Gemini API key not configured")
        
        # Limit text for speed
        max_chars = 3000
        if len(document_text) > max_chars:
            processed_text = document_text[:max_chars]
        else:
            processed_text = document_text
        
        prompt = f"Based on this document, answer the question briefly and accurately.\n\nDocument: {processed_text}\n\nQuestion: {question}\n\nAnswer:"
        
        # Show progress
        with st.spinner("🤖 Finding answer with Gemini..."):
            start_time = time.time()
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            elapsed_time = time.time() - start_time
            st.success(f"✅ Answer ready in {elapsed_time:.1f}s")
        
        if not response.text or not response.text.strip():
            raise Exception("Empty answer generated")
            
        return response.text.strip()
        
    except Exception as e:
        error_msg = f"Failed to generate answer: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)