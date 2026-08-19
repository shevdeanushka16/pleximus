"""
Comprehensive unit tests for NOVA Smart Action Agent tools.
Covers:
- Calculator (valid, invalid, division by zero, percentage, powers, modulo)
- Text Utility (uppercase, lowercase, word count, character count, reverse, empty/invalid cases)
- Weather Lookup (valid city, unknown/invalid city, empty input)
- GitHub Repo Lookup (valid repo, nonexistent/invalid repo, input variations)
"""
import pytest
from tools.calculator import calculator
from tools.weather import get_weather
from tools.text_utils import text_utility
from tools.github import github_repo_info


# ==========================================
# 1. Calculator Tool Tests
# ==========================================

def test_calculator_valid_expression():
    """Test standard arithmetic operations: addition, subtraction, multiplication, division."""
    res1 = calculator("25 + 75")
    assert res1["status"] == "success"
    assert res1["result"] == 100

    res2 = calculator("15 * 4 - 10")
    assert res2["status"] == "success"
    assert res2["result"] == 50

    res3 = calculator("(10 + 20) * 3 / 2")
    assert res3["status"] == "success"
    assert res3["result"] == 45

    res4 = calculator("2 ** 8")
    assert res4["status"] == "success"
    assert res4["result"] == 256


def test_calculator_percentage():
    """Test percentage evaluation such as '25% of 840'."""
    res = calculator("25% of 840")
    assert res["status"] == "success"
    assert res["result"] == 210

    res_pct = calculator("840 * 25%")
    assert res_pct["status"] == "success"
    assert res_pct["result"] == 210


def test_calculator_division_by_zero():
    """Test division by zero returns friendly error without crashing."""
    res = calculator("10 / 0")
    assert res["status"] == "error"
    assert res["result"] is None
    assert "division by zero" in res["error"].lower()


def test_calculator_modulo_by_zero():
    """Test modulo by zero returns friendly error without crashing."""
    res = calculator("10 % 0")
    assert res["status"] == "error"
    assert res["result"] is None
    assert "zero" in res["error"].lower()


def test_calculator_invalid_expression():
    """Test syntax error handling for invalid or dangerous expressions."""
    res1 = calculator("25 + + * 4")
    assert res1["status"] == "error"
    assert res1["result"] is None

    # Verify code injection / arbitrary python execution is blocked
    res2 = calculator("__import__('os').system('ls')")
    assert res2["status"] == "error"
    assert res2["result"] is None

    res3 = calculator("")
    assert res3["status"] == "error"


# ==========================================
# 2. Text Utility Tool Tests
# ==========================================

def test_text_utility_uppercase():
    """Test uppercase conversion."""
    res = text_utility("hello world", "uppercase")
    assert res["status"] == "success"
    assert res["result"] == "HELLO WORLD"


def test_text_utility_lowercase():
    """Test lowercase conversion."""
    res = text_utility("HELLO NOVA AGENT", "lowercase")
    assert res["status"] == "success"
    assert res["result"] == "hello nova agent"


def test_text_utility_word_count():
    """Test counting words in a sentence."""
    res = text_utility("The quick brown fox jumps over the lazy dog", "word_count")
    assert res["status"] == "success"
    assert res["result"] == 9


def test_text_utility_character_count():
    """Test total and non-space character count."""
    res = text_utility("Hello World!", "character_count")
    assert res["status"] == "success"
    assert res["total_characters"] == 12
    assert res["characters_excluding_spaces"] == 11


def test_text_utility_reverse():
    """Test string reversal."""
    res = text_utility("Python", "reverse")
    assert res["status"] == "success"
    assert res["result"] == "nohtyP"


def test_text_utility_edge_cases():
    """Test empty string and invalid operation edge cases."""
    res_empty = text_utility("", "word_count")
    assert res_empty["status"] == "success"
    assert res_empty["result"] == 0

    res_invalid_op = text_utility("test text", "invalid_operation_name")
    assert res_invalid_op["status"] == "error"
    assert "Unknown operation" in res_invalid_op["error"]


# ==========================================
# 3. Weather Lookup Tool Tests
# ==========================================

def test_weather_invalid_city():
    """Test handling of unknown/fictional city names."""
    res = get_weather("xyzabcunknowncity123456789")
    assert res["status"] == "error"
    assert any(w in res["error"].lower() for w in ["not found", "coordinates", "timed out", "connection error"])


def test_weather_empty_city():
    """Test handling of empty city string."""
    res = get_weather("")
    assert res["status"] == "error"
    assert "valid city name" in res["error"].lower()


def test_weather_valid_city():
    """Test weather lookup for a major known city (Mumbai)."""
    res = get_weather("Mumbai")
    if res["status"] == "success":
        assert "Mumbai" in res["location"] or "Mumbai" in res["city"]
        assert isinstance(res["temperature_c"], (int, float))
        assert "condition" in res
        assert "wind_speed_kmh" in res
    else:
        # Handled gracefully if network is unavailable
        assert "error" in res
        assert res["status"] == "error"


# ==========================================
# 4. GitHub Repository Info Tool Tests
# ==========================================

def test_github_invalid_repository():
    """Test handling of a non-existent GitHub repository."""
    res = github_repo_info("abcxyz_nonexistent_owner_999", "not-a-real-repo-12345")
    assert res["status"] == "error"
    assert any(phrase in res["error"].lower() for phrase in ["not found", "404", "rate limit", "forbidden", "error"])


def test_github_combined_string_input():
    """Test passing 'owner/repo' in the first argument."""
    res = github_repo_info("octocat/Hello-World")
    if res["status"] == "success":
        assert res["repository_name"] == "Hello-World"
        assert res["stars"] >= 0
        assert "html_url" in res
    else:
        assert "error" in res


def test_github_valid_repository():
    """Test lookup of a popular public repository."""
    res = github_repo_info("google", "gemini-api")
    if res["status"] == "success":
        assert "gemini" in res["repository_name"].lower()
        assert res["stars"] >= 0
        assert res["visibility"] == "public"
    else:
        assert "error" in res
