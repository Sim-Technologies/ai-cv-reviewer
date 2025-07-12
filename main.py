import streamlit as st
import time
import asyncio
from app.ui.components import (
    render_file_upload, render_processing_status,
    render_complete_results, render_about_section,
    render_file_preview, render_processing_sidebar
)
from app.utils.llm_config import validate_api_key
from app.graph.workflow import run_cv_review_async
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
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.get('file_uploaded', False):
            uploaded_file = st.session_state.uploaded_file
            render_file_preview(st.session_state.uploaded_file)
        else:
            render_about_section() 
    
    with col2:
        # File upload section - only show if no file uploaded yet
        if not st.session_state.get('file_uploaded', False):
            uploaded_file = render_file_upload()
            
            if uploaded_file is not None:
                # Set uploaded state
                st.session_state.file_uploaded = True
                st.session_state.uploaded_file = uploaded_file
                st.rerun()

        else:
            if not st.session_state.get('processing_started', False):
                st.subheader("🚀 Ready to Review")
                st.write("Your CV has been uploaded successfully. Click the button below to start the AI review process.")
                
                if st.button("🚀 Start CV Review", type="primary", use_container_width=True):
                    st.session_state.processing_started = True
                    st.rerun()
                
                # Option to upload different file
                if st.button("📄 Upload Different File", use_container_width=True):
                    # Clear uploaded state
                    st.session_state.file_uploaded = False
                    if 'uploaded_file' in st.session_state:
                        del st.session_state.uploaded_file
                    st.rerun()

            else:
                try:
                    # Create progress container
                    progress_container = st.container()
                    
                    with progress_container:
                        if st.session_state.get('progress', 0) < 100:
                            st.info("🔄 Processing your CV... This may take a few minutes.")
                        
                        # Initialize progress
                        if 'progress' not in st.session_state:
                            st.session_state.progress = 5
                            st.session_state.status_text = "📄 Processing uploaded file..."
                        
                        # Create a progress bar
                        progress_bar = st.progress(st.session_state.progress / 100)
                        status_text = st.empty()
                        status_text.text(st.session_state.status_text)
                        
                        # Run CV review workflow asynchronously
                        async def process_cv():
                            final_result = None
                            async for state in run_cv_review_async(uploaded_file):
                                final_result = state
                                
                                # Update progress based on status
                                if state.processing_status == "processed_file_complete":
                                    st.session_state.progress = 15
                                    st.session_state.status_text = "📖 Extracting data from CV..."
                                elif state.processing_status == "extraction_complete":
                                    st.session_state.progress = 30
                                    st.session_state.status_text = "🔍 Analyzing CV content..."
                                elif state.processing_status == "analysis_complete":
                                    st.session_state.progress = 50
                                    st.session_state.status_text = "💬 Generating feedback..."
                                elif state.processing_status == "feedback_complete":
                                    st.session_state.progress = 75
                                    st.session_state.status_text = "🎯 Generating recommendations..."
                                elif state.processing_status == "complete":
                                    st.session_state.progress = 100
                                    st.session_state.status_text = "✅ CV review completed!"
                                elif state.processing_status == "failed":
                                    st.session_state.progress = 0
                                    st.session_state.status_text = "❌ Processing failed"
                                
                                # Update UI
                                progress_bar.progress(st.session_state.progress / 100)
                                status_text.text(st.session_state.status_text)
                                
                                # Small delay to show progress
                                await asyncio.sleep(0.5)
                            
                            return final_result
                        
                        # Run the async function
                        result = asyncio.run(process_cv())
                        
                        # Small delay to show completion
                        time.sleep(0.5)
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                    
                    # Store result in session state
                    st.session_state.cv_review_result = result
                    
                    # Clear processing flags
                    st.session_state.processing_started = False
                    st.session_state.file_uploaded = False
                    if 'uploaded_file' in st.session_state:
                        del st.session_state.uploaded_file
                    
                    # Clear progress state
                    if 'progress' in st.session_state:
                        del st.session_state.progress
                    if 'status_text' in st.session_state:
                        del st.session_state.status_text
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    # Clear processing flag on error
                    st.session_state.processing_started = False
                    st.stop()

        # Display results if available
        if hasattr(st.session_state, 'cv_review_result'):
            result = st.session_state.cv_review_result
            
            # Show processing status
            render_processing_status(result.processing_status)
            
            # Show results
            render_complete_results(result)
            
            # Add a button to clear results
            if st.button("🔄 Review Another CV", use_container_width=True):
                if 'cv_review_result' in st.session_state:
                    del st.session_state.cv_review_result
                st.rerun()


if __name__ == "__main__":
    main() 