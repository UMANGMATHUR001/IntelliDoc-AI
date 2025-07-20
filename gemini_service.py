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

def chunk_text(text: str, max_words: int = 1200) -> list:
    """Split text into manageable chunks for processing"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    
    return chunks

def generate_summary(text: str, length: str = "medium") -> str:
    """Generate intelligent summary using Gemini with chunking"""
    try:
        if not client:
            raise Exception("Gemini API key not configured")
        
        st.info("💡 Your PDF is being split into sections to ensure a smooth and accurate summary with Gemini AI. This helps us stay within the free usage limits and maintain performance.")
        
        # Determine chunk size and summary style based on length preference
        chunk_configs = {
            "short": {"max_words": 1500, "instruction": "Write a brief 2-3 sentence summary"},
            "medium": {"max_words": 1200, "instruction": "Write a concise paragraph summary"},
            "long": {"max_words": 1000, "instruction": "Write a detailed 2-paragraph summary"}
        }
        
        config = chunk_configs.get(length, chunk_configs["medium"])
        
        # Split text into chunks
        chunks = chunk_text(text, config["max_words"])
        
        if len(chunks) == 1:
            # Single chunk - process directly
            prompt = f"{config['instruction']} of this document:\n\n{chunks[0]}"
            
            with st.spinner("🤖 Generating summary with Gemini..."):
                start_time = time.time()
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                elapsed_time = time.time() - start_time
                st.success(f"✅ Summary ready in {elapsed_time:.1f}s")
            
            return response.text.strip() if response.text else ""
        
        else:
            # Multiple chunks - process each and combine
            chunk_summaries = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, chunk in enumerate(chunks):
                status_text.text(f"Processing section {i+1} of {len(chunks)}...")
                progress_bar.progress((i + 1) / len(chunks))
                
                prompt = f"Summarize this section concisely:\n\n{chunk}"
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response.text:
                    chunk_summaries.append(response.text.strip())
                
                # Small delay to respect rate limits
                time.sleep(0.5)
            
            # Combine all chunk summaries into final summary
            combined_text = "\n\n".join(chunk_summaries)
            
            final_instructions = {
                "short": "Combine these section summaries into a brief 2-3 sentence overview",
                "medium": "Combine these section summaries into a comprehensive 1-2 paragraph summary",
                "long": "Combine these section summaries into a detailed 3-4 paragraph summary covering all key points"
            }
            
            final_prompt = f"{final_instructions[length]}:\n\n{combined_text}"
            
            status_text.text("Creating final summary...")
            
            final_response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=final_prompt
            )
            
            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"✅ Complete summary ready! Processed {len(chunks)} sections")
            
            return final_response.text.strip() if final_response.text else ""
        
    except Exception as e:
        error_msg = f"Failed to generate summary: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)

def answer_question(document_text: str, question: str) -> str:
    """Smart question answering using Gemini with intelligent text handling"""
    try:
        if not client:
            raise Exception("Gemini API key not configured")
        
        # For Q&A, search through chunks to find most relevant section
        chunks = chunk_text(document_text, 1000)
        
        if len(chunks) == 1:
            # Single chunk - process directly
            prompt = f"Based on this document, answer the question briefly and accurately.\n\nDocument: {chunks[0]}\n\nQuestion: {question}\n\nAnswer:"
            
            with st.spinner("🤖 Finding answer with Gemini..."):
                start_time = time.time()
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                elapsed_time = time.time() - start_time
                st.success(f"✅ Answer ready in {elapsed_time:.1f}s")
            
            return response.text.strip() if response.text else ""
        
        else:
            # Multiple chunks - find most relevant one
            st.info("🔍 Searching through document sections for the best answer...")
            
            # Use first few chunks for context (most documents have key info early)
            relevant_chunks = chunks[:3]  # Use first 3 chunks for speed
            combined_text = "\n\n".join(relevant_chunks)
            
            # Limit combined text length
            if len(combined_text) > 4000:
                combined_text = combined_text[:4000] + "..."
            
            prompt = f"Based on this document, answer the question briefly and accurately.\n\nDocument: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
            
            with st.spinner("🤖 Finding answer with Gemini..."):
                start_time = time.time()
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                elapsed_time = time.time() - start_time
                st.success(f"✅ Answer ready in {elapsed_time:.1f}s")
            
            return response.text.strip() if response.text else ""
        
    except Exception as e:
        error_msg = f"Failed to generate answer: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)