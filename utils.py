import re
import hashlib
from datetime import datetime, timedelta
import streamlit as st

def format_file_size(size_bytes):
    """
    Format file size in bytes to human readable format
    
    Args:
        size_bytes (int): File size in bytes
    
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text, length=100, add_ellipsis=True):
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        length (int): Maximum length
        add_ellipsis (bool): Whether to add "..." at the end
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= length:
        return text
    
    truncated = text[:length]
    
    if add_ellipsis:
        truncated += "..."
    
    return truncated

def clean_filename(filename):
    """
    Clean filename by removing invalid characters
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Cleaned filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra spaces and dots
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.strip()
    
    return filename

def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    
    Args:
        filename (str): File name
        allowed_extensions (list): List of allowed extensions
    
    Returns:
        bool: True if extension is allowed
    """
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1]
    return f".{file_extension}" in [ext.lower() for ext in allowed_extensions]

def sanitize_text(text):
    """
    Sanitize text by removing potentially harmful content
    
    Args:
        text (str): Text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential script tags and other dangerous HTML
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Remove all HTML tags
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def generate_unique_id(prefix="doc"):
    """
    Generate a unique ID with timestamp and hash
    
    Args:
        prefix (str): Prefix for the ID
    
    Returns:
        str: Unique ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    
    return f"{prefix}_{timestamp}_{random_hash}"

def format_datetime(dt, format_string="%Y-%m-%d %H:%M:%S"):
    """
    Format datetime object to string
    
    Args:
        dt (datetime): Datetime object
        format_string (str): Format string
    
    Returns:
        str: Formatted datetime string
    """
    if not dt:
        return "Unknown"
    
    return dt.strftime(format_string)

def time_ago(dt):
    """
    Get human-readable time difference
    
    Args:
        dt (datetime): Datetime to compare
    
    Returns:
        str: Human-readable time difference
    """
    if not dt:
        return "Unknown"
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def count_words(text):
    """
    Count words in text
    
    Args:
        text (str): Text to count words in
    
    Returns:
        int: Word count
    """
    if not text:
        return 0
    
    # Remove extra whitespace and split by spaces
    words = re.findall(r'\b\w+\b', text.lower())
    return len(words)

def count_sentences(text):
    """
    Count sentences in text
    
    Args:
        text (str): Text to count sentences in
    
    Returns:
        int: Sentence count
    """
    if not text:
        return 0
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return len(sentences)

def extract_keywords(text, max_keywords=10):
    """
    Extract keywords from text (simple frequency-based approach)
    
    Args:
        text (str): Text to extract keywords from
        max_keywords (int): Maximum number of keywords to return
    
    Returns:
        list: List of keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'within',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Filter words
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequency
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_keywords[:max_keywords]]

def validate_question(question):
    """
    Validate if a question is appropriate for Q&A
    
    Args:
        question (str): Question to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Question cannot be empty"
    
    if len(question.strip()) < 3:
        return False, "Question too short (minimum 3 characters)"
    
    if len(question.strip()) > 500:
        return False, "Question too long (maximum 500 characters)"
    
    # Check for potentially inappropriate content (basic check)
    inappropriate_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'<.*?>',
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return False, "Question contains inappropriate content"
    
    return True, ""

def get_text_statistics(text):
    """
    Get comprehensive text statistics
    
    Args:
        text (str): Text to analyze
    
    Returns:
        dict: Dictionary containing text statistics
    """
    if not text:
        return {
            'character_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0,
            'average_words_per_sentence': 0,
            'reading_time_minutes': 0
        }
    
    char_count = len(text)
    word_count = count_words(text)
    sentence_count = count_sentences(text)
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    avg_words_per_sentence = round(word_count / sentence_count, 1) if sentence_count > 0 else 0
    reading_time = round(word_count / 200, 1)  # Assuming 200 words per minute reading speed
    
    return {
        'character_count': char_count,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'average_words_per_sentence': avg_words_per_sentence,
        'reading_time_minutes': reading_time
    }

def create_download_link(content, filename, mime_type="text/plain"):
    """
    Create a download link for content (for use with st.download_button)
    
    Args:
        content (str): Content to download
        filename (str): Suggested filename
        mime_type (str): MIME type of the content
    
    Returns:
        dict: Dictionary with download parameters
    """
    return {
        'data': content,
        'file_name': clean_filename(filename),
        'mime': mime_type
    }

def log_user_action(user_id, action, details=None):
    """
    Log user actions (for debugging/analytics)
    
    Args:
        user_id (str): User ID
        action (str): Action performed
        details (dict): Additional details
    """
    # In a production environment, this would log to a proper logging system
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'user_id': user_id,
        'action': action,
        'details': details or {}
    }
    
    # For now, we'll just store in session state for debugging
    if 'user_action_log' not in st.session_state:
        st.session_state['user_action_log'] = []
    
    st.session_state['user_action_log'].append(log_entry)
    
    # Keep only last 100 log entries to prevent memory issues
    if len(st.session_state['user_action_log']) > 100:
        st.session_state['user_action_log'] = st.session_state['user_action_log'][-100:]

def display_success_message(message, duration=3):
    """
    Display a success message with auto-dismiss
    
    Args:
        message (str): Success message to display
        duration (int): Duration in seconds (not implemented in Streamlit)
    """
    st.success(message)

def display_error_message(message, details=None):
    """
    Display an error message with optional details
    
    Args:
        message (str): Error message to display
        details (str): Additional error details
    """
    st.error(message)
    
    if details:
        with st.expander("Error Details"):
            st.text(details)

def display_warning_message(message):
    """
    Display a warning message
    
    Args:
        message (str): Warning message to display
    """
    st.warning(message)

def display_info_message(message):
    """
    Display an info message
    
    Args:
        message (str): Info message to display
    """
    st.info(message)
