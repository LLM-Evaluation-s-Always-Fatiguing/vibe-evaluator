import datetime
import json
import os
import sys
from typing import Any, Dict, List, Union

import yaml
from mcp import StdioServerParameters
from pydantic import BaseModel, Field, field_validator
from smolagents import CodeAgent, OpenAIServerModel, ToolCollection


class Capability(BaseModel):
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Detailed capability description")

class EvaluationMetric(BaseModel):
    name: str = Field(..., description="Evaluation metric name")
    description: str = Field(..., description="Detailed evaluation metric description")

class EvaluationTask(BaseModel):
    id: int = Field(..., description="Task ID")
    description: str = Field(..., description="Task description")
    execution_result: Union[str, Dict[str, Any]] = Field(..., description="Execution result")
    execution_time: float = Field(..., description="Execution time (seconds)")

class CapabilityReportModel(BaseModel):
    capability_overview: str = Field(..., description="Capability overview")
    capability_list: List[Capability] = Field(..., description="Capability list")
    evaluation_metrics: List[EvaluationMetric] = Field(..., description="Evaluation metrics list")
    evaluation_tasks: List[EvaluationTask] = Field(..., description="Evaluation tasks list")
    final_metric_scores: Dict[str, float] = Field(
        ..., 
        description="Final metric scores, keys are metric names, values are corresponding scores"
    )
    
    @field_validator('final_metric_scores')
    @classmethod
    def validate_scores(cls, v: Dict[str, float]) -> Dict[str, float]:
        for key, value in v.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Score for {key} must be between 0 and 1, got {value}")
        return v

CapabilityReportSchema = CapabilityReportModel.model_json_schema()

INTROSPECT_PROMPT = f"""
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

{CapabilityReportSchema}
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

    parser = argparse.ArgumentParser(description="MCP Service Evaluation Tool")
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
        args.server_params = "uvx mcp-server-time --local-timezone=Asia/Shanghai"
    
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
            agent = CodeAgent(tools=[*tool_collection.tools], model=model, add_base_tools=False)
            result = agent.run(INTROSPECT_PROMPT)
            
            # Generate timestamp for filenames
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if args.output == "console":
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            elif args.output == "json":
                output_file = f"report_{timestamp}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Report saved as {output_file}")
            
            elif args.output == "yaml":
                output_file = f"report_{timestamp}.yaml"
                with open(output_file, "w", encoding="utf-8") as f:
                    yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
                print(f"Report saved as {output_file}")
            
            elif args.output == "html":
                # Check if template exists
                template_path = os.path.join(os.path.dirname(__file__), "template.html")
                
                # Read the template
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                except FileNotFoundError:
                    print(f"Error: Template file not found at {template_path}", file=sys.stderr)
                    print("Generating JSON output instead")
                    output_file = f"report_{timestamp}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"Report saved as {output_file}")
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
        // Report data generated on {timestamp}
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
                output_file = f"report_{timestamp}.html"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"Report saved as {output_file}")
                
                # Also save the raw data for reference
                with open(f"report_{timestamp}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Raw data also saved as report_{timestamp}.json")
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
