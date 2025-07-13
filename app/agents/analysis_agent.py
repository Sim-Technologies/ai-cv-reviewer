import json
from typing import Dict, Any
from langchain.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.models import ExtractedCVData, AnalysisResult, CVReviewState
from app.utils.llm_config import get_chat_model


# Define the analysis prompt template
ANALYSIS_PROMPT = PromptTemplate(
    template="""You are an expert CV analyst and career consultant. Analyze the CV data and provide comprehensive insights.

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

CV Data:
{cv_data}

{format_instructions}""",
    input_variables=["cv_data"],
    partial_variables={"format_instructions": "{format_instructions}"}
)


class AnalysisAgent:
    def __init__(self):
        self.llm = get_chat_model()
        self.parser = JsonOutputParser(pydantic_object=AnalysisResult)
        
        # Create prompt with format instructions
        self.prompt = ANALYSIS_PROMPT.partial(format_instructions=self.parser.get_format_instructions())
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze_data(self, extracted_data: ExtractedCVData) -> AnalysisResult:
        """Analyze extracted CV data and provide insights using JsonOutputParser."""
        
        try:
            # Convert extracted data to JSON for analysis
            data_json = extracted_data.model_dump_json()
            
            # Run the chain
            result = self.chain.invoke({"cv_data": data_json})
            
            return result
            
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