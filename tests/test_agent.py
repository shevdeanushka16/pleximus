"""
Unit tests for NovaAgent decision and execution logic.
"""
from unittest.mock import MagicMock, patch
import pytest
from agent import NovaAgent, TOOL_REGISTRY, TOOL_DISPLAY_NAMES


def test_agent_unconfigured():
    """Verify agent returns a friendly configuration message when API key is missing."""
    agent = NovaAgent(api_key="")
    res = agent.run("What's the weather in Paris?")
    assert res["status"] == "Configuration Required"
    assert "MISSING_API_CREDENTIALS" in res["response"] or "API_KEY" in res["response"]
    assert res["tool_used"] is None


def test_agent_empty_message():
    """Verify agent handles empty messages gracefully."""
    agent = NovaAgent(api_key="dummy_key_for_testing")
    res = agent.run("   ")
    assert "Awaiting input" in res["response"] or "Please enter a question" in res["response"]


@patch("agent.genai.Client")
def test_agent_calculator_tool_flow(mock_client_cls):
    """Test full agent flow when Gemini chooses the calculator tool."""
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_func_call = MagicMock()
    mock_func_call.name = "calculator"
    mock_func_call.args = {"expression": "25% of 840"}

    first_response = MagicMock()
    first_response.function_calls = [mock_func_call]
    first_response.candidates = [MagicMock()]

    second_response = MagicMock()
    second_response.function_calls = []
    second_response.text = "25% of 840 is 210."

    mock_client.models.generate_content.side_effect = [first_response, second_response]

    agent = NovaAgent(api_key="test_api_key")
    result = agent.run("Calculate 25% of 840")

    assert result["tool_used"] == "calculator"
    assert result["status"] == "Completed"
    assert result["tool_result"]["result"] == 210
    assert "210" in result["response"]
    assert mock_client.models.generate_content.call_count == 2


@patch("agent.genai.Client")
def test_agent_weather_tool_flow(mock_client_cls):
    """Test full agent flow when Gemini chooses weather tool."""
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_func_call = MagicMock()
    mock_func_call.name = "get_weather"
    mock_func_call.args = {"city": "Mumbai"}

    first_response = MagicMock()
    first_response.function_calls = [mock_func_call]
    first_response.candidates = [MagicMock()]

    second_response = MagicMock()
    second_response.function_calls = []
    second_response.text = "The current weather in Mumbai is warm and clear."

    mock_client.models.generate_content.side_effect = [first_response, second_response]

    agent = NovaAgent(api_key="test_api_key")
    result = agent.run("What's the weather in Mumbai?")

    assert result["tool_used"] == "get_weather"
    assert "OPEN_METEO" in result["tool_display_name"] or "Weather" in result["tool_display_name"]
    assert mock_client.models.generate_content.call_count == 2


@patch("agent.genai.Client")
def test_agent_direct_response_no_tool(mock_client_cls):
    """Test agent flow when no tool is needed (e.g. general greeting)."""
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    first_response = MagicMock()
    first_response.function_calls = []
    first_response.text = "Hello! I am NOVA, your smart action agent. How can I help you today?"

    mock_client.models.generate_content.return_value = first_response

    agent = NovaAgent(api_key="test_api_key")
    result = agent.run("Hello NOVA!")

    assert result["tool_used"] is None
    assert result["status"] == "Direct Response"
    assert "Hello" in result["response"]
    assert mock_client.models.generate_content.call_count == 1
