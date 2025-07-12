from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.models import CVReviewState
from app.agents.extraction_agent import ExtractionAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.recommendation_agent import RecommendationAgent


def create_cv_review_workflow():
    """Create the CV review workflow using LangGraph."""
    
    # Initialize agents
    extraction_agent = ExtractionAgent()
    analysis_agent = AnalysisAgent()
    feedback_agent = FeedbackAgent()
    recommendation_agent = RecommendationAgent()
    
    # Create workflow
    workflow = StateGraph(CVReviewState)
    
    # Add nodes
    workflow.add_node("extract", extraction_agent.process)
    workflow.add_node("analyze", analysis_agent.process)
    workflow.add_node("feedback", feedback_agent.process)
    workflow.add_node("recommend", recommendation_agent.process)
    
    # Set entry point
    workflow.set_entry_point("extract")
    
    # Add edges
    workflow.add_edge("extract", "analyze")
    workflow.add_edge("analyze", "feedback")
    workflow.add_edge("feedback", "recommend")
    workflow.add_edge("recommend", END)
    
    # Add conditional edges for error handling
    def should_continue(state: CVReviewState) -> str:
        """Determine if workflow should continue or end due to errors."""
        if state.errors:
            return END
        return "analyze"
    
    def should_continue_after_analysis(state: CVReviewState) -> str:
        """Determine if workflow should continue after analysis."""
        if state.errors:
            return END
        return "feedback"
    
    def should_continue_after_feedback(state: CVReviewState) -> str:
        """Determine if workflow should continue after feedback."""
        if state.errors:
            return END
        return "recommend"
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "extract",
        should_continue,
        {
            "analyze": "analyze",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "analyze",
        should_continue_after_analysis,
        {
            "feedback": "feedback",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "feedback",
        should_continue_after_feedback,
        {
            "recommend": "recommend",
            END: END
        }
    )
    
    return workflow.compile()


def run_cv_review(file_name: str, file_content: str) -> CVReviewState:
    """Run the complete CV review workflow."""
    
    # Initialize workflow
    workflow = create_cv_review_workflow()
    
    # Create initial state
    initial_state = CVReviewState(
        file_name=file_name,
        file_content=file_content,
        processing_status="started"
    )
    
    # Run workflow
    try:
        result_dict = workflow.invoke(initial_state)
        return CVReviewState(**result_dict)
    except Exception as e:
        # Handle workflow errors
        error_state = CVReviewState(
            file_name=file_name,
            file_content=file_content,
            processing_status="failed",
            errors=[f"Workflow execution failed: {str(e)}"]
        )
        return error_state 