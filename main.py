import streamlit as st
from app.ui.sections import render_left_section, render_right_section
from app.utils.llm_config import validate_api_key
from dotenv import load_dotenv

load_dotenv()



def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="AI CV Reviewer",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .preview-container {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

    # API key validation
    if not validate_api_key():
        st.error("❌ Anthropic API key not configured or invalid")
        st.info("Please set your ANTHROPIC_API_KEY in the .env file")
        st.stop()

    # Main content area
    left_col, right_col = st.columns([1, 1])
    with left_col:
        render_left_section()
        
    with right_col:
        render_right_section()

if __name__ == "__main__":
    main()
