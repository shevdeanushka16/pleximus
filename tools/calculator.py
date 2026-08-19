"""
Safe AST-based Calculator Tool for NOVA Agent.
Evaluates mathematical expressions without using unrestricted eval().
"""
import ast
import operator
import re
from typing import Any, Dict, Union

# Whitelisted operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

MAX_EXPONENT = 1000
MAX_RESULT = 1e308


def _safe_eval_node(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate an AST node safely."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body)

    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    elif isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        op_type = type(node.op)

        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

        if op_type is ast.Div and right == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")

        if op_type is ast.FloorDiv and right == 0:
            raise ZeroDivisionError("Floor division by zero is not allowed.")

        if op_type is ast.Mod and right == 0:
            raise ZeroDivisionError("Modulo by zero is not allowed.")

        if op_type is ast.Pow:
            if abs(right) > MAX_EXPONENT or (abs(left) > 1000 and right > 100):
                raise ValueError(f"Exponent too large (max exponent: {MAX_EXPONENT}).")

        calc_op = SAFE_OPERATORS[op_type]
        res = calc_op(left, right)

        if isinstance(res, (int, float)) and abs(res) > MAX_RESULT:
            raise OverflowError("Result exceeds maximum calculable limit.")

        return res

    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_node(node.operand)
        op_type = type(node.op)

        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        return SAFE_OPERATORS[op_type](operand)

    else:
        raise ValueError(f"Unsupported syntax expression: {type(node).__name__}")


def _normalize_expression(expression: str) -> str:
    """Preprocess natural language variations into standard mathematical expressions."""
    expr = expression.strip()

    # Handle percentage of: '25% of 840' -> '(25 * 0.01 * 840)'
    expr = re.sub(
        r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)",
        r"(\1 * 0.01 * \2)",
        expr,
        flags=re.IGNORECASE,
    )

    # Handle percentage not followed by another number (e.g. '840 * 25%' -> '840 * (25/100)', but NOT '10 % 3')
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*%(?!\s*\d)", r"(\1/100)", expr)

    # Replace unicode multiplication and division symbols
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")

    return expr


def calculator(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Supports: +, -, *, /, %, **, //, and parentheses ().
    Safely handles division by zero and invalid syntax.
    
    Args:
        expression: A string containing the math expression (e.g. '25 * 840 / 100', '10 / 2', '2**8').
        
    Returns:
        A dictionary containing the status, evaluated result, and any error message.
    """
    if not expression or not expression.strip():
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "error": "Empty mathematical expression provided.",
        }

    cleaned = _normalize_expression(expression)

    try:
        # Parse expression into an AST tree in 'eval' mode
        tree = ast.parse(cleaned, mode="eval")
        result = _safe_eval_node(tree)

        # Clean integer display if float has no decimal part (e.g. 5.0 -> 5)
        if isinstance(result, float) and result.is_integer():
            formatted = int(result)
        elif isinstance(result, float):
            formatted = round(result, 6)
        else:
            formatted = result

        return {
            "status": "success",
            "expression": expression,
            "result": formatted,
            "formatted_result": str(formatted),
            "error": None,
        }

    except ZeroDivisionError as e:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "error": f"Math Error: {str(e)}",
        }
    except OverflowError as e:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "error": f"Overflow Error: {str(e)}",
        }
    except (SyntaxError, ValueError) as e:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "error": f"Invalid expression syntax: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "result": None,
            "error": f"Calculation error: {str(e)}",
        }
