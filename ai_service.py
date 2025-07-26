from gemini_service import (
    generate_summary,
    answer_question,
    check_gemini_service
)


# import os
# import json
# import ollama
# import streamlit as st
# import time
# from typing import Optional
# import requests
# import time

# # Initialize Ollama client
# OLLAMA_MODEL = "mistral"
# OLLAMA_BASE_URL = "http://localhost:11434"

# def check_ollama_service():
#     """Check if Ollama service is running and model is available"""
#     try:
#         # Check if Ollama is running
#         response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
#         if response.status_code == 200:
#             models = response.json().get("models", [])
#             model_names = [model.get("name", "").split(":")[0] for model in models]
            
#             if OLLAMA_MODEL not in model_names:
#                 with st.spinner(f"Downloading {OLLAMA_MODEL} model..."):
#                     try:
#                         # Pull the model
#                         ollama.pull(OLLAMA_MODEL)
#                         st.success(f"Model '{OLLAMA_MODEL}' downloaded successfully!")
#                     except Exception as pull_error:
#                         st.warning(f"Could not download model automatically: {str(pull_error)}")
#                         st.info("Please run: `ollama pull mistral` in your terminal")
#                         return False
            
#             return True
#     except requests.exceptions.ConnectionError:
#         st.warning("Ollama service is not running. Starting Ollama...")
#         return start_ollama_service()
#     except Exception as e:
#         st.warning(f"Ollama service check failed: {str(e)}")
#         return False

# def start_ollama_service():
#     """Attempt to start Ollama service"""
#     try:
#         import subprocess
#         import os
        
#         # Try to start Ollama in the background
#         env = os.environ.copy()
#         env['OLLAMA_HOST'] = '0.0.0.0:11434'
        
#         subprocess.Popen(['ollama', 'serve'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
#         # Wait a bit for the service to start
#         time.sleep(5)
        
#         # Check if it's running
#         try:
#             response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
#             if response.status_code == 200:
#                 st.success("Ollama service started successfully!")
#                 return True
#         except:
#             pass
            
#         st.warning("Could not start Ollama automatically. Please run 'ollama serve' manually.")
#         return False
        
#     except Exception as e:
#         st.warning(f"Could not start Ollama service: {str(e)}")
#         return False

# def generate_ollama_response(prompt, system_prompt="You are a helpful AI assistant.", max_tokens=None):
#     """Generate response using Ollama with performance optimizations"""
#     try:
#         # Configure options for maximum speed
#         options = {
#             'temperature': 0.1,  # Very low temperature for fastest responses
#             'top_p': 0.7,
#             'top_k': 20,
#             'num_ctx': 1024,  # Very small context window for speed
#             'repeat_penalty': 1.1,
#         }
        
#         if max_tokens:
#             options['num_predict'] = max_tokens
        
#         response = ollama.chat(
#             model=OLLAMA_MODEL,
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": prompt}
#             ],
#             options=options,
#             stream=False
#         )
#         return response["message"]["content"]
#     except Exception as e:
#         st.error(f"Error generating response with Ollama: {str(e)}")
#         raise

# def generate_summary(text: str, length: str = "medium") -> str:
#     """Generate optimized summary using Ollama Mistral"""
#     try:
#         # Extremely aggressive text limiting for speed
#         max_chars = 1000 if length == "short" else 1500 if length == "medium" else 2000
        
#         if len(text) > max_chars:
#             processed_text = text[:max_chars]
#         else:
#             processed_text = text
        
#         # Ultra-simple prompt for maximum speed
#         length_tokens = {"short": 30, "medium": 100, "long": 200}
#         max_tokens = length_tokens.get(length, 100)
        
#         prompt = f"Summarize in {max_tokens} words:\n{processed_text}"
        
#         # Generate summary with timeout protection
#         import signal
        
#         def timeout_handler(signum, frame):
#             raise TimeoutError("Summary generation timed out")
        
#         signal.signal(signal.SIGALRM, timeout_handler)
#         signal.alarm(30)  # 30 second timeout
        
#         try:
#             summary = generate_ollama_response(
#                 prompt, 
#                 "Summarize briefly.", 
#                 max_tokens
#             )
#             signal.alarm(0)  # Cancel timeout
#         except TimeoutError:
#             signal.alarm(0)
#             raise Exception("Summary generation timed out (30s). Try a shorter document.")
        
#         if not summary or not summary.strip():
#             raise Exception("Empty summary generated")
            
#         return summary.strip()
        
#     except Exception as e:
#         error_msg = f"Failed to generate summary: {str(e)}"
#         st.error(error_msg)
#         raise Exception(error_msg)

# def answer_question(document_text: str, question: str) -> str:
#     """Fast question answering using Ollama Mistral"""
#     try:
#         # Aggressive text limiting for speed
#         max_chars = 3000
#         if len(document_text) > max_chars:
#             processed_text = document_text[:max_chars] + "..."
#         else:
#             processed_text = document_text
        
#         # Simple, fast prompt
#         prompt = f"Answer briefly: {question}\n\nDocument: {processed_text}"
        
#         # Generate answer with speed optimizations
#         answer = generate_ollama_response(
#             prompt, 
#             "Answer questions concisely based on the document.", 
#             max_tokens=150
#         )
        
#         if not answer or not answer.strip():
#             raise Exception("Empty answer generated")
            
#         return answer.strip()
        
