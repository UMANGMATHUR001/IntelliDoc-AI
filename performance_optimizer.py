#!/usr/bin/env python3
"""
Performance optimization utilities for Ollama AI service
"""

import time
import requests
import psutil
import streamlit as st
from typing import Dict, Any

class OllamaPerformanceOptimizer:
    """Optimize Ollama performance for faster responses"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources that affect Ollama performance"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_ollama_settings(self) -> bool:
        """Apply optimal settings for Ollama service"""
        try:
            # Check if we can modify Ollama settings
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                st.warning("🔄 Ollama service is starting up...")
                return False
            
            # Log current performance status
            resources = self.check_system_resources()
            
            if "error" not in resources:
                if resources["memory_available_gb"] < 2:
                    st.warning("⚠️ Low memory detected. Consider closing other applications for better performance.")
                
                if resources["cpu_usage"] > 80:
                    st.warning("⚠️ High CPU usage detected. This may slow down AI responses.")
            
            return True
            
        except requests.exceptions.ConnectionError:
            st.info("🚀 Ollama service is starting up. Please wait a moment...")
            return False
        except Exception as e:
            st.warning(f"⚠️ Ollama service check: {e}")
            return False
    
    def warm_up_model(self, model_name: str = "mistral") -> bool:
        """Warm up the model for faster first response"""
        try:
            import ollama
            
            st.info("🔥 Warming up AI model for faster responses...")
            start_time = time.time()
            
            # Simple warm-up prompt
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                options={
                    'num_predict': 5,
                    'temperature': 0.1
                }
            )
            
            elapsed = time.time() - start_time
            
            if response:
                st.success(f"✅ Model warmed up successfully in {elapsed:.1f}s")
                return True
            else:
                st.warning("Model warm-up completed but no response received")
                return False
                
        except Exception as e:
            st.error(f"Model warm-up failed: {e}")
            return False
    
    def get_performance_tips(self) -> list:
        """Get performance optimization tips"""
        tips = [
            "🚀 Use shorter summary types for faster responses",
            "📝 Upload smaller PDF files when possible (under 10MB)",
            "⚡ Close other applications to free up system memory",
            "🔄 The first request is always slower - subsequent ones are faster",
            "📊 Short summaries: ~5-10 seconds, Medium: ~10-20 seconds",
            "💡 Ask specific questions instead of general ones for faster answers"
        ]
        return tips
    
    def monitor_response_time(self, operation_name: str):
        """Context manager to monitor operation response times"""
        class ResponseTimeMonitor:
            def __init__(self, name, optimizer):
                self.name = name
                self.optimizer = optimizer
                self.start_time = None
                
            def __enter__(self):
                self.start_time = time.time()
                st.info(f"⏳ Starting {self.name}...")
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.start_time:
                    elapsed = time.time() - self.start_time
                    if exc_type is None:
                        st.success(f"✅ {self.name} completed in {elapsed:.1f}s")
                    else:
                        st.error(f"❌ {self.name} failed after {elapsed:.1f}s")
        
        return ResponseTimeMonitor(operation_name, self)

def display_performance_dashboard():
    """Display performance monitoring dashboard"""
    optimizer = OllamaPerformanceOptimizer()
    
    st.sidebar.markdown("### 🚀 Performance Monitor")
    
    # System resources
    resources = optimizer.check_system_resources()
    
    if "error" not in resources:
        st.sidebar.metric("CPU Usage", f"{resources['cpu_usage']:.1f}%")
        st.sidebar.metric("Memory Usage", f"{resources['memory_usage']:.1f}%")
        st.sidebar.metric("Available Memory", f"{resources['memory_available_gb']:.1f}GB")
        
        # Performance status
        if resources["memory_available_gb"] < 2:
            st.sidebar.error("🔴 Low Memory")
        elif resources["memory_available_gb"] < 4:
            st.sidebar.warning("🟡 Medium Memory")
        else:
            st.sidebar.success("🟢 Good Memory")
    
    # Performance tips
    if st.sidebar.button("💡 Performance Tips"):
        tips = optimizer.get_performance_tips()
        for tip in tips:
            st.sidebar.info(tip)
    
    # Warm up model button
    if st.sidebar.button("🔥 Warm Up AI Model"):
        optimizer.warm_up_model()
    
    return optimizer

def apply_speed_optimizations():
    """Apply various speed optimizations"""
    
    # Set Streamlit page config for performance
    if "page_config_set" not in st.session_state:
        st.set_page_config(
            page_title="PDF AI Analyzer",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.session_state.page_config_set = True
    
    # Initialize performance optimizer
    if "performance_optimizer" not in st.session_state:
        st.session_state.performance_optimizer = OllamaPerformanceOptimizer()
        st.session_state.performance_optimizer.optimize_ollama_settings()

# Usage example function
def optimized_ai_operation(operation_func, operation_name, *args, **kwargs):
    """Wrapper for AI operations with performance monitoring"""
    optimizer = st.session_state.get("performance_optimizer", OllamaPerformanceOptimizer())
    
    with optimizer.monitor_response_time(operation_name):
        return operation_func(*args, **kwargs)