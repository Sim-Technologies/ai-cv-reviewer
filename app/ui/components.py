import streamlit as st
import json
from typing import Optional
from app.models import CVReviewState, ExtractedCVData, AnalysisResult, Feedback, Recommendation
from streamlit_pdf_viewer import pdf_viewer
from app.graph.workflow import CVReviewWorkflow
import asyncio
import time


def dict_to_markdown(data: dict, indent: int = 0) -> str:
    """Convert dictionary to markdown key-value format."""
    if not data:
        return "No data available"
    
    markdown_lines = []
    indent_str = "  " * indent
    
    for key, value in data.items():
        # Format the key
        formatted_key = key.replace('_', ' ').title()
        
        if isinstance(value, dict):
            # Nested dictionary
            markdown_lines.append(f"{indent_str}**{formatted_key}:**")
            markdown_lines.append(dict_to_markdown(value, indent + 1))
        elif isinstance(value, list):
            # List
            markdown_lines.append(f"{indent_str}**{formatted_key}:**")
            for item in value:
                if isinstance(item, dict):
                    markdown_lines.append(dict_to_markdown(item, indent + 1))
                else:
                    markdown_lines.append(f"{indent_str}  • {item}")
        else:
            # Simple value
            markdown_lines.append(f"{indent_str}**{formatted_key}:** {value}")
    
    return "\n".join(markdown_lines)


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

def render_processing_actions():
    """Render the processing actions."""
    st.subheader("🚀 Ready to Review")
    st.write("Your CV has been uploaded successfully. Click the button below to start the AI review process.")
    
    if st.button("🚀 Start CV Review", type="primary", use_container_width=True):
        st.session_state.processing_status = 'processing'
        st.rerun()
    
    # Option to upload different file
    if st.button("📄 Upload Different File", use_container_width=True):
        # Clear uploaded state
        st.session_state.file_uploaded = False
        if 'uploaded_file' in st.session_state:
            del st.session_state.uploaded_file
        st.rerun()

def render_file_upload():
    """Render the file upload section."""
    st.subheader("📄 Upload Your CV")
    
    uploaded_file = st.file_uploader(
        "Choose a CV file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT (max 10MB)"
    )

    if uploaded_file is not None:
        # Set uploaded state
        st.session_state.file_uploaded = True
        st.session_state.uploaded_file = uploaded_file
        st.rerun()
    


def render_file_preview(uploaded_file):
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



def render_processing_status(status: str):
    """Render processing status with progress indicators."""
    if status == "started":
        st.info("🚀 Starting CV review process...")
    elif status == "extracting":
        st.info("📖 Extracting data from CV...")
    elif status == "extraction_complete":
        st.success("✅ Data extraction completed")
    elif status == "analyzing":
        st.info("🔍 Analyzing CV content...")
    elif status == "analysis_complete":
        st.success("✅ Analysis completed")
    elif status == "generating_feedback":
        st.info("💬 Generating feedback...")
    elif status == "feedback_complete":
        st.success("✅ Feedback generated")
    elif status == "generating_recommendations":
        st.info("🎯 Generating recommendations...")
    elif status == "complete":
        st.success("🎉 CV review completed!")
    elif "failed" in status:
        st.error(f"❌ Process failed: {status}")


