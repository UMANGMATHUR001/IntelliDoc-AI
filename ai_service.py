import os
import json
import ollama
import streamlit as st
import time
from typing import Optional
import requests
import time

# Initialize Ollama client
OLLAMA_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_service():
    """Check if Ollama service is running and model is available"""
    try:
        # Check if Ollama is running
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "").split(":")[0] for model in models]
            
            if OLLAMA_MODEL not in model_names:
                with st.spinner(f"Downloading {OLLAMA_MODEL} model..."):
                    try:
                        # Pull the model
                        ollama.pull(OLLAMA_MODEL)
                        st.success(f"Model '{OLLAMA_MODEL}' downloaded successfully!")
                    except Exception as pull_error:
                        st.warning(f"Could not download model automatically: {str(pull_error)}")
                        st.info("Please run: `ollama pull mistral` in your terminal")
                        return False
            
            return True
    except requests.exceptions.ConnectionError:
        st.warning("Ollama service is not running. Starting Ollama...")
        return start_ollama_service()
    except Exception as e:
        st.warning(f"Ollama service check failed: {str(e)}")
        return False

def start_ollama_service():
    """Attempt to start Ollama service"""
    try:
        import subprocess
        import os
        
        # Try to start Ollama in the background
        env = os.environ.copy()
        env['OLLAMA_HOST'] = '0.0.0.0:11434'
        
        subprocess.Popen(['ollama', 'serve'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a bit for the service to start
        time.sleep(5)
        
        # Check if it's running
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                st.success("Ollama service started successfully!")
                return True
        except:
            pass
            
        st.warning("Could not start Ollama automatically. Please run 'ollama serve' manually.")
        return False
        
    except Exception as e:
        st.warning(f"Could not start Ollama service: {str(e)}")
        return False

def generate_ollama_response(prompt, system_prompt="You are a helpful AI assistant.", max_tokens=None):
    """Generate response using Ollama with performance optimizations"""
    try:
        # Configure options for faster response
        options = {
            'temperature': 0.3,  # Lower temperature for faster, more focused responses
            'top_p': 0.9,
            'top_k': 40,
            'num_ctx': 2048,  # Reduced context window for speed
        }
        
        if max_tokens:
            options['num_predict'] = max_tokens
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options=options,
            stream=False
        )
        return response["message"]["content"]
    except Exception as e:
        st.error(f"Error generating response with Ollama: {str(e)}")
        raise

def generate_summary(text: str, length: str = "medium") -> str:
    """
    Generate a summary of the provided text using Ollama Mistral
    
    Args:
        text (str): The text to summarize
        length (str): Summary length - "short", "medium", or "long"
    
    Returns:
        str: Generated summary
    """
    try:
        # Check if Ollama service is available
        if not check_ollama_service():
            raise Exception("Ollama service is not available")
        
        # Define length specifications
        length_specs = {
            "short": "in 2-3 sentences, focusing only on the most critical points",
            "medium": "in 1-2 paragraphs, covering the main topics and key details",
            "long": "in 3-4 paragraphs, providing comprehensive coverage of all major points and supporting details"
        }
        
        length_instruction = length_specs.get(length, length_specs["medium"])
        
        # Optimize text processing for speed
        max_chars = 3000 if length == "short" else 4000 if length == "medium" else 5000
        
        if len(text) > max_chars:
            # Take first and last portions for better context
            first_part = text[:max_chars//2]
            last_part = text[-(max_chars//2):]
            processed_text = first_part + "\n...[content truncated]...\n" + last_part
        else:
            processed_text = text
        
        # Create optimized prompt
        prompt = f"Summarize this document {length_instruction}:\n\n{processed_text}"
        
        system_prompt = "You are an expert document analyst. Provide clear, accurate summaries."
        
        # Set max tokens based on summary type
        max_tokens = 100 if length == "short" else 200 if length == "medium" else 400
        
        # Show progress to user
        progress_placeholder = st.empty()
        progress_placeholder.info("🤖 Generating summary...")
        
        start_time = time.time()
        
        # Generate summary using Ollama
        summary = generate_ollama_response(prompt, system_prompt, max_tokens)
        
        elapsed_time = time.time() - start_time
        progress_placeholder.success(f"✅ Summary ready in {elapsed_time:.1f}s")
        
        if not summary or not summary.strip():
            raise Exception("Empty summary generated")
            
        return summary.strip()
        
    except Exception as e:
        error_msg = f"Failed to generate summary: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)

def answer_question(document_text: str, question: str) -> str:
    """
    Answer a question based on the document content using Ollama Mistral
    
    Args:
        document_text (str): The document content
        question (str): The user's question
    
    Returns:
        str: Generated answer
    """
    try:
        # Check if Ollama service is available
        if not check_ollama_service():
            raise Exception("Ollama service is not available")
        
        # Optimize document text for faster processing
        max_chars = 4000
        if len(document_text) > max_chars:
            # Use first part and try to find relevant sections
            processed_text = document_text[:max_chars] + "...[document continues]"
        else:
            processed_text = document_text
        
        # Create optimized prompt
        prompt = f"Based on this document, answer: {question}\n\nDocument:\n{processed_text}"
        
        system_prompt = "Answer questions using only the provided document. Be concise and accurate."
        
        # Show progress to user
        progress_placeholder = st.empty()
        progress_placeholder.info("🤖 Finding answer...")
        
        start_time = time.time()
        
        # Generate answer using Ollama with token limit
        answer = generate_ollama_response(prompt, system_prompt, max_tokens=200)
        
        elapsed_time = time.time() - start_time
        progress_placeholder.success(f"✅ Answer ready in {elapsed_time:.1f}s")
        
        if not answer or not answer.strip():
            raise Exception("Empty answer generated")
            
        return answer.strip()
        
    except Exception as e:
        error_msg = f"Failed to generate answer: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)

def analyze_document_topics(text: str) -> dict:
    """
    Analyze the document to identify main topics and themes using Ollama Mistral
    
    Args:
        text (str): The document text
    
    Returns:
        dict: Analysis results with topics, themes, and key entities
    """
    try:
        # Check if Ollama service is available
        if not check_ollama_service():
            raise Exception("Ollama service is not available")
        
        prompt = f"""
Please analyze the following document and provide a structured analysis in JSON format.

Include:
1. main_topics: List of 3-5 main topics covered
2. key_themes: List of 2-3 overarching themes
3. document_type: Classification of document type (e.g., research paper, report, manual, etc.)
4. key_entities: Important people, organizations, dates, or locations mentioned
5. complexity_level: Rate from 1-5 (1=simple, 5=highly technical)

Document text:
{text[:4000]}

Respond with valid JSON only:
"""
        
        system_prompt = "You are a document analysis expert. Analyze documents and provide structured insights in JSON format. Always respond with valid JSON."
        
        # Generate analysis using Ollama
        response_text = generate_ollama_response(prompt, system_prompt)
        
        # Try to parse JSON response
        try:
            analysis = json.loads(response_text)
            return analysis
        except json.JSONDecodeError:
            # If JSON parsing fails, extract key information manually
            return {
                "main_topics": ["Document analysis completed"],
                "key_themes": ["Content analyzed"],
                "document_type": "Document",
                "key_entities": [],
                "complexity_level": 3
            }
        
    except Exception as e:
        error_msg = f"Failed to analyze document: {str(e)}"
        st.warning(error_msg)
        return {
            "main_topics": ["Unable to analyze"],
            "key_themes": ["Analysis failed"],
            "document_type": "Unknown",
            "key_entities": [],
            "complexity_level": 0
        }

def generate_questions(text: str, num_questions: int = 5) -> list:
    """
    Generate potential questions that could be asked about the document using Ollama Mistral
    
    Args:
        text (str): The document text
        num_questions (int): Number of questions to generate
    
    Returns:
        list: List of suggested questions
    """
    try:
        # Check if Ollama service is available
        if not check_ollama_service():
            raise Exception("Ollama service is not available")
        
        prompt = f"""
Based on the following document, generate {num_questions} insightful questions that would help someone understand the key concepts and information in the document.

Make the questions:
1. Specific to the document content
2. Varied in complexity (some simple, some analytical)
3. Cover different aspects of the document
4. Helpful for comprehension and learning

Document:
{text[:4000]}

Generate exactly {num_questions} questions, one per line, without numbering:
"""
        
        system_prompt = "You are an educational expert who generates insightful questions to help people understand documents better."
        
        # Generate questions using Ollama
        questions_text = generate_ollama_response(prompt, system_prompt)
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        return questions[:num_questions]  # Ensure we don't exceed requested number
        
    except Exception as e:
        error_msg = f"Failed to generate questions: {str(e)}"
        st.warning(error_msg)
        return [
            "What is the main topic of this document?",
            "What are the key findings or conclusions?",
            "What important information should I remember?",
            "Are there any specific recommendations or actions mentioned?",
            "What context or background information is provided?"
        ]

def extract_key_insights(text: str) -> dict:
    """
    Extract key insights, facts, and important information from the document using Ollama Mistral
    
    Args:
        text (str): The document text
    
    Returns:
        dict: Extracted insights and key information
    """
    try:
        # Check if Ollama service is available
        if not check_ollama_service():
            raise Exception("Ollama service is not available")
        
        prompt = f"""
Please extract and organize the key insights from this document in JSON format.

Include:
1. key_facts: List of 3-5 most important facts or findings
2. recommendations: Any recommendations, suggestions, or calls to action
3. important_dates: Significant dates mentioned
4. important_numbers: Key statistics, percentages, or numerical data
5. conclusions: Main conclusions or takeaways

Document:
{text[:4000]}

Respond with valid JSON:
"""
        
        system_prompt = "You are an information extraction expert. Extract and organize key insights from documents in structured JSON format. Always respond with valid JSON."
        
        # Generate insights using Ollama
        response_text = generate_ollama_response(prompt, system_prompt)
        
        # Try to parse JSON response
        try:
            insights = json.loads(response_text)
            return insights
        except json.JSONDecodeError:
            # If JSON parsing fails, return a basic structure
            return {
                "key_facts": ["Key information extracted from document"],
                "recommendations": [],
                "important_dates": [],
                "important_numbers": [],
                "conclusions": ["Document analysis completed"]
            }
        
    except Exception as e:
        error_msg = f"Failed to extract insights: {str(e)}"
        st.warning(error_msg)
        return {
            "key_facts": ["Unable to extract insights"],
            "recommendations": [],
            "important_dates": [],
            "important_numbers": [],
            "conclusions": ["Extraction failed"]
        }
