"""
Utility functions for the Build vs Buy Dashboard
"""
import re
from typing import Any, Union


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float with a default fallback.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent injection attacks.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', value)
    
    # Limit length
    return sanitized[:max_length].strip()


def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
    """
    Validate that a numeric value is within acceptable range.
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        
    Returns:
        True if valid, False otherwise
    """
    return min_val <= value <= max_val


def format_currency(amount: float) -> str:
    """
    Format a number as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.0f}"


def validate_parameters(params: dict) -> list:
    """
    Validate input parameters and return list of errors.
    
    Args:
        params: Dictionary of parameters to validate
        
    Returns:
        List of error messages (empty if no errors)
    """
    errors = []
    
    # Check required parameters
    required = ['build_timeline', 'fte_cost', 'fte_count', 'useful_life', 'prob_success', 'wacc']
    for param in required:
        value = safe_float(params.get(param))
        if value <= 0:
            errors.append(f"{param.replace('_', ' ').title()} must be greater than 0")
    
    # Check percentage parameters with strict bounds
    percentage_params = ['prob_success', 'wacc']
    for param in percentage_params:
        value = safe_float(params.get(param))
        if not validate_numeric_range(value, 0, 100):
            errors.append(f"{param.replace('_', ' ').title()} must be between 0 and 100")
    
    # Check timeline with reasonable business limits
    timeline = safe_float(params.get('build_timeline'))
    if not validate_numeric_range(timeline, 1, 120):  # 1 month to 10 years
        errors.append("Build timeline must be between 1 and 120 months")
    
    # Check FTE count is reasonable
    fte_count = safe_float(params.get('fte_count', 0))
    if not validate_numeric_range(fte_count, 1, 1000):  # Reasonable team size limits
        errors.append("FTE count must be between 1 and 1000")
    
    # Validate costs are in reasonable ranges
    fte_cost = safe_float(params.get('fte_cost', 0))
    if not validate_numeric_range(fte_cost, 1000, 1000000):  # $1K to $1M per FTE
        errors.append("FTE cost must be between $1,000 and $1,000,000")
    
    return errors
