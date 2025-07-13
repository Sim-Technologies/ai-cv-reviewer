from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Experience(BaseModel):
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = None


class Skill(BaseModel):
    name: str
    level: Optional[SkillLevel] = None
    years_experience: Optional[int] = None


class ExtractedCVData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    raw_text: str = Field(description="Raw extracted text from CV")


class AnalysisResult(BaseModel):
    overall_score: float = Field(ge=0, le=100, description="Overall CV score out of 100")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    experience_analysis: Dict[str, Any] = Field(default_factory=dict)
    skills_analysis: Dict[str, Any] = Field(default_factory=dict)
    education_analysis: Dict[str, Any] = Field(default_factory=dict)
    market_alignment: Dict[str, Any] = Field(default_factory=dict)
    years_experience: Optional[int] = None
    seniority_level: Optional[str] = None


class Feedback(BaseModel):
    general_feedback: str
    experience_feedback: str
    skills_feedback: str
    education_feedback: str
    presentation_feedback: str
    specific_improvements: List[str] = Field(default_factory=list)
    positive_aspects: List[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    skill_development: List[str] = Field(default_factory=list)
    experience_gaps: List[str] = Field(default_factory=list)
    career_path_suggestions: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)
    long_term_goals: List[str] = Field(default_factory=list)
    industry_trends: List[str] = Field(default_factory=list)


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    PROCESSED_FILE_COMPLETE = "processed_file_complete"

    EXTRACTING = "extracting"
    EXTRACTION_COMPLETE = "extraction_complete"
    
    ANALYZING = "analyzing"
    ANALYSIS_COMPLETE = "analysis_complete"
    
    GENERATING_FEEDBACK = "generating_feedback"
    FEEDBACK_COMPLETE = "feedback_complete"
    
    GENERATING_RECOMMENDATIONS = "generating_recommendations"
    RECOMMEND_COMPLETE = "recommend_complete"
    
    COMPLETED = "completed"
    FAILED = "failed"

class CVReviewState(BaseModel):
    file_name: Optional[str] = None
    file_content: Optional[str] = None
    extracted_data: Optional[ExtractedCVData] = None
    analysis_results: Optional[AnalysisResult] = None
    feedback: Optional[Feedback] = None
    recommendations: Optional[Recommendation] = None
    errors: List[str] = Field(default_factory=list)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING