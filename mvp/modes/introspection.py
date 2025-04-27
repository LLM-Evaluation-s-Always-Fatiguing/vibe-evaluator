from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, field_validator
from smolagents import CodeAgent, OpenAIServerModel, ToolCollection

from .base import Capability, EvaluationMode


# Define nested models outside the main class temporarily for schema generation
class _IntrospectionEvaluationMetric(BaseModel):
    name: str = Field(..., description="Evaluation metric name")
    description: str = Field(..., description="Detailed evaluation metric description")

class _IntrospectionEvaluationTask(BaseModel):
    id: int = Field(..., description="Task ID")
    description: str = Field(..., description="Task description")
    execution_result: Union[str, Dict[str, Any]] = Field(..., description="Execution result")
    execution_time: float = Field(..., description="Execution time (seconds)")

class _CapabilityReportModel(BaseModel):
    capability_overview: str = Field(..., description="Capability overview")
    capability_list: List[Capability] = Field(..., description="Capability list")
    evaluation_metrics: List[_IntrospectionEvaluationMetric] = Field(..., description="Evaluation metrics list")
    evaluation_tasks: List[_IntrospectionEvaluationTask] = Field(..., description="Evaluation tasks list")
    final_metric_scores: Dict[str, float] = Field(
        ..., 
        description="Final metric scores, keys are metric names, values are corresponding scores (0-1)"
    )
    
    @field_validator('final_metric_scores')
    @classmethod
    def validate_scores(cls, v: Dict[str, float]) -> Dict[str, float]:
        for key, value in v.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Score for {key} must be between 0 and 1, got {value}")
        return v

# Define the main mode class
class IntrospectionMode(EvaluationMode):
    """Implements the self-evaluation (introspection) mode."""
    
    # Define nested models properly within the class scope for usage
    EvaluationMetric = _IntrospectionEvaluationMetric
    EvaluationTask = _IntrospectionEvaluationTask
    CapabilityReportModel = _CapabilityReportModel

    # Store the report model class for schema generation later
    _ReportModel = _CapabilityReportModel 

    INTROSPECT_PROMPT_TEMPLATE = """
    Please create a detailed list describing the capabilities of your tools (excluding the final answer tool).
    Then, identify 6 evaluation metrics for yourself and define each one. These metrics should reflect how well you can perform the capabilities you've declared.

    Next, design a set of tasks (specific, executable, with the number flexibly chosen based on the number of tools) that comprehensively cover these capabilities. These tasks should test the capabilities you've just listed and, through their execution results, allow you to derive quantified values for your evaluation metrics.

    Organize these elements into a document with the following format:

    ## Capability Overview
    [Provide an overview of the capabilities of your tools.]

    ## Capability List
    [List in detail the capabilities of your tools, excluding the final_answer tool.]

    ## Evaluation Metrics
    [Define 6 evaluation metrics and provide a definition for each. These metrics should be closely related to the user's focus areas. Each metric should be normalized to between 0 and 1.]

    ## Evaluation Task
    [Design a set of tasks that comprehensively cover your capabilities. The number can be flexible based on the number of tools and user focus areas. These tasks should test the capabilities you've declared and, through their execution results, allow you to derive quantified values for the above metrics. You need to design specific inputs and outputs according to the tool requirements, execute these tasks one by one, and record the execution results of each task.]

    ## Final Metric Scores
    [Based on the execution results of the above tasks, provide quantified values for each evaluation metric.]

    After completing all the steps above, use the final answer tool to output a complete JSON object (without the "```json" and "```" tags).

    {CapabilityReportSchema} # Placeholder for schema
    """

    def __init__(self):
        # Generate schema after the class is defined
        IntrospectionMode._ReportModel.model_rebuild(force=True)
        self.CapabilityReportSchema = IntrospectionMode._ReportModel.model_json_schema()
        self.INTROSPECT_PROMPT = self.INTROSPECT_PROMPT_TEMPLATE.format(CapabilityReportSchema=self.CapabilityReportSchema)

    def run(self, model: OpenAIServerModel, tool_collection: ToolCollection) -> Dict[str, Any]:
        agent = CodeAgent(
            tools=[*tool_collection.tools], 
            model=model, 
            add_base_tools=False # Introspection agent only uses provided tools
        )
        # Use the formatted prompt from __init__
        result = agent.run(self.INTROSPECT_PROMPT) 
        return result 