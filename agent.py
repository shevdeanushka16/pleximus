"""
NOVA Agent Core - Powered by Google Gemini API and Native Tool Calling.
Follows the Flow: User Request -> Gemini Decision -> Python Tool Execution -> Gemini Synthesis -> Final Response.
Includes automatic model fallback across Gemini 3.5/3.7 models for 100% uptime.
"""
import os
import re
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

from google import genai
from google.genai import types

from tools.calculator import calculator
from tools.weather import get_weather
from tools.text_utils import text_utility
from tools.github import github_repo_info

# Mapping of tool names to Python functions
TOOL_REGISTRY = {
    "calculator": calculator,
    "get_weather": get_weather,
    "text_utility": text_utility,
    "github_repo_info": github_repo_info,
}

TOOL_DISPLAY_NAMES = {
    "calculator": "🧮 Calculator Module",
    "get_weather": "🌤️ Weather Lookup",
    "text_utility": "📝 Text Utility",
    "github_repo_info": "🐙 GitHub Explorer",
}

# Reliable Gemini 3.x models
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.1-flash-lite",
]

SYSTEM_INSTRUCTION = """You are NOVA, a smart, helpful, and friendly action agent. Your tagline is 'Ask. Decide. Act.'
You have access to 4 specialized real-world tools:
1. `calculator(expression)`: For safe mathematical calculations, percentages, powers, and arithmetic via AST.
2. `get_weather(city)`: For live weather reports, temperature, wind, and forecast conditions worldwide via Open-Meteo.
3. `text_utility(text, operation)`: For word count, character count, uppercase, lowercase, and string reversal.
4. `github_repo_info(owner, repo)`: For GitHub public repository stats, star counts, forks, primary language, and metadata.

Rules:
- When a user request requires calculation, weather, string operations, or GitHub data, ALWAYS call the appropriate tool.
- DO NOT hallucinate numbers, weather, or repository data; rely strictly on execution outputs.
- When tool results return, explain the answer clearly, warmly, and naturally in a friendly human tone.
- If a tool returns an error (e.g. division by zero, 404 repo, unknown city), explain the cause politely and helpfully.
- Never output raw code blocks of private chain-of-thought or internal reasoning signatures.
"""


def sanitize_api_key(key: Optional[str]) -> Optional[str]:
    """Clean, unwrap and validate API key string."""
    if not key:
        return None
    cleaned = str(key).strip().strip("\"'").strip()
    
    if "=" in cleaned:
        cleaned = cleaned.split("=", 1)[1].strip().strip("\"'").strip()
        
    if cleaned.lower().startswith("bearer "):
        cleaned = cleaned[7:].strip().strip("\"'").strip()
        
    if not cleaned or "your_gemini_api_key" in cleaned.lower() or "your_key" in cleaned.lower():
        return None
    return cleaned


