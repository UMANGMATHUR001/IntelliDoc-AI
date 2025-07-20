import fitz  # PyMuPDF
import streamlit as st
from io import BytesIO
import re

def validate_pdf(uploaded_file) -> bool:
    """Validate if the uploaded file is a valid PDF"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Check if file starts with PDF signature
        first_bytes = uploaded_file.read(8)
        uploaded_file.seek(0)
        
        if not first_bytes.startswith(b'%PDF-'):
            return False
        
        # Try to open with PyMuPDF
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        doc.close()
        
        return True
        
    except Exception as e:
        st.warning(f"PDF validation failed: {str(e)}")
        return False

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text content from PDF file - optimized for speed"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read file bytes
        file_bytes = uploaded_file.read()
        
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        extracted_text = ""
        max_pages = min(doc.page_count, 50)  # Limit to 50 pages for speed
        
        # Extract text from each page (optimized)
        for page_num in range(max_pages):
            page = doc.load_page(page_num)
            
            # Get text from page (faster method)
            page_text = page.get_text("text")  # Use simple text extraction
            
            if page_text.strip():
                if page_num > 0:
                    extracted_text += "\n\n"
                extracted_text += page_text
            
        # Close the document
        doc.close()
        
        # Quick cleanup (remove excessive whitespace only)
        extracted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', extracted_text)
        extracted_text = re.sub(r' +', ' ', extracted_text)
        
        return extracted_text.strip()
        
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        raise

def clean_extracted_text(text: str) -> str:
    """Clean and format extracted text"""
    try:
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' +', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('\x0c', '\n')  # Form feed to newline
        text = text.replace('\xa0', ' ')   # Non-breaking space to regular space
        
        # Remove very short lines that might be artifacts (less than 3 characters)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) >= 3 or line == "" or line.startswith('---'):
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines
        cleaned_text = re.sub(r'\n\n\n+', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
        
    except Exception as e:
        st.warning(f"Text cleaning error: {str(e)}")
        return text

def get_pdf_metadata(uploaded_file) -> dict:
    """Extract metadata from PDF file"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read file bytes
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Get metadata
        metadata = doc.metadata
        
        # Get page count
        page_count = doc.page_count
        
        # Get file size
        file_size = len(file_bytes)
        
        doc.close()
        
        return {
            'title': metadata.get('title', 'Unknown'),
            'author': metadata.get('author', 'Unknown'),
            'subject': metadata.get('subject', 'Unknown'),
            'creator': metadata.get('creator', 'Unknown'),
            'producer': metadata.get('producer', 'Unknown'),
            'creation_date': metadata.get('creationDate', 'Unknown'),
            'modification_date': metadata.get('modDate', 'Unknown'),
            'page_count': page_count,
            'file_size': file_size
        }
        
    except Exception as e:
        st.warning(f"Error extracting PDF metadata: {str(e)}")
        return {
            'title': 'Unknown',
            'author': 'Unknown',
            'subject': 'Unknown',
            'creator': 'Unknown',
            'producer': 'Unknown',
            'creation_date': 'Unknown',
            'modification_date': 'Unknown',
            'page_count': 0,
            'file_size': 0
        }

def extract_text_by_page(uploaded_file) -> dict:
    """Extract text from PDF and return page-by-page breakdown"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read file bytes
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        pages_text = {}
        
        # Extract text from each page
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            
            # Clean the text
            cleaned_text = clean_extracted_text(page_text)
            
            pages_text[page_num + 1] = {
                'text': cleaned_text,
                'char_count': len(cleaned_text),
                'word_count': len(cleaned_text.split()) if cleaned_text else 0
            }
        
        # Close the document
        doc.close()
        
        return pages_text
        
    except Exception as e:
        st.error(f"Error extracting text by page: {str(e)}")
        raise

def search_text_in_pdf(uploaded_file, search_term: str, case_sensitive: bool = False) -> list:
    """Search for specific text in PDF and return matches with page numbers"""
    try:
        pages_text = extract_text_by_page(uploaded_file)
        matches = []
        
        for page_num, page_data in pages_text.items():
            text = page_data['text']
            
            if not case_sensitive:
                search_text = text.lower()
                term = search_term.lower()
            else:
                search_text = text
                term = search_term
            
            if term in search_text:
                # Find all occurrences in this page
                start = 0
                while True:
                    pos = search_text.find(term, start)
                    if pos == -1:
                        break
                    
                    # Get context around the match
                    context_start = max(0, pos - 100)
                    context_end = min(len(text), pos + len(search_term) + 100)
                    context = text[context_start:context_end]
                    
                    matches.append({
                        'page': page_num,
                        'position': pos,
                        'context': context,
                        'match_text': text[pos:pos + len(search_term)]
                    })
                    
                    start = pos + 1
        
        return matches
        
    except Exception as e:
        st.error(f"Error searching text in PDF: {str(e)}")
        return []
