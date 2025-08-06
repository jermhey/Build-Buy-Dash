"""
Utility functions for the Build vs Buy Dashboard
"""
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
    
    # Check percentage parameters
    percentage_params = ['prob_success', 'wacc']
    for param in percentage_params:
        value = safe_float(params.get(param))
        if value < 0 or value > 100:
            errors.append(f"{param.replace('_', ' ').title()} must be between 0 and 100")
    
    # Check timeline
    timeline = safe_float(params.get('build_timeline'))
    if timeline > 120:  # 10 years seems excessive
        errors.append("Build timeline seems unusually long (>10 years)")
    
    return errors
