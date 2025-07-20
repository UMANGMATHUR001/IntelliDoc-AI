#!/usr/bin/env python3
"""
Performance optimization utilities for Ollama AI service
"""

import time
import requests
import psutil
import streamlit as st
from typing import Dict, Any

class PerformanceOptimizer:
    """Optimize system performance for faster AI responses"""
    
    def __init__(self):
        pass
        
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
    
    def check_performance_status(self) -> bool:
        """Check system performance status for optimal AI processing"""
        try:
            # Log current performance status
            resources = self.check_system_resources()
            
            if "error" not in resources:
                if resources["memory_available_gb"] < 2:
                    st.warning("⚠️ Low memory detected. Consider closing other applications for better performance.")
                
                if resources["cpu_usage"] > 80:
                    st.warning("⚠️ High CPU usage detected. This may slow down AI responses.")
            
            return True
            
        except Exception as e:
            st.warning(f"⚠️ Performance check: {e}")
            return False
    
    def display_system_info(self) -> None:
        """Display system information for debugging"""
        resources = self.check_system_resources()
        
        if "error" not in resources:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Usage", f"{resources['cpu_usage']:.1f}%")
            
            with col2:
                st.metric("Memory Available", f"{resources['memory_available_gb']:.1f} GB")
            
            with col3:
                st.metric("Disk Free", f"{resources['disk_free_gb']:.1f} GB")
    
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
    optimizer = PerformanceOptimizer()
    
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
    
    # System info button
    if st.sidebar.button("📊 System Info"):
        optimizer.display_system_info()
    
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
        st.session_state.performance_optimizer = PerformanceOptimizer()
        st.session_state.performance_optimizer.check_performance_status()

# Usage example function
def optimized_ai_operation(operation_func, operation_name, *args, **kwargs):
    """Wrapper for AI operations with performance monitoring"""
    optimizer = st.session_state.get("performance_optimizer", OllamaPerformanceOptimizer())
    
    with optimizer.monitor_response_time(operation_name):
        return operation_func(*args, **kwargs)