#     except Exception as e:
#         error_msg = f"Failed to generate answer: {str(e)}"
#         st.error(error_msg)
#         raise Exception(error_msg)

# def analyze_document_topics(text: str) -> dict:
#     """
#     Analyze the document to identify main topics and themes using Ollama Mistral
    
#     Args:
#         text (str): The document text
    
#     Returns:
#         dict: Analysis results with topics, themes, and key entities
#     """
#     try:
#         # Check if Ollama service is available
#         if not check_ollama_service():
#             raise Exception("Ollama service is not available")
        
#         prompt = f"""
# Please analyze the following document and provide a structured analysis in JSON format.

# Include:
# 1. main_topics: List of 3-5 main topics covered
# 2. key_themes: List of 2-3 overarching themes
# 3. document_type: Classification of document type (e.g., research paper, report, manual, etc.)
# 4. key_entities: Important people, organizations, dates, or locations mentioned
# 5. complexity_level: Rate from 1-5 (1=simple, 5=highly technical)

# Document text:
# {text[:4000]}

# Respond with valid JSON only:
# """
        
#         system_prompt = "You are a document analysis expert. Analyze documents and provide structured insights in JSON format. Always respond with valid JSON."
        
#         # Generate analysis using Ollama
#         response_text = generate_ollama_response(prompt, system_prompt)
        
#         # Try to parse JSON response
#         try:
#             analysis = json.loads(response_text)
#             return analysis
#         except json.JSONDecodeError:
#             # If JSON parsing fails, extract key information manually
#             return {
#                 "main_topics": ["Document analysis completed"],
#                 "key_themes": ["Content analyzed"],
#                 "document_type": "Document",
#                 "key_entities": [],
#                 "complexity_level": 3
#             }
        
#     except Exception as e:
#         error_msg = f"Failed to analyze document: {str(e)}"
#         st.warning(error_msg)
#         return {
#             "main_topics": ["Unable to analyze"],
#             "key_themes": ["Analysis failed"],
#             "document_type": "Unknown",
#             "key_entities": [],
#             "complexity_level": 0
#         }

# def generate_questions(text: str, num_questions: int = 5) -> list:
#     """
#     Generate potential questions that could be asked about the document using Ollama Mistral
    
#     Args:
#         text (str): The document text
#         num_questions (int): Number of questions to generate
    
#     Returns:
#         list: List of suggested questions
#     """
#     try:
#         # Check if Ollama service is available
#         if not check_ollama_service():
#             raise Exception("Ollama service is not available")
        
#         prompt = f"""
# Based on the following document, generate {num_questions} insightful questions that would help someone understand the key concepts and information in the document.

# Make the questions:
# 1. Specific to the document content
# 2. Varied in complexity (some simple, some analytical)
# 3. Cover different aspects of the document
# 4. Helpful for comprehension and learning

# Document:
# {text[:4000]}

# Generate exactly {num_questions} questions, one per line, without numbering:
# """
        
#         system_prompt = "You are an educational expert who generates insightful questions to help people understand documents better."
        
#         # Generate questions using Ollama
#         questions_text = generate_ollama_response(prompt, system_prompt)
#         questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
#         return questions[:num_questions]  # Ensure we don't exceed requested number
        
#     except Exception as e:
#         error_msg = f"Failed to generate questions: {str(e)}"
#         st.warning(error_msg)
#         return [
#             "What is the main topic of this document?",
#             "What are the key findings or conclusions?",
#             "What important information should I remember?",
#             "Are there any specific recommendations or actions mentioned?",
#             "What context or background information is provided?"
#         ]

# def extract_key_insights(text: str) -> dict:
#     """
#     Extract key insights, facts, and important information from the document using Ollama Mistral
    
#     Args:
#         text (str): The document text
    
#     Returns:
#         dict: Extracted insights and key information
#     """
#     try:
#         # Check if Ollama service is available
#         if not check_ollama_service():
#             raise Exception("Ollama service is not available")
        
#         prompt = f"""
# Please extract and organize the key insights from this document in JSON format.

# Include:
# 1. key_facts: List of 3-5 most important facts or findings
# 2. recommendations: Any recommendations, suggestions, or calls to action
# 3. important_dates: Significant dates mentioned
# 4. important_numbers: Key statistics, percentages, or numerical data
# 5. conclusions: Main conclusions or takeaways

# Document:
# {text[:4000]}

# Respond with valid JSON:
# """
        
#         system_prompt = "You are an information extraction expert. Extract and organize key insights from documents in structured JSON format. Always respond with valid JSON."
        
#         # Generate insights using Ollama
#         response_text = generate_ollama_response(prompt, system_prompt)
        
#         # Try to parse JSON response
#         try:
#             insights = json.loads(response_text)
#             return insights
#         except json.JSONDecodeError:
#             # If JSON parsing fails, return a basic structure
#             return {
#                 "key_facts": ["Key information extracted from document"],
#                 "recommendations": [],
#                 "important_dates": [],
#                 "important_numbers": [],
#                 "conclusions": ["Document analysis completed"]
#             }
        
#     except Exception as e:
#         error_msg = f"Failed to extract insights: {str(e)}"
#         st.warning(error_msg)
#         return {
#             "key_facts": ["Unable to extract insights"],
#             "recommendations": [],
#             "important_dates": [],
#             "important_numbers": [],
#             "conclusions": ["Extraction failed"]
#         }