def render_extracted_data(data: ExtractedCVData):
    """Render extracted CV data."""
    st.subheader("📋 Extracted Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if data.name:
            st.write(f"**Name:** {data.name}")
        if data.email:
            st.write(f"**Email:** {data.email}")
        if data.phone:
            st.write(f"**Phone:** {data.phone}")
        if data.location:
            st.write(f"**Location:** {data.location}")
    
    with col2:
        if data.summary:
            st.write("**Summary:**")
            st.write(data.summary)
    
    # Experience
    if data.experience:
        st.write("**Work Experience:**")
        for i, exp in enumerate(data.experience, 1):
            with st.expander(f"{i}. {exp.position} at {exp.company}"):
                if exp.start_date or exp.end_date:
                    st.write(f"**Period:** {exp.start_date or 'N/A'} - {exp.end_date or 'Present'}")
                if exp.description:
                    st.write(f"**Description:** {exp.description}")
                if exp.achievements:
                    st.write("**Achievements:**")
                    for achievement in exp.achievements:
                        st.write(f"• {achievement}")
    
    # Education
    if data.education:
        st.write("**Education:**")
        for edu in data.education:
            with st.expander(f"{edu.degree} from {edu.institution}"):
                if edu.field_of_study:
                    st.write(f"**Field:** {edu.field_of_study}")
                if edu.start_date or edu.end_date:
                    st.write(f"**Period:** {edu.start_date or 'N/A'} - {edu.end_date or 'N/A'}")
                if edu.gpa:
                    st.write(f"**GPA:** {edu.gpa}")
    
    # Skills
    if data.skills:
        st.write("**Skills:**")
        skill_cols = st.columns(3)
        for i, skill in enumerate(data.skills):
            col_idx = i % 3
            with skill_cols[col_idx]:
                level_text = f" ({skill.level})" if skill.level else ""
                years_text = f" - {skill.years_experience} years" if skill.years_experience else ""
                st.write(f"• {skill.name}{level_text}{years_text}")


def render_analysis_results(analysis: AnalysisResult):
    """Render analysis results."""
    st.subheader("📊 Analysis Results")
    
    # Overall score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{analysis.overall_score:.1f}/100")
    with col2:
        if analysis.years_experience:
            st.metric("Years Experience", analysis.years_experience)
    with col3:
        if analysis.seniority_level:
            st.metric("Seniority Level", analysis.seniority_level)
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**💪 Strengths:**")
        for strength in analysis.strengths:
            st.write(f"• {strength}")
    
    with col2:
        st.write("**⚠️ Areas for Improvement:**")
        for weakness in analysis.weaknesses:
            st.write(f"• {weakness}")
    
    # Detailed analysis
    if analysis.experience_analysis:
        with st.expander("📈 Experience Analysis"):
            st.markdown(dict_to_markdown(analysis.experience_analysis))
    
    if analysis.skills_analysis:
        with st.expander("🛠️ Skills Analysis"):
            st.markdown(dict_to_markdown(analysis.skills_analysis))
    
    if analysis.education_analysis:
        with st.expander("🎓 Education Analysis"):
            st.markdown(dict_to_markdown(analysis.education_analysis))
    
    if analysis.market_alignment:
        with st.expander("🌐 Market Alignment"):
            st.markdown(dict_to_markdown(analysis.market_alignment))


def render_feedback(feedback: Feedback):
    """Render feedback section."""
    st.subheader("💬 Feedback")
    
    # General feedback
    st.write("**Overall Feedback:**")
    st.write(feedback.general_feedback)
    
    # Specific feedback areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**💼 Experience Feedback:**")
        st.write(feedback.experience_feedback)
        
        st.write("**🎓 Education Feedback:**")
        st.write(feedback.education_feedback)
    
    with col2:
        st.write("**🛠️ Skills Feedback:**")
        st.write(feedback.skills_feedback)
        
        st.write("**📝 Presentation Feedback:**")
        st.write(feedback.presentation_feedback)
    
    # Improvements and positive aspects
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔧 Specific Improvements:**")
        for improvement in feedback.specific_improvements:
            st.write(f"• {improvement}")
    
    with col2:
        st.write("**✅ Positive Aspects:**")
        for aspect in feedback.positive_aspects:
            st.write(f"• {aspect}")


def render_recommendations(recommendations: Recommendation):
    """Render recommendations section."""
    st.subheader("🎯 Recommendations")
    
    # Skill development
    st.write("**🛠️ Skill Development:**")
    for skill in recommendations.skill_development:
        st.write(f"• {skill}")
    
    # Experience gaps
    if recommendations.experience_gaps:
        st.write("**📈 Experience Gaps:**")
        for gap in recommendations.experience_gaps:
            st.write(f"• {gap}")
    
    # Career path suggestions
    if recommendations.career_path_suggestions:
        st.write("**🚀 Career Path Suggestions:**")
        for suggestion in recommendations.career_path_suggestions:
            st.write(f"• {suggestion}")
    
    # Immediate actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**⚡ Immediate Actions:**")
        for action in recommendations.immediate_actions:
            st.write(f"• {action}")
    
    with col2:
        st.write("**🎯 Long-term Goals:**")
        for goal in recommendations.long_term_goals:
            st.write(f"• {goal}")
    
    # Industry trends
    if recommendations.industry_trends:
        st.write("**📊 Industry Trends:**")
        for trend in recommendations.industry_trends:
            st.write(f"• {trend}")


def render_errors(errors: list):
    """Render error messages."""
    if errors:
        st.error("❌ Errors occurred during processing:")
        for error in errors:
            st.write(f"• {error}")


def render_download_section(state: CVReviewState):
    """Render download section for results."""
    if state.processing_status == "complete":
        st.subheader("💾 Download Results")
        
        # Prepare data for download
        results_data = {
            "file_name": state.file_name,
            "extracted_data": state.extracted_data.model_dump() if state.extracted_data else None,
            "analysis_results": state.analysis_results.model_dump() if state.analysis_results else None,
            "feedback": state.feedback.model_dump() if state.feedback else None,
            "recommendations": state.recommendations.model_dump() if state.recommendations else None,
            "errors": state.errors
        }
        
        # Create JSON download
        json_str = json.dumps(results_data, indent=2, default=str)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json_str,
            file_name=f"cv_review_{state.file_name}.json",
            mime="application/json"
        )


def render_complete_results(state: CVReviewState):
    with st.container(height=600):
        # Show processing status
        render_processing_status(state.processing_status)
        
        """Render complete results section."""
        if state.processing_status == "complete":
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
            render_download_section(state)


            # Add a button to clear results
            if st.button("🔄 Review Another CV", use_container_width=True):
                if 'cv_review_result' in st.session_state:
                    del st.session_state.cv_review_result
                st.rerun()
        
        elif state.errors:
            render_errors(state.errors) 

def render_processing_progress():
    """Render processing progress."""
    try:
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
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
                workflow = CVReviewWorkflow(st.session_state.uploaded_file)

                async for state in workflow.run_async():
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
                
                return workflow.state
            
            # Run the async function
            result = asyncio.run(process_cv())
            
            # Small delay to show completion
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
        
        # Store result in session state
        st.session_state.cv_review_result = result
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        # Clear processing flag on error
        st.session_state.processing_status = 'failed'
        st.stop()

def render_left_section():
    if st.session_state.file_uploaded:
        render_file_preview(st.session_state.uploaded_file)
    else:
        render_about_section() 

def render_right_section():
    processing_status = st.session_state.processing_status

    # File upload section - only show if no file uploaded yet
    if not st.session_state.file_uploaded:
        render_file_upload()
    else:
        if processing_status == 'pending':
            render_processing_actions()

        if processing_status == 'processing':
            render_processing_progress()

        if processing_status == 'completed':
            render_complete_results(st.session_state.cv_review_result)
