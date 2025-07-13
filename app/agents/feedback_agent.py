from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.models import ExtractedCVData, AnalysisResult, Feedback, CVReviewState, ProcessingStatus
from app.utils.llm_config import get_chat_model


FEEDBACK_PROMPT = PromptTemplate(
    template="""You are an expert career coach and CV reviewer. Generate constructive, actionable feedback based on the CV data and analysis.

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

CV Data:
{cv_data}

Analysis Results:
{analysis_data}

{format_instructions}""",
    input_variables=["cv_data", "analysis_data"],
    partial_variables={"format_instructions": "{format_instructions}"}
)


class FeedbackAgent:
    def __init__(self):
        self.llm = get_chat_model()
        self.parser = JsonOutputParser(pydantic_object=Feedback)
        self.prompt = FEEDBACK_PROMPT.partial(format_instructions=self.parser.get_format_instructions())
        self.chain = self.prompt | self.llm | self.parser
    
    def generate_feedback(self, extracted_data: ExtractedCVData, analysis_results: AnalysisResult) -> Feedback:
        """Generate constructive feedback based on CV data and analysis using JsonOutputParser."""
        
        try:
            data_json = extracted_data.model_dump_json()
            analysis_json = analysis_results.model_dump_json()
            result = self.chain.invoke({
                "cv_data": data_json,
                "analysis_data": analysis_json
            })
            
            return result
            
        except Exception as e:
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
            
            state.processing_status = ProcessingStatus.GENERATING_FEEDBACK
            feedback = self.generate_feedback(state.extracted_data, state.analysis_results)
            state.feedback = feedback
            state.processing_status = ProcessingStatus.FEEDBACK_COMPLETE
            return state
            
        except Exception as e:
            state.errors.append(f"Feedback generation failed: {str(e)}")
            state.processing_status = "feedback_failed"
            return state 