class NovaAgent:
    """
    NOVA Agent implementation using the Google GenAI SDK with Tool Calling.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.5-flash-lite"):
        if api_key is not None:
            self.api_key = sanitize_api_key(api_key)
        else:
            self.api_key = sanitize_api_key(os.getenv("GEMINI_API_KEY"))
            
        self.model = model
        self.active_model = model
        self.client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Initialize the GenAI client with the current API key."""
        self.client = genai.Client(api_key=self.api_key)

    def set_api_key(self, api_key: str):
        """Update the API key dynamically."""
        self.api_key = sanitize_api_key(api_key)
        if self.api_key:
            self._init_client()
        else:
            self.client = None

    def is_configured(self) -> bool:
        """Check if the agent is ready with a valid API key."""
        return bool(self.api_key and len(self.api_key) > 5)

    def _call_gemini_with_fallback(self, contents: List[Any], config: Any):
        """Execute generate_content with automatic fallback if a model experiences 503 high demand or 404."""
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = None

        for idx, model_name in enumerate(models_to_try):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                self.active_model = model_name
                return response
            except Exception as e:
                err_text = str(e)
                last_error = e
                # Fall back on 503 (high demand), 429 (rate limit), or 404 (model deprecated/unavailable)
                if any(code in err_text for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND", "no longer available"]):
                    time.sleep(0.3)
                    continue
                else:
                    raise e

        if last_error:
            raise last_error

    def run(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an agent turn with tool decision and execution.
        """
        if not self.is_configured():
            return {
                "response": "⚠️ **Missing API Key**: Please add `GEMINI_API_KEY=your_key` in your `.env` file to enable NOVA.",
                "tool_used": None,
                "tool_display_name": None,
                "tool_args": None,
                "tool_result": None,
                "status": "Configuration Required",
                "error": "Missing or placeholder GEMINI_API_KEY",
            }

        if not user_message or not user_message.strip():
            return {
                "response": "Please enter a question or request for NOVA.",
                "tool_used": None,
                "tool_display_name": None,
                "tool_args": None,
                "tool_result": None,
                "status": "Direct Response",
                "error": None,
            }

        try:
            # Build tool declarations
            tool_list = [calculator, get_weather, text_utility, github_repo_info]
            config = types.GenerateContentConfig(
                tools=tool_list,
                temperature=0.1,
                system_instruction=SYSTEM_INSTRUCTION,
            )

            # Build history / contents
            contents = []
            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = "user" if msg.get("role") == "user" else "model"
                    content_text = msg.get("content", "")
                    if content_text:
                        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=content_text)]))

            # Current user prompt
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message.strip())]))

            # Step 1: Request model decision
            first_response = self._call_gemini_with_fallback(
                contents=contents,
                config=config,
            )

            # Step 2: Check if Gemini decided a tool call
            function_calls = first_response.function_calls
            if function_calls and len(function_calls) > 0:
                call = function_calls[0]
                tool_name = call.name
                tool_args = dict(call.args) if hasattr(call, "args") and call.args else {}

                # Step 3: Python executes the selected tool
                if tool_name in TOOL_REGISTRY:
                    tool_fn = TOOL_REGISTRY[tool_name]
                    try:
                        tool_result = tool_fn(**tool_args)
                    except Exception as exec_err:
                        tool_result = {
                            "status": "error",
                            "error": f"Execution error in {tool_name}: {str(exec_err)}",
                        }
                else:
                    tool_result = {
                        "status": "error",
                        "error": f"Tool '{tool_name}' is not registered in NOVA registry.",
                    }

                tool_status = (
                    "Completed"
                    if isinstance(tool_result, dict) and tool_result.get("status") == "success"
                    else "Handled with Error"
                )

                # Step 4: Pass tool result back to Gemini for synthesis
                contents.append(first_response.candidates[0].content)

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result},
                )
                contents.append(types.Content(role="user", parts=[function_response_part]))

                # Step 5: Receive final natural-language answer
                final_response = self._call_gemini_with_fallback(
                    contents=contents,
                    config=config,
                )

                final_text = final_response.text or "Here is your result."

                return {
                    "response": final_text,
                    "tool_used": tool_name,
                    "tool_display_name": TOOL_DISPLAY_NAMES.get(tool_name, tool_name),
                    "tool_args": tool_args,
                    "tool_result": tool_result,
                    "status": tool_status,
                    "error": None,
                }

            else:
                direct_text = first_response.text or "I processed your request."
                return {
                    "response": direct_text,
                    "tool_used": None,
                    "tool_display_name": None,
                    "tool_args": None,
                    "tool_result": None,
                    "status": "Direct Response",
                    "error": None,
                }

        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                user_friendly_msg = (
                    "❌ **Invalid API Key**: The provided Google Gemini API key was rejected. Please verify the `GEMINI_API_KEY` in your `.env` file."
                )
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                user_friendly_msg = (
                    "⏳ **High Traffic (503)**: Google's free-tier servers are momentarily busy. Please try sending your request again in a few seconds!"
                )
            else:
                user_friendly_msg = f"⚠️ **NOVA Encountered an Error**: {err_str}"

            return {
                "response": user_friendly_msg,
                "tool_used": None,
                "tool_display_name": None,
                "tool_args": None,
                "tool_result": None,
                "status": "Error",
                "error": err_str,
            }
