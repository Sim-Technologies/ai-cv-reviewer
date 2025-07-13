import streamlit as st
import asyncio
import time
from streamlit_pdf_viewer import pdf_viewer
from app.models import CVReviewState
from app.ui.components import (
    render_processing_status, 
    render_extracted_data, 
    render_analysis_results, 
    render_feedback, 
    render_recommendations, 
    render_download_button, 
    render_errors
)
from app.graph.workflow import CVReviewWorkflow
from .session_state import (
    set_uploaded_file, 
    has_file_uploaded, 
    clear_uploaded_file,
    set_processing_status,
    reset_session_state,
    set_progress,
    get_current_progress,
    set_cv_review_result,
    get_processing_status
)

def render_about_section():
    """Render the about section."""
    # About section
    st.header("🤖 AI CV Reviewer")
    st.markdown("""
    This AI CV Reviewer uses advanced language models to:

    - **Extract** structured data from your CV
    - **Analyze** your experiences, skills and education
    - **Provide** constructive feedback
    - **Suggest** improvements and career guidance
    
    Supported formats: PDF, DOCX, TXT
    """)

def render_processing_actions_section():
    """Render the processing actions."""
    section = st.empty()
    with section.container(height=600):
        st.subheader("🚀 Ready to Review")
        st.write("Your CV has been uploaded successfully. Click the button below to start the AI review process.")
        start_button = st.button("🚀 Start CV Review", type="primary", use_container_width=True)
        reset_button = st.button("📄 Upload Different File", use_container_width=True)
        
        if start_button:
            section.empty()
            set_processing_status('processing')
        
        if reset_button:
            clear_uploaded_file()

def render_file_upload_section():
    """Render the file upload section."""
    st.subheader("📄 Upload Your CV")
    
    uploaded_file = st.file_uploader(
        "Choose a CV file",
        type=['pdf', 'docx', 'txt']
    )

    if uploaded_file is not None:
        set_uploaded_file(uploaded_file)

def render_file_preview_section(uploaded_file):
    """Render file preview based on file type."""
    if uploaded_file is None:
        return
    
    file_name = uploaded_file.name
    file_extension = file_name.lower().split('.')[-1]
    
    st.subheader("📄 File Preview")
    
    if file_extension == 'pdf':
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()
        pdf_viewer(pdf_bytes, height=600)

    elif file_extension == 'docx':
        st.info("📄 DOCX files cannot be previewed directly")
        st.write("**File:** " + file_name)
        st.write("**Size:** " + f"{uploaded_file.size / 1024:.1f} KB")

    elif file_extension == 'txt':
        st.info("📄 Text file content:")
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        text_content = uploaded_file.read().decode('utf-8')
        st.text_area("Content", text_content, height=400, disabled=True)

    else:
        st.info(f"📄 File: {file_name}")

def render_complete_results_section(state: CVReviewState):
    with st.container(height=600):
        """Render complete results section."""
        if state.processing_status == ProcessingStatus.COMPLETED:
            st.success("🎉 CV review completed!")
            # Render each section
            if state.extracted_data:
                render_extracted_data(state.extracted_data)
            
            if state.analysis_results:
                render_analysis_results(state.analysis_results)
            
            if state.feedback:
                render_feedback(state.feedback)
            
            if state.recommendations:
                render_recommendations(state.recommendations)

            # Download section
            render_download_button(state)


            # Add a button to clear results
            if st.button("🔄 Review Another CV", use_container_width=True):
                reset_session_state()
        
        elif state.errors:
            render_errors(state.errors) 

from app.models import ProcessingStatus

PROGRESS = [
    ProcessingStatus.STARTED,
    ProcessingStatus.PROCESSED_FILE_COMPLETE,
    ProcessingStatus.EXTRACTION_COMPLETE,
    ProcessingStatus.ANALYSIS_COMPLETE,
    ProcessingStatus.FEEDBACK_COMPLETE,
    ProcessingStatus.RECOMMEND_COMPLETE,
]

PROGRESSING_TEXT_MAP = [
    "📄 Processing uploaded file...",
    "📖 Extracting data from CV...",
    "🔍 Analyzing CV content...",
    "💬 Generating feedback...",
    "🎯 Generating recommendations...",
    "✅ CV review completed!",
]

COMPLETED_TEXT_MAP = [
    "Processed uploaded file...",
    "Extracted data from CV...",
    "Analyzed CV content...",
    "Generated feedback...",
    "Generated recommendations...",
    "CV review completed!",
]



def get_completed_text(status: ProcessingStatus):
    return "✅ " + COMPLETED_TEXT_MAP[PROGRESS.index(status)]

def get_progressing_text(status: ProcessingStatus):
    return PROGRESSING_TEXT_MAP[PROGRESS.index(status)]

def calculate_progress(status: ProcessingStatus):
    return PROGRESS.index(status) / len(PROGRESS) * 100

def build_progress_text(status: ProcessingStatus):
    progressing_step = status
    completed_steps = PROGRESS[:PROGRESS.index(status)]

    progressing_text = get_progressing_text(progressing_step)
    completed_text = [get_completed_text(step) for step in completed_steps]

    return  completed_text + [progressing_text]


def render_processing_progress_section():
    """Render processing progress."""
    try:
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            def refresh_progress(progress: int, texts: list[str]):
                progress_bar.progress(progress / 100)
                with status_text.container():
                    for text in texts:
                        st.text(text)

            async def process_cv():
                workflow = CVReviewWorkflow(st.session_state.uploaded_file)
                async for state in workflow.run_async():

                    if state.processing_status == ProcessingStatus.FAILED:
                        refresh_progress(0, ["❌ Processing failed"])
                        st.stop()

                    if state.processing_status in PROGRESS:
                        refresh_progress(calculate_progress(state.processing_status), build_progress_text(state.processing_status))
                        # Small delay to show progress
                        await asyncio.sleep(0.5)
                
                return workflow.state

            result = asyncio.run(process_cv())
            
            time.sleep(0.5)

            progress_bar.empty()
            status_text.empty()

        set_cv_review_result(result)
        set_processing_status('completed')
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        set_processing_status('failed')
        st.stop()

def render_left_section():
    if has_file_uploaded():
        render_file_preview_section(st.session_state.uploaded_file)
    else:
        render_about_section() 

def render_right_section():
    processing_status = get_processing_status()

    if has_file_uploaded():
        if processing_status == 'pending':
            render_processing_actions_section()

        if processing_status == 'processing':
            render_processing_progress_section()

        if processing_status == 'completed':
            render_complete_results_section(st.session_state.cv_review_result)

    else:
        render_file_upload_section()
