import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Import modes from the new package
from modes.base import EvaluationMode
from modes.interview import InterviewMode
from modes.introspection import IntrospectionMode
from smolagents import OpenAIServerModel, ToolCollection

# --- Utility Functions (Remain unchanged) ---

def get_server_parameters(server_type, server_params):
    """Create appropriate server parameters based on server type."""
    try:
        if server_type == "stdio":
            parts = server_params.split()
            if not parts:
                raise ValueError("No command specified for stdio server")
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            return StdioServerParameters(
                command=command,
                args=args,
                env={"UV_PYTHON": "3.12"}, # Default env, could be made configurable
            )
        elif server_type == "sse":
            if not server_params:
                raise ValueError("No URL specified for SSE server")
            return {"url": server_params}
        else:
            raise ValueError(f"Unknown server type: {server_type}")
    except Exception as e:
        print(f"Error configuring server parameters: {str(e)}", file=sys.stderr)
        sys.exit(1)

def save_report(result: Dict[str, Any], output_format: str, mode: str, timestamp: str):
    """Save the evaluation report in the specified format."""
    report_prefix = f"{mode}_report"
    # Look for templates inside mvp/modes/templates
    template_file = f"template_{mode}.html"
    # Construct the path relative to the current file's directory
    base_dir = os.path.dirname(__file__) 
    template_path = os.path.join(base_dir, "modes", "templates", template_file)
    output_file_html = f"{report_prefix}_{timestamp}.html"
    output_file_json = f"{report_prefix}_{timestamp}.json" # Always save raw data

    if output_format == "console":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif output_format == "json":
        with open(output_file_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Report saved as {output_file_json}")
    
    elif output_format == "yaml":
        output_file_yaml = f"{report_prefix}_{timestamp}.yaml"
        with open(output_file_yaml, "w", encoding="utf-8") as f:
            yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
        print(f"Report saved as {output_file_yaml}")
    
    elif output_format == "html":
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            print(f"Error: Template file not found at {template_path}", file=sys.stderr)
            print("Generating JSON output instead.")
            with open(output_file_json, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Report saved as {output_file_json}")
            return # Skip HTML generation

        # Convert the Python dict to a JSON string
        # DO NOT HTML escape this string, as it's going inside a <script> tag
        json_str = json.dumps(result, ensure_ascii=False)
        
        placeholder = "REPORT_DATA_PLACEHOLDER" # Define placeholder clearly
        
        # Prepare the script tag with the raw JSON string.
        # JSON.parse() will handle the string correctly.
        # We need to escape backticks and ${} if they appear in json_str, or use a different string delimiter.
        # Using JSON.stringify in JS side is safer if json_str could contain complex sequences.
        # Let's embed it directly for now, assuming simple JSON content unlikely to break JS template literals.
        # A more robust way would involve careful escaping or using JSON.stringify on JS side if possible.
        script_tag = f"""<script>
// Report data generated on {timestamp}
// Directly embed the JSON string. JSON.parse() will handle it.
const reportData = JSON.parse({json.dumps(json_str)});

// Call render functions (assuming renderReport exists in the template)
document.addEventListener("DOMContentLoaded", function() {{
    if (typeof renderReport === 'function') {{
        // Add error handling around rendering too
        try {{
            renderReport(reportData);
        }} catch (e) {{
            console.error("Error executing renderReport function:", e);
            document.body.innerHTML = "<div style='color: red; padding: 20px;'>Error rendering report details. Please check the console.</div>";
        }}
    }} else {{
        console.error("renderReport function not found in the template.");
        // Optionally, display raw JSON if render function missing
        try {{ // Add try-catch for safety
            document.body.innerHTML = '<pre>' + JSON.stringify(reportData, null, 2) + '</pre>';
        }} catch (e) {{
             console.error("Failed to display raw JSON data:", e);
        }}
    }}
}});
</script>
"""

        if placeholder in template_content:
             # If placeholder exists, replace it (less common now)
             print(f"Warning: Found legacy {placeholder}. Replacing it. Consider removing it from the template.", file=sys.stderr)
             html_content = template_content.replace(placeholder, json_str) # Inject raw JSON here too if placeholder used
        else:
            # Inject the script tag before </body> or </html>
            injection_point = template_content.find("</body>")
            if injection_point == -1:
                 injection_point = template_content.find("</html>")
                 if injection_point == -1:
                     print("Warning: Could not find </body> or </html> tag in template. Appending script to the end.", file=sys.stderr)
                     injection_point = len(template_content)
                 else:
                     print("Warning: Found </html> but not </body>. Injecting before </html>.", file=sys.stderr)
            
            html_content = template_content[:injection_point] + script_tag + template_content[injection_point:]
        
        with open(output_file_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML report saved as {output_file_html}")

        # Save the raw JSON data as well
        with open(output_file_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Raw data also saved as {output_file_json}")

# --- Main Execution (Refactored) ---

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="MCP Agent Evaluation Tool")
    parser.add_argument("--mode", type=str, choices=["introspect", "interview"], required=True,
                        help="Evaluation mode: introspect (agent evaluates itself) or interview (interviewer evaluates agent)")
    parser.add_argument("--output", type=str, choices=["console", "json", "yaml", "html"], 
                        default="console", help="Output format (default: console)")
    
    server_group = parser.add_argument_group("MCP Server Configuration")
    server_group.add_argument("--server-type", type=str, choices=["stdio", "sse"],
                       help="MCP server type (default: stdio if not specified)")
    server_group.add_argument("--server-params", type=str, 
                       help="Parameters for the MCP server. Required for the specified server type. "
                            "For stdio: command and args (e.g., 'uvx mcp-server-time --local-timezone=UTC'). "
                            "For sse: endpoint URL.")
    
    args = parser.parse_args()

    # Default server if none specified
    if not args.server_type:
        print("Warning: No server type specified. Using the time server (stdio) for demo.")
        args.server_type = "stdio"
        # Ensure a default command is provided if params are missing for the default type
        if not args.server_params:
             args.server_params = "uvx mcp-server-time --local-timezone=Asia/Shanghai" # Default demo server
    elif not args.server_params:
         parser.error(f"--server-params is required when --server-type is '{args.server_type}'")

    # Validate OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)
        
    try:
        server_parameters = get_server_parameters(args.server_type, args.server_params)
        
        model = OpenAIServerModel(
            model_id="gpt-4o", # Use gpt-4o as requested
            api_key=api_key,
        )

        # Instantiate the correct evaluation mode based on CLI argument
        eval_mode: EvaluationMode
        if args.mode == "introspect":
            eval_mode = IntrospectionMode()
        elif args.mode == "interview":
            eval_mode = InterviewMode()
        else:
            # This case should not happen due to argparse choices, but good for safety
            print(f"Error: Unknown mode '{args.mode}'", file=sys.stderr)
            sys.exit(1)
        
        # Run the selected evaluation mode within the ToolCollection context
        with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
            result = eval_mode.run(model, tool_collection)

        # Save the result
        if result:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_report(result, args.output, args.mode, timestamp)
        else:
             print("Error: Evaluation did not produce a result.", file=sys.stderr)
             sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        # Optional: Add more detailed traceback logging here if needed
        # import traceback
        # traceback.print_exc()
        sys.exit(1) 