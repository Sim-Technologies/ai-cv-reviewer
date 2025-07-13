from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.models import ExtractedCVData, AnalysisResult, Feedback, Recommendation, CVReviewState, ProcessingStatus
from app.utils.llm_config import get_chat_model


RECOMMENDATION_PROMPT = PromptTemplate(
    template="""You are an expert career development consultant and professional coach. Generate comprehensive recommendations for CV improvement and career development.

Provide recommendations in the following areas:
1. Skill development: Specific skills to acquire or improve
2. Experience gaps: Areas where experience could be enhanced
3. Career path suggestions: Potential career trajectories and opportunities
4. Immediate actions: Quick wins and short-term improvements
5. Long-term goals: Strategic career development objectives
6. Industry trends: Relevant industry insights and emerging opportunities

Guidelines:
- Be specific and actionable
- Consider current market trends
- Provide realistic timelines
- Focus on high-impact improvements
- Consider the individual's background and goals
- Include both technical and soft skills
- Suggest relevant certifications or training

CV Data:
{cv_data}

Analysis Results:
{analysis_data}

Feedback:
{feedback_data}

{format_instructions}""",
    input_variables=["cv_data", "analysis_data", "feedback_data"],
    partial_variables={"format_instructions": "{format_instructions}"}
)


class RecommendationAgent:
    def __init__(self):
        self.llm = get_chat_model()
        self.parser = JsonOutputParser(pydantic_object=Recommendation)
        self.prompt = RECOMMENDATION_PROMPT.partial(format_instructions=self.parser.get_format_instructions())
        self.chain = self.prompt | self.llm | self.parser
    
    def generate_recommendations(self, extracted_data: ExtractedCVData, analysis_results: AnalysisResult, feedback: Feedback) -> Recommendation:
        """Generate improvement recommendations and career guidance using JsonOutputParser."""
        
        try:
            data_json = extracted_data.model_dump_json()
            analysis_json = analysis_results.model_dump_json()
            feedback_json = feedback.model_dump_json()
            result = self.chain.invoke({
                "cv_data": data_json,
                "analysis_data": analysis_json,
                "feedback_data": feedback_json
            })
            
            return result
            
        except Exception as e:
            return Recommendation(
                skill_development=["Focus on developing relevant technical and soft skills"],
                experience_gaps=["Consider gaining more experience in key areas"],
                career_path_suggestions=["Explore opportunities for career advancement"],
                immediate_actions=["Review and update CV regularly"],
                long_term_goals=["Set clear career objectives and milestones"],
                industry_trends=["Stay updated with industry developments"]
            )
    
    def process(self, state: CVReviewState) -> CVReviewState:
        """Process the CV review state and generate recommendations."""
        try:
            if not state.extracted_data or not state.analysis_results or not state.feedback:
                state.errors.append("Missing required data for recommendations")
                return state
            
            state.processing_status = ProcessingStatus.GENERATING_RECOMMENDATIONS
            recommendations = self.generate_recommendations(
                state.extracted_data, 
                state.analysis_results, 
                state.feedback
            )
            state.recommendations = recommendations
            
            state.processing_status = ProcessingStatus.RECOMMEND_COMPLETE
            return state
            
        except Exception as e:
            state.errors.append(f"Recommendation generation failed: {str(e)}")
            state.processing_status = "recommendations_failed"
            return state 