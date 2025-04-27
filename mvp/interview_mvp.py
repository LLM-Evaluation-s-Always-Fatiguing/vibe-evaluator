import datetime
import json
import os
import sys
from typing import Dict, List

import yaml
from mcp import StdioServerParameters
from pydantic import BaseModel, Field, field_validator
from smolagents import CodeAgent, OpenAIServerModel, ToolCallingAgent, ToolCollection


class Question(BaseModel):
    id: int = Field(..., description="Question ID")
    question: str = Field(..., description="Question asked by the interviewer")
    answer: str = Field(..., description="Answer provided by the candidate")

class Capability(BaseModel):
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Detailed capability description")
    confidence: float = Field(..., description="Confidence score (0-1)")

class InterviewReportModel(BaseModel):
    candidate_overview: str = Field(..., description="Overview of the candidate's capabilities")
    declared_capabilities: List[Capability] = Field(..., description="Capabilities the candidate claims to have")
    verified_capabilities: List[Capability] = Field(..., description="Capabilities verified through testing")
    questions_and_answers: List[Question] = Field(..., description="Interview questions and answers")
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

InterviewReportSchema = InterviewReportModel.model_json_schema()

INTERVIEW_PROMPT = f"""
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

{InterviewReportSchema}
"""

def get_server_parameters(server_type, server_params):
    """Create appropriate server parameters based on server type."""
    try:
        if server_type == "stdio":
            # Parse the stdio command string
            parts = server_params.split()
            if not parts:
                raise ValueError("No command specified for stdio server")
                
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            return StdioServerParameters(
                command=command,
                args=args,
                env={"UV_PYTHON": "3.12"},  # Default env, could be made configurable
            )
        elif server_type == "sse":
            # Use the parameter as URL
            if not server_params:
                raise ValueError("No URL specified for SSE server")
                
            return {
                "url": server_params
            }
        else:
            raise ValueError(f"Unknown server type: {server_type}")
    except Exception as e:
        print(f"Error configuring server parameters: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    import datetime

    from dotenv import load_dotenv
    
    load_dotenv()

    parser = argparse.ArgumentParser(description="MCP Service Interview Evaluation Tool")
    parser.add_argument("--output", type=str, choices=["console", "json", "yaml", "html"], 
                        default="console", help="Output format (default: console)")
    
    # Add server type and parameter arguments
    server_group = parser.add_argument_group("MCP Server Configuration")
    server_group.add_argument("--server-type", type=str, choices=["stdio", "sse"],
                       help="MCP server type (default: stdio)")
    server_group.add_argument("--server-params", type=str, 
                       help="Parameters for the MCP server. For stdio: command and args as a string. For SSE: endpoint URL")
    
    args = parser.parse_args()

    if args.server_type != "stdio" and args.server_type != "sse":
        print("Warning: No server type specified. Using the time server for demo.")
        args.server_type = "stdio"
        args.server_params = "uvx mcp-server-time --local-timezone=America/New_York"
    
    # Set default server parameters if not provided
    if args.server_type == "stdio" and not args.server_params:
        parser.error("--server-params is required when using a stdio server")
    
    # Validate required parameters
    if args.server_type == "sse" and not args.server_params:
        parser.error("--server-params is required when using an SSE server")
        
    try:
        # Get appropriate server parameters
        server_parameters = get_server_parameters(args.server_type, args.server_params)
        
        model = OpenAIServerModel(
            model_id="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # If OPENAI_API_KEY is not set
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)

        with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
            # Create the candidate agent with the tools
            candidate_agent = ToolCallingAgent(
                tools=[*tool_collection.tools],
                model=model,
                add_base_tools=False,
                name="ToolAgent",
                description="An AI candidate with specific capabilities provided by the available tools. When asked about capabilities, only describe what you can do with your available tools, not your general abilities."
            )

            # Create the interviewer agent that can manage the candidate
            interviewer_agent = CodeAgent(
                tools=[], 
                model=model, 
                add_base_tools=True, 
                managed_agents=[candidate_agent]
            )
            
            # Run the interview
            result = interviewer_agent.run(INTERVIEW_PROMPT)
            
            # Generate timestamp for filenames
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if args.output == "console":
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            elif args.output == "json":
                output_file = f"interview_report_{timestamp}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Interview report saved as {output_file}")
            
            elif args.output == "yaml":
                output_file = f"interview_report_{timestamp}.yaml"
                with open(output_file, "w", encoding="utf-8") as f:
                    yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
                print(f"Interview report saved as {output_file}")
            
            elif args.output == "html":
                # Check if template exists
                template_path = os.path.join(os.path.dirname(__file__), "template_interview.html")
                
                # Read the template
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                except FileNotFoundError:
                    print(f"Error: Template file not found at {template_path}", file=sys.stderr)
                    print("Generating JSON output instead")
                    output_file = f"interview_report_{timestamp}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"Interview report saved as {output_file}")
                    sys.exit(1)
                
                # Inject the report data into the template
                # Properly encode JSON to make it safe for HTML
                import html
                
                # Convert the data to JSON string
                json_str = json.dumps(result, ensure_ascii=False)
                
                # Escape the JSON string for HTML
                escaped_json = html.escape(json_str)
                
                # Replace a placeholder or add a script section with the data
                if "REPORT_DATA_PLACEHOLDER" in template_content:
                    # Simple placeholder replacement
                    html_content = template_content.replace("REPORT_DATA_PLACEHOLDER", escaped_json)
                else:
                    # If no placeholder found, insert before the closing body tag
                    script_tag = f"""<script>
        // Interview report data generated on {timestamp}
        const reportData = JSON.parse("{escaped_json}".replace(/&quot;/g, '"').replace(/&#x27;/g, "'"));
        
        // Call render functions
        document.addEventListener("DOMContentLoaded", function() {{
            // Initialize rendering
            renderReport(reportData);
        }});
    </script>
    </body>"""
                    html_content = template_content.replace("</body>", script_tag)
                
                # Save the rendered HTML
                output_file = f"interview_report_{timestamp}.html"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"Interview report saved as {output_file}")
                
                # Also save the raw data for reference
                with open(f"interview_report_{timestamp}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Raw data also saved as interview_report_{timestamp}.json")
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1) 