import json
from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from app.models import ExtractedCVData, AnalysisResult, CVReviewState
from app.utils.llm_config import get_chat_model


class AnalysisAgent:
    def __init__(self):
        self.llm = get_chat_model()
    
    def analyze_data(self, extracted_data: ExtractedCVData) -> AnalysisResult:
        """Analyze extracted CV data and provide insights."""
        
        system_prompt = """You are an expert CV analyst and career consultant. Analyze the CV data and provide comprehensive insights.

Analyze the following aspects:
1. Overall CV strength and market competitiveness
2. Experience quality and progression
3. Skills alignment with market demands
4. Education relevance and impact
5. Identified strengths and weaknesses
6. Market alignment and career trajectory

Provide a detailed analysis with:
- Overall score (0-100)
- Key strengths (3-5 points)
- Areas for improvement (3-5 points)
- Experience analysis (depth, progression, achievements)
- Skills analysis (relevance, market demand, gaps)
- Education analysis (relevance, impact)
- Market alignment assessment
- Estimated years of experience
- Suggested seniority level

Return ONLY valid JSON without any additional text or formatting."""

        # Convert extracted data to JSON for analysis
        data_json = extracted_data.model_dump_json()
        
        user_prompt = f"Please analyze this CV data:\n\n{data_json}"

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
            
            # Parse JSON and create AnalysisResult object
            analysis_dict = json.loads(json_str)
            
            return AnalysisResult(**analysis_dict)
            
        except Exception as e:
            # Fallback: create basic analysis
            return AnalysisResult(
                overall_score=50.0,
                strengths=["Analysis could not be completed"],
                weaknesses=["Analysis could not be completed"],
                experience_analysis={},
                skills_analysis={},
                education_analysis={},
                market_alignment={}
            )
    
    def process(self, state: CVReviewState) -> CVReviewState:
        """Process the CV review state and analyze data."""
        try:
            if not state.extracted_data:
                state.errors.append("No extracted data to analyze")
                return state
            
            state.processing_status = "analyzing"
            
            # Analyze extracted data
            analysis_results = self.analyze_data(state.extracted_data)
            state.analysis_results = analysis_results
            
            state.processing_status = "analysis_complete"
            return state
            
        except Exception as e:
            state.errors.append(f"Analysis failed: {str(e)}")
            state.processing_status = "analysis_failed"
            return state 