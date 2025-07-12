import json
from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from app.models import ExtractedCVData, AnalysisResult, Feedback, Recommendation, CVReviewState
from app.utils.llm_config import get_chat_model


class RecommendationAgent:
    def __init__(self):
        self.llm = get_chat_model()
    
    def generate_recommendations(self, extracted_data: ExtractedCVData, analysis_results: AnalysisResult, feedback: Feedback) -> Recommendation:
        """Generate improvement recommendations and career guidance."""
        
        system_prompt = """You are an expert career development consultant and professional coach. Generate comprehensive recommendations for CV improvement and career development.

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

Return ONLY valid JSON without any additional text or formatting."""

        # Prepare data for recommendation generation
        data_json = extracted_data.model_dump_json()
        analysis_json = analysis_results.model_dump_json()
        feedback_json = feedback.model_dump_json()
        
        user_prompt = f"""Please generate comprehensive recommendations for this professional:

CV Data:
{data_json}

Analysis Results:
{analysis_json}

Feedback:
{feedback_json}"""

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
            
            # Parse JSON and create Recommendation object
            recommendation_dict = json.loads(json_str)
            
            return Recommendation(**recommendation_dict)
            
        except Exception as e:
            # Fallback: create basic recommendations
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
            
            state.processing_status = "generating_recommendations"
            
            # Generate recommendations
            recommendations = self.generate_recommendations(
                state.extracted_data, 
                state.analysis_results, 
                state.feedback
            )
            state.recommendations = recommendations
            
            state.processing_status = "complete"
            return state
            
        except Exception as e:
            state.errors.append(f"Recommendation generation failed: {str(e)}")
            state.processing_status = "recommendations_failed"
            return state 