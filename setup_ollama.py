#!/usr/bin/env python3
"""
Setup script for Ollama service and Mistral model
This script helps initialize Ollama for the PDF Summarizer application
"""

import subprocess
import time
import requests
import sys
import os

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Ollama is not installed")
    return False

def start_ollama_service():
    """Start Ollama service"""
    try:
        print("Starting Ollama service...")
        
        # Set environment variable for host binding
        env = os.environ.copy()
        env['OLLAMA_HOST'] = '0.0.0.0:11434'
        
        # Start Ollama in background
        process = subprocess.Popen(
            ['ollama', 'serve'],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for service to start
        for i in range(10):
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    print("✓ Ollama service is running")
                    return True
            except:
                time.sleep(1)
        
        print("✗ Failed to start Ollama service")
        return False
        
    except Exception as e:
        print(f"✗ Error starting Ollama: {e}")
        return False

def check_mistral_model():
    """Check if Mistral model is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '').split(':')[0] for model in models]
            
            if 'mistral' in model_names:
                print("✓ Mistral model is available")
                return True
            else:
                print("✗ Mistral model not found")
                return False
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False

def pull_mistral_model():
    """Pull Mistral model"""
    try:
        print("Downloading Mistral model (this may take a few minutes)...")
        result = subprocess.run(['ollama', 'pull', 'mistral'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Mistral model downloaded successfully")
            return True
        else:
            print(f"✗ Failed to download Mistral model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Model download timed out")
        return False
    except Exception as e:
        print(f"✗ Error downloading model: {e}")
        return False

def test_model():
    """Test the Mistral model with a simple prompt"""
    try:
        print("Testing Mistral model...")
        
        import ollama
        response = ollama.chat(
            model='mistral',
            messages=[
                {
                    'role': 'user',
                    'content': 'Say hello in one sentence.'
                }
            ]
        )
        
        if response and 'message' in response:
            print("✓ Mistral model is working correctly")
            print(f"  Test response: {response['message']['content'][:50]}...")
            return True
        else:
            print("✗ Model test failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing model: {e}")
        return False

def main():
    """Main setup function"""
    print("=== Ollama Setup for PDF Summarizer ===\n")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\nPlease install Ollama first:")
        print("Visit: https://ollama.ai/download")
        sys.exit(1)
    
    # Start Ollama service
    if not start_ollama_service():
        print("\nFailed to start Ollama service. Try running manually:")
        print("OLLAMA_HOST=0.0.0.0:11434 ollama serve")
        sys.exit(1)
    
    # Check if Mistral model exists
    if not check_mistral_model():
        print("\nMistral model not found. Downloading...")
        if not pull_mistral_model():
            print("\nFailed to download Mistral model. Try running manually:")
            print("ollama pull mistral")
            sys.exit(1)
    
    # Test the model
    if not test_model():
        print("\nModel test failed. Please check your setup.")
        sys.exit(1)
    
    print("\n✓ Setup complete! Your PDF Summarizer is ready to use.")
    print("\nThe application will now use Ollama with Mistral model for:")
    print("  • PDF document summarization")
    print("  • Question & Answer functionality") 
    print("  • Document topic analysis")

if __name__ == "__main__":
    main()