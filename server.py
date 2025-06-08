# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
import os
import sys
import json
import tempfile
import subprocess
import re
import logging

from typing import Annotated, Dict

from fastmcp import FastMCP
from pydantic import Field


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
security_logger = logging.getLogger('mcp_security')

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")


def basic_input_validation(text: str, field_name: str) -> str:
    """Basic input validation - only removes obviously dangerous content"""
    if not text or not isinstance(text, str):
        return ""

    # Remove null bytes and some control characters
    clean_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)

    # Log potential issues but don't block
    dangerous_patterns = [
        r'<script', r'javascript:', r'exec\s*\(', r'eval\s*\('
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, clean_text, re.IGNORECASE):
            security_logger.warning(
                f"Potential security risk in {field_name}: {pattern}")

    return clean_text.strip()


def launch_feedback_ui(project_directory: str, summary: str) -> dict[str, str]:
    """Launch feedback UI - adds basic security validation while maintaining original behavior"""

    # Basic input cleaning
    clean_project_dir = basic_input_validation(
        project_directory, "project_directory")
    clean_summary = basic_input_validation(summary, "summary")

    # If directory doesn't exist, use current directory but log it
    if not os.path.isdir(clean_project_dir):
        security_logger.warning(
            f"Directory does not exist: {clean_project_dir}, using current directory")
        clean_project_dir = os.getcwd()

    security_logger.info(
        f"Launching Interactive Feedback UI: {clean_project_dir}")

    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")

        # Check if feedback_ui.py exists
        if not os.path.exists(feedback_ui_path):
            security_logger.error(
                f"feedback_ui.py not found at: {feedback_ui_path}")
            return {"command_logs": "", "interactive_feedback": ""}

        # Run feedback_ui.py as a separate process
        # NOTE: There appears to be a bug in uv, so we need
        # to pass a bunch of special flags to make this work
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--project-directory", clean_project_dir,
            "--prompt", clean_summary,
            "--output-file", output_file
        ]

        security_logger.info(f"Executing command: {' '.join(args[:3])}...")

        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            timeout=300  # 5 minutes timeout protection
        )
        if result.returncode != 0:
            security_logger.error(
                f"UI launch failed with exit code: {result.returncode}")
            return {"command_logs": "", "interactive_feedback": ""}

        # Check if output file exists
        if not os.path.exists(output_file):
            security_logger.error("Output file does not exist")
            return {"command_logs": "", "interactive_feedback": ""}

        # Read the result from the temporary file
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        os.unlink(output_file)
        security_logger.info("Successfully obtained user feedback")

        # Ensure correct return format (same as original version)
        if isinstance(result, dict):
            return result
        else:
            # If format is incorrect, return default format
            return {"command_logs": "", "interactive_feedback": ""}

    except subprocess.TimeoutExpired:
        security_logger.error("UI process timed out after 5 minutes")
        if os.path.exists(output_file):
            os.unlink(output_file)
        return {"command_logs": "", "interactive_feedback": ""}
    except Exception as e:
        security_logger.error(f"Error occurred while launching UI: {e}")
        if os.path.exists(output_file):
            os.unlink(output_file)
        # Important: return correct dictionary format even on error, cannot raise
        return {"command_logs": "", "interactive_feedback": ""}


def first_line(text: str) -> str:
    return text.split("\n")[0].strip()


@mcp.tool()
def interactive_feedback(
    project_directory: Annotated[str, Field(description="Full path to the project directory")],
    summary: Annotated[str, Field(description="Short, one-line summary of the changes")],
) -> Dict[str, str]:
    """Request interactive feedback for a given project directory and summary"""
    try:

        clean_project_dir = first_line(
            project_directory) if project_directory else os.getcwd()
        clean_summary = first_line(summary) if summary else ""

        result = launch_feedback_ui(clean_project_dir, clean_summary)

        if not isinstance(result, dict):
            security_logger.error("Return result format error")
            return {"command_logs": "", "interactive_feedback": ""}

        return result

    except Exception as e:
        security_logger.error(f"interactive_feedback tool error: {e}")
        # Important: return empty correct format on error, cannot let MCP fail
        return {"command_logs": "", "interactive_feedback": ""}


if __name__ == "__main__":
    security_logger.info(
        "Interactive Feedback MCP server starting")
    mcp.run(transport="stdio")
