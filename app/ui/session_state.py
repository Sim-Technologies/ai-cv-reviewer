import streamlit as st
from typing import Literal
from app.models import CVReviewState

def initialize_session_state():
    st.session_state.processing_status = 'pending'
    st.session_state.uploaded_file = None
    st.session_state.cv_review_result = None
    st.session_state.progress = 0

def reset_session_state():
    initialize_session_state()
    st.rerun()

def set_cv_review_result(cv_review_result: CVReviewState):
    st.session_state.cv_review_result = cv_review_result
    st.rerun()

def set_progress(progress: int, status_text: str):
    st.session_state.progress = progress
    st.session_state.status_text = status_text
    st.rerun()

def get_current_progress() -> tuple[int, str]:
    return st.session_state.progress, st.session_state.status_text

def set_processing_status(processing_status: Literal['pending', 'processing', 'completed', 'failed']):
    st.session_state.processing_status = processing_status
    st.rerun()

def set_uploaded_file(uploaded_file):
    st.session_state.uploaded_file = uploaded_file
    st.rerun()

def clear_uploaded_file():
    st.session_state.uploaded_file = None
    st.rerun()

def has_file_uploaded() -> bool:
    return bool(st.session_state.uploaded_file)
