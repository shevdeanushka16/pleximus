"""
Word/Text Utility Tool for NOVA Agent.
Performs text manipulation: uppercase, lowercase, word count, character count, and reverse.
"""
from typing import Any, Dict

VALID_OPERATIONS = [
    "uppercase",
    "lowercase",
    "word_count",
    "character_count",
    "reverse",
]


def text_utility(text: str, operation: str) -> Dict[str, Any]:
    """
    Perform text processing operations such as case conversion, counting, and reversal.
    
    Args:
        text: The input text to process.
        operation: The operation to perform ('uppercase', 'lowercase', 'word_count', 'character_count', 'reverse').
        
    Returns:
        A dictionary containing the operation performed, resulting output/counts, and any error message.
    """
    if text is None:
        return {
            "status": "error",
            "operation": operation,
            "error": "Input text cannot be None.",
        }

    if not operation or not str(operation).strip():
        return {
            "status": "error",
            "operation": operation,
            "error": f"Operation required. Supported operations: {', '.join(VALID_OPERATIONS)}",
        }

    # Normalize operation string (e.g. "word-count", "Word Count" -> "word_count")
    op_normalized = (
        str(operation)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    if op_normalized in ["upper", "uppercase", "to_upper", "to_uppercase"]:
        processed = text.upper()
        return {
            "status": "success",
            "operation": "uppercase",
            "original_text": text,
            "result": processed,
            "length": len(processed),
            "error": None,
        }

    elif op_normalized in ["lower", "lowercase", "to_lower", "to_lowercase"]:
        processed = text.lower()
        return {
            "status": "success",
            "operation": "lowercase",
            "original_text": text,
            "result": processed,
            "length": len(processed),
            "error": None,
        }

    elif op_normalized in ["word_count", "words", "count_words"]:
        words = text.split()
        count = len(words)
        return {
            "status": "success",
            "operation": "word_count",
            "original_text": text,
            "result": count,
            "word_count": count,
            "words": words[:20],  # Sample first few words
            "error": None,
        }

    elif op_normalized in ["character_count", "char_count", "length", "chars", "count_characters"]:
        total_chars = len(text)
        non_space_chars = len(text.replace(" ", "").replace("\t", "").replace("\n", ""))
        return {
            "status": "success",
            "operation": "character_count",
            "original_text": text,
            "result": total_chars,
            "total_characters": total_chars,
            "characters_excluding_spaces": non_space_chars,
            "error": None,
        }

    elif op_normalized in ["reverse", "invert", "backwards"]:
        processed = text[::-1]
        return {
            "status": "success",
            "operation": "reverse",
            "original_text": text,
            "result": processed,
            "error": None,
        }

    else:
        return {
            "status": "error",
            "operation": operation,
            "original_text": text,
            "result": None,
            "error": f"Unknown operation '{operation}'. Supported operations: {', '.join(VALID_OPERATIONS)}",
        }
