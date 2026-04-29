import os
import streamlit as st
import subprocess
import sys

def init_playwright():
    """
    Ensures Playwright browsers are installed in the Streamlit Cloud environment.
    This only runs once per session to save time and resources.
    """
    if 'playwright_installed' not in st.session_state:
        with st.spinner("Initializing browser environment..."):
            try:
                # Install chromium browser and its dependencies
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                st.session_state['playwright_installed'] = True
            except Exception as e:
                st.error(f"Error initializing Playwright: {e}")
