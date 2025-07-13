from typing import Dict, Any, AsyncGenerator

from langgraph.graph import StateGraph, END
from app.models import CVReviewState, ProcessingStatus
from app.agents.extraction_agent import ExtractionAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.utils.file_processor import process_uploaded_file

class CVReviewWorkflow:
    """CV Review workflow using LangGraph for orchestration."""
    
    def __init__(self, cv_file):
        """Initialize the workflow with agents."""
        self.cv_file = cv_file
        self.state = CVReviewState(
            processing_status=ProcessingStatus.STARTED
        )
        self.extraction_agent = ExtractionAgent()
        self.analysis_agent = AnalysisAgent()
        self.feedback_agent = FeedbackAgent()
        self.recommendation_agent = RecommendationAgent()
        self._workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the CV review workflow using LangGraph."""
        
        # Create workflow
        workflow = StateGraph(CVReviewState)
        
        # Add nodes
        workflow.add_node("extract", self.extraction_agent.process)
        workflow.add_node("analyze", self.analysis_agent.process)
        workflow.add_node("feedback", self.feedback_agent.process)
        workflow.add_node("recommend", self.recommendation_agent.process)
        
        # Set entry point
        workflow.set_entry_point("extract")
        
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
    
    def _set_state_from_step(self, step: dict) -> None:
        """Set the state from a step."""
        for node_name, state_data in step.items():
            for key, value in state_data.items():
                setattr(self.state, key, value)

    
    async def _run_workflow(self) -> AsyncGenerator[CVReviewState, None]:
        """Run the CV review workflow."""
        try:
            async for step in self._workflow.astream(self.state):
                self._set_state_from_step(step)
                yield self.state
        except Exception as e:
            print("Error", e)
            error_state = CVReviewState(
                file_name=self.state.file_name,
                file_content=self.state.file_content,
                processing_status=ProcessingStatus.FAILED,
                errors=[f"Workflow execution failed: {str(e)}"]
            )
            yield error_state


    def _process_file(self) -> None:
        """Process the file."""
        file_name, file_content = process_uploaded_file(self.cv_file)
        self.state.file_name = file_name
        self.state.file_content = file_content
        self.state.processing_status = ProcessingStatus.PROCESSED_FILE_COMPLETE
    
    async def run_async(self) -> AsyncGenerator[CVReviewState, None]:
        """Run the CV review workflow asynchronously with real-time status updates."""
        yield self.state

        self._process_file()
        yield self.state
       
        async for state in self._run_workflow():
            yield state

        self.state.processing_status = ProcessingStatus.COMPLETED
        yield self.state


