"""
Enhanced utility functions for the Build vs Buy Dashboard
Consolidates and improves existing utility functions
"""
from typing import Any, Union, Dict, List
import re


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float with enhanced error handling.
    
    Args:
        value: Value to convert (can be string with currency symbols, etc.)
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    if value in (None, ""):
        return default
    
    try:
        # Handle string values that might contain currency symbols or commas
        if isinstance(value, str):
            # Remove currency symbols and commas
            clean_value = re.sub(r'[$,]', '', value.strip())
            return float(clean_value) if clean_value else default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer."""
    try:
        return int(safe_float(value, default))
    except (ValueError, TypeError):
        return default


def format_currency(amount: float, decimals: int = 0) -> str:
    """
    Format a number as currency string with improved formatting.
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places (default 0)
        
    Returns:
        Formatted currency string
    """
    if decimals == 0:
        return f"${amount:,.0f}"
    else:
        return f"${amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a decimal as percentage."""
    return f"{value * 100:.{decimals}f}%"


def validate_parameters(params: Dict[str, Any]) -> List[str]:
    """
    Enhanced parameter validation with specific business rules.
    
    Args:
        params: Dictionary of parameters to validate
        
    Returns:
        List of error messages (empty if no errors)
    """
    errors = []
    
    # Required parameters with minimum values
    required_params = {
        'build_timeline': (1, 120),  # 1 month to 10 years
        'fte_cost': (50000, 500000),  # Reasonable FTE cost range
        'fte_count': (1, 50),  # Team size limits
        'useful_life': (1, 20),  # Asset useful life
        'prob_success': (10, 100),  # Success probability range
        'wacc': (1, 30)  # WACC percentage range
    }
    
    for param, (min_val, max_val) in required_params.items():
        value = safe_float(params.get(param, 0))
        if value < min_val:
            errors.append(f"{param.replace('_', ' ').title()} must be at least {min_val}")
        elif value > max_val:
            errors.append(f"{param.replace('_', ' ').title()} cannot exceed {max_val}")
    
    # Validate buy options
    buy_selector = params.get('buy_selector', [])
    product_price = safe_float(params.get('product_price', 0))
    subscription_price = safe_float(params.get('subscription_price', 0))
    
    if 'one_time' in buy_selector and product_price <= 0:
        errors.append("One-time purchase price must be greater than 0")
    
    if 'subscription' in buy_selector and subscription_price <= 0:
        errors.append("Subscription price must be greater than 0")
    
    if not buy_selector:
        errors.append("At least one buy option must be selected")
    
    return errors


def clean_scenario_data(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize scenario data for storage/processing.
    
    Args:
        scenario: Raw scenario dictionary
        
    Returns:
        Cleaned scenario dictionary
    """
    cleaned = {}
    
    # Numeric fields that should be converted to float
    numeric_fields = [
        'build_timeline', 'build_timeline_std', 'fte_cost', 'fte_cost_std',
        'fte_count', 'useful_life', 'prob_success', 'wacc', 'cap_percent',
        'product_price', 'subscription_price', 'subscription_increase',
        'misc_costs', 'tech_risk', 'vendor_risk', 'market_risk',
        'maint_opex', 'maint_opex_std', 'capex', 'amortization'
    ]
    
    for field in numeric_fields:
        cleaned[field] = safe_float(scenario.get(field, 0))
    
    # String fields
    cleaned['name'] = str(scenario.get('name', 'Unnamed Scenario')).strip()
    
    # List fields
    for list_field in ['buy_selector', 'risk_selector', 'cost_selector']:
        cleaned[list_field] = scenario.get(list_field, []) or []
    
    return cleaned


class DataValidator:
    """Advanced validation class for complex business logic."""
    
    @staticmethod
    def validate_scenario_consistency(scenario: Dict[str, Any]) -> List[str]:
        """Validate internal consistency of scenario parameters."""
        errors = []
        
        # Check if timeline makes sense with team size
        timeline_months = safe_float(scenario.get('build_timeline', 12))
        fte_count = safe_float(scenario.get('fte_count', 3))
        
        if timeline_months > 24 and fte_count < 2:
            errors.append("Long projects (>24 months) typically require larger teams")
        
        if timeline_months < 6 and fte_count > 10:
            errors.append("Short projects (<6 months) with large teams may be inefficient")
        
        # Check cost relationships
        one_time_price = safe_float(scenario.get('product_price', 0))
        subscription_price = safe_float(scenario.get('subscription_price', 0))
        useful_life = safe_float(scenario.get('useful_life', 5))
        
        if one_time_price > 0 and subscription_price > 0:
            total_subscription = subscription_price * useful_life
            if one_time_price > total_subscription * 3:
                errors.append("One-time price seems high compared to subscription total")
        
        return errors
