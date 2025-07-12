from typing import Dict, Any, AsyncGenerator
import asyncio
from langgraph.graph import StateGraph, END
from app.models import CVReviewState
from app.agents.extraction_agent import ExtractionAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.utils.file_processor import process_uploaded_file


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


async def run_cv_review_async(uploaded_file) -> AsyncGenerator[CVReviewState, None]:
    """Run the CV review workflow asynchronously with real-time status updates."""

    # Create initial state
    current_state = CVReviewState(
        processing_status="started"
    )
    
    # Yield initial state
    yield current_state

    # Process uploaded file
    file_name, file_content = process_uploaded_file(uploaded_file)

    current_state.file_name = file_name
    current_state.file_content = file_content
    current_state.processing_status = "processed_file_complete"
    yield current_state

    # Initialize workflow
    workflow = create_cv_review_workflow()
    
    try:
        # Run workflow step by step
        async for step in workflow.astream(current_state):
            for node_name, state_data in step.items():
                for key, value in state_data.items():
                    setattr(current_state, key, value)
            yield current_state

                
    except Exception as e:
        # Handle workflow errors
        error_state = CVReviewState(
            file_name=file_name,
            file_content=file_content,
            processing_status="failed",
            errors=[f"Workflow execution failed: {str(e)}"]
        )
        yield error_state

