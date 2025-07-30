#!/usr/bin/env python3
"""
Performance optimization utilities for AI services (Gemini-focused)
"""

import time
import shutil
import streamlit as st
from typing import Dict, Any

class PerformanceOptimizer:
    """Optimize system performance for faster AI responses"""
    
    def __init__(self):
        pass
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check disk space only (no psutil)."""
        try:
            total, used, free = shutil.disk_usage('/')
            return {
                "disk_free_gb": free / (1024**3),
                "disk_total_gb": total / (1024**3)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_performance_status(self) -> bool:
        """Show simple performance messages (disk check only)."""
        try:
            resources = self.check_system_resources()
            if "error" not in resources:
                if resources["disk_free_gb"] < 1:
                    st.warning("⚠️ Low disk space detected. Free some space for better performance.")
            return True
        except Exception as e:
            st.warning(f"⚠️ Performance check: {e}")
            return False
    
    def display_system_info(self) -> None:
        """Display basic disk info."""
        resources = self.check_system_resources()
        if "error" not in resources:
            st.metric("Disk Free", f"{resources['disk_free_gb']:.1f} GB")
    
    def get_performance_tips(self) -> list:
        """Get performance optimization tips."""
        return [
            "🚀 Use shorter summary types for faster responses",
            "📝 Upload smaller PDF files (under 10MB)",
            "🔄 First AI request may be slower",
            "📊 Short summaries: ~5-10 seconds, Medium: ~10-20 seconds"
        ]
    
    def monitor_response_time(self, operation_name: str):
        """Context manager to monitor operation response times."""
        class ResponseTimeMonitor:
            def __init__(self, name):
                self.name = name
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
        
        return ResponseTimeMonitor(operation_name)

def display_performance_dashboard():
    """Display performance monitoring dashboard."""
    optimizer = PerformanceOptimizer()
    
    st.sidebar.markdown("### 🚀 Performance Monitor")
    resources = optimizer.check_system_resources()
    
    if "error" not in resources:
        st.sidebar.metric("Disk Free", f"{resources['disk_free_gb']:.1f} GB")
        if resources["disk_free_gb"] < 1:
            st.sidebar.error("🔴 Low Disk Space")
        else:
            st.sidebar.success("🟢 Sufficient Disk Space")
    
    if st.sidebar.button("💡 Performance Tips"):
        for tip in optimizer.get_performance_tips():
            st.sidebar.info(tip)
    
    if st.sidebar.button("📊 System Info"):
        optimizer.display_system_info()
    
    return optimizer

def apply_speed_optimizations():
    """Apply various speed optimizations."""
    if "page_config_set" not in st.session_state:
        st.set_page_config(
            page_title="AskMyPDF- Smart PDF Analysis",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.session_state.page_config_set = True
    
    if "performance_optimizer" not in st.session_state:
        st.session_state.performance_optimizer = PerformanceOptimizer()
        st.session_state.performance_optimizer.check_performance_status()

def optimized_ai_operation(operation_func, operation_name, *args, **kwargs):
    """Wrapper for AI operations with performance monitoring."""
    optimizer = st.session_state.get("performance_optimizer", PerformanceOptimizer())
    with optimizer.monitor_response_time(operation_name):
        return operation_func(*args, **kwargs)
