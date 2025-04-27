from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator
from smolagents import CodeAgent, OpenAIServerModel, ToolCallingAgent, ToolCollection

from .base import Capability, EvaluationMode


# Define nested models outside the main class temporarily for schema generation
class _InterviewQuestion(BaseModel):
    id: int = Field(..., description="Question ID")
    question: str = Field(..., description="Question asked by the interviewer")
    answer: str = Field(..., description="Answer provided by the candidate")

class _InterviewCapability(Capability): # Inherits from shared Capability
    confidence: float = Field(..., description="Confidence score (0-1)")

class _InterviewReportModel(BaseModel):
    candidate_overview: str = Field(..., description="Overview of the candidate's capabilities")
    declared_capabilities: List[_InterviewCapability] = Field(..., description="Capabilities the candidate claims to have")
    verified_capabilities: List[_InterviewCapability] = Field(..., description="Capabilities verified through testing")
    questions_and_answers: List[_InterviewQuestion] = Field(..., description="Interview questions and answers")
    overall_assessment: str = Field(..., description="Overall assessment of the candidate")
    capability_scores: Dict[str, float] = Field(
        ..., 
        description="Capability scores, keys are capability names, values are scores between 0 and 1"
    )
    
    @field_validator('capability_scores')
    @classmethod
    def validate_scores(cls, v: Dict[str, float]) -> Dict[str, float]:
        for key, value in v.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Score for {key} must be between 0 and 1, got {value}")
        return v

# Define the main mode class
class InterviewMode(EvaluationMode):
    """Implements the interview evaluation mode."""

    # Define nested models properly within the class scope for usage
    Question = _InterviewQuestion
    InterviewCapability = _InterviewCapability
    InterviewReportModel = _InterviewReportModel

    # Store the report model class for schema generation later
    _ReportModel = _InterviewReportModel

    INTERVIEW_PROMPT_TEMPLATE = """
    You are a technical interviewer evaluating an AI agent candidate for a role that requires specific capabilities. 
    Conduct a comprehensive interview to assess the candidate's capabilities and provide an evaluation based on their performance.

    Follow this interview process:

    1. Ask the candidate to introduce themselves and describe their capabilities
    2. Based on their introduction, ask specific questions to verify each capability they claim to have
    3. Test their capabilities with practical tasks that would demonstrate their skills
    4. Evaluate their performance on each capability

    Organize your evaluation into the following format:

    ## Candidate Overview
    [Provide an overview of the candidate based on their self-description and your assessment]

    ## Declared Capabilities
    [List capabilities the candidate claims to have, with detailed descriptions and your confidence in each claim (0-1)]

    ## Verified Capabilities
    [List capabilities you've verified through testing, with detailed descriptions and a score for each (0-1)]

    ## Questions and Answers
    [List each question you asked and the candidate's response]

    ## Overall Assessment
    [Provide your overall assessment of the candidate, including strengths, weaknesses, and suitability]

    ## Capability Scores
    [For each capability, assign a score between 0 and 1 that represents their proficiency]

    After completing all the steps above, use the final answer tool to output a complete JSON object (without the "```json" and "```" tags).

    {InterviewReportSchema} # Placeholder for schema
    """
    
    def __init__(self):
        # Generate schema after the class is defined
        InterviewMode._ReportModel.model_rebuild(force=True)
        self.InterviewReportSchema = InterviewMode._ReportModel.model_json_schema()
        self.INTERVIEW_PROMPT = self.INTERVIEW_PROMPT_TEMPLATE.format(InterviewReportSchema=self.InterviewReportSchema)

    def run(self, model: OpenAIServerModel, tool_collection: ToolCollection) -> Dict[str, Any]:
        candidate_agent = ToolCallingAgent(
            tools=[*tool_collection.tools],
            model=model,
            add_base_tools=False,
            name="CandidateAgent",
            description="An AI candidate with specific capabilities provided by the available tools. When asked about capabilities, only describe what you can do with your available tools, not your general abilities(e.g. final_answer)."
        )
        interviewer_agent = CodeAgent(
            tools=[], 
            model=model, 
            add_base_tools=True, # Interviewer can use base tools like final_answer
            managed_agents=[candidate_agent]
        )
        # Use the formatted prompt from __init__
        result = interviewer_agent.run(self.INTERVIEW_PROMPT) 
        return result 