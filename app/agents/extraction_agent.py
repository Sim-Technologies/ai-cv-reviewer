import json
from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from app.models import ExtractedCVData, CVReviewState
from app.utils.llm_config import get_chat_model


class ExtractionAgent:
    def __init__(self):
        self.llm = get_chat_model()
    
    def extract_data(self, cv_text: str) -> ExtractedCVData:
        """Extract structured data from CV text."""
        
        system_prompt = """You are an expert CV parser. Extract structured information from the CV text and return it as a JSON object.

Extract the following information:
- name: Full name of the person
- email: Email address
- phone: Phone number
- location: City, State/Country
- summary: Professional summary or objective
- experience: List of work experiences with company, position, dates, description, and achievements
- education: List of educational background with institution, degree, field, dates, and GPA
- skills: List of skills with name, level (beginner/intermediate/advanced/expert), and years of experience
- certifications: List of certifications
- languages: List of languages spoken

For experience, education, and skills, create structured objects. For dates, use format "YYYY-MM" or "YYYY" if only year is available.

Return ONLY valid JSON without any additional text or formatting."""

        user_prompt = f"Please extract structured data from this CV:\n\n{cv_text}"

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
            
            # Parse JSON and create ExtractedCVData object
            data_dict = json.loads(json_str)
            
            # Ensure raw_text is included
            data_dict['raw_text'] = cv_text
            
            return ExtractedCVData(**data_dict)
            
        except Exception as e:
            # Fallback: create basic structure with raw text
            return ExtractedCVData(
                raw_text=cv_text,
                name="Could not extract",
                experience=[],
                education=[],
                skills=[]
            )
    
    def process(self, state: CVReviewState) -> CVReviewState:
        """Process the CV review state and extract data."""
        try:
            if not state.file_content:
                state.errors.append("No file content to extract")
                return state
            
            state.processing_status = "extracting"
            
            # Extract structured data
            extracted_data = self.extract_data(state.file_content)
            state.extracted_data = extracted_data
            
            state.processing_status = "extraction_complete"
            return state
            
        except Exception as e:
            state.errors.append(f"Extraction failed: {str(e)}")
            state.processing_status = "extraction_failed"
            return state 