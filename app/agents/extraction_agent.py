from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.models import ExtractedCVData, CVReviewState, ProcessingStatus
from app.utils.llm_config import get_chat_model


EXTRACTION_PROMPT = PromptTemplate(
    template="""You are an expert CV parser. Extract structured information from the CV text and return it as a JSON object.

Extract the following information:
- name: Full name of the person
- email: Email address  
- phone: Phone number
- location: City, State/Country
- summary: Professional summary or objective
- experience: List of work experiences with company, position, start_date, end_date, description, and achievements
- education: List of educational background with institution, degree, field_of_study, start_date, end_date, and gpa
- skills: List of skills with name, level (beginner/intermediate/advanced/expert), and years_experience
- certifications: List of certifications
- languages: List of languages spoken

For dates, use format "YYYY-MM" or "YYYY" if only year is available.
For skill levels, use: beginner, intermediate, advanced, or expert.

CV Text:
{cv_text}

{format_instructions}""",
    input_variables=["cv_text"],
    partial_variables={"format_instructions": "{format_instructions}"}
)


class ExtractionAgent:
    def __init__(self):
        self.llm = get_chat_model()
        self.parser = JsonOutputParser(pydantic_object=ExtractedCVData)
        self.prompt = EXTRACTION_PROMPT.partial(format_instructions=self.parser.get_format_instructions())
        self.chain = self.prompt | self.llm | self.parser
    
    def extract_data(self, cv_text: str) -> ExtractedCVData:
        """Extract structured data from CV text using JsonOutputParser."""
        
        try:
            result = self.chain.invoke({"cv_text": cv_text})
            result.raw_text = cv_text

            return result
            
        except Exception as e:
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

            # Extract structured data
            extracted_data = self.extract_data(state.file_content)
            state.extracted_data = extracted_data
            return state
            
        except Exception as e:
            state.errors.append(f"Extraction failed: {str(e)}")
            state.processing_status = "extraction_failed"
            return state 