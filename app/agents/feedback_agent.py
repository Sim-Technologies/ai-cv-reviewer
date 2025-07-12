import json
from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from app.models import ExtractedCVData, AnalysisResult, Feedback, CVReviewState
from app.utils.llm_config import get_chat_model


class FeedbackAgent:
    def __init__(self):
        self.llm = get_chat_model()
    
    def generate_feedback(self, extracted_data: ExtractedCVData, analysis_results: AnalysisResult) -> Feedback:
        """Generate constructive feedback based on CV data and analysis."""
        
        system_prompt = """You are an expert career coach and CV reviewer. Generate constructive, actionable feedback based on the CV data and analysis.

Provide feedback in the following areas:
1. General feedback: Overall impression and key observations
2. Experience feedback: Work experience quality, progression, and presentation
3. Skills feedback: Skills relevance, market alignment, and development areas
4. Education feedback: Educational background impact and relevance
5. Presentation feedback: CV structure, formatting, and clarity
6. Specific improvements: 5-7 actionable suggestions
7. Positive aspects: 3-5 strengths to highlight

Guidelines:
- Be constructive and encouraging
- Provide specific, actionable advice
- Balance criticism with positive reinforcement
- Focus on improvement opportunities
- Consider market trends and best practices

Return ONLY valid JSON without any additional text or formatting."""

        # Prepare data for feedback generation
        data_json = extracted_data.model_dump_json()
        analysis_json = analysis_results.model_dump_json()
        
        user_prompt = f"""Please generate comprehensive feedback for this CV:

CV Data:
{data_json}

Analysis Results:
{analysis_json}"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Clean the response to extract JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content.strip()
            
            # Parse JSON and create Feedback object
            feedback_dict = json.loads(json_str)
            
            return Feedback(**feedback_dict)
            
        except Exception as e:
            # Fallback: create basic feedback
            return Feedback(
                general_feedback="Feedback generation could not be completed due to technical issues.",
                experience_feedback="Unable to provide specific experience feedback.",
                skills_feedback="Unable to provide specific skills feedback.",
                education_feedback="Unable to provide specific education feedback.",
                presentation_feedback="Unable to provide specific presentation feedback.",
                specific_improvements=["Please review the CV manually for improvements"],
                positive_aspects=["CV contains valuable information"]
            )
    
    def process(self, state: CVReviewState) -> CVReviewState:
        """Process the CV review state and generate feedback."""
        try:
            if not state.extracted_data or not state.analysis_results:
                state.errors.append("Missing extracted data or analysis results for feedback")
                return state
            
            state.processing_status = "generating_feedback"
            
            # Generate feedback
            feedback = self.generate_feedback(state.extracted_data, state.analysis_results)
            state.feedback = feedback
            
            state.processing_status = "feedback_complete"
            return state
            
        except Exception as e:
            state.errors.append(f"Feedback generation failed: {str(e)}")
            state.processing_status = "feedback_failed"
            return state 