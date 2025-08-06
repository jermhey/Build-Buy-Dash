# Parameter Configuration for Build vs Buy Dashboard

# Risk Factors Configuration
RISK_FACTORS = [
    {
        "id": "tech",
        "label": "Technical Risk",
        "default": 0,
        "description": "Risk of technical challenges and cost overruns"
    },
    {
        "id": "vendor", 
        "label": "Vendor Risk",
        "default": 0,
        "description": "Risk of vendor delays or cost increases"
    },
    {
        "id": "market",
        "label": "Market Risk", 
        "default": 0,
        "description": "Risk of market changes affecting solution value"
    }
]

# Cost Parameters Configuration
COST_PARAMETERS = [
    {
        "id": "opex",
        "label": "Annual Maintenance/OpEx",
        "default": 0,
        "has_uncertainty": True,
        "description": "Ongoing annual operational costs"
    },
    {
        "id": "capex",
        "label": "CapEx Investment",
        "default": 0,
        "has_uncertainty": False,
        "description": "Upfront capital expenditures"
    },
    {
        "id": "amortization",
        "label": "Monthly Amortization",
        "default": 0,
        "has_uncertainty": False,
        "description": "Monthly recurring costs during build"
    }
]

# Buy Options Configuration
BUY_OPTIONS = [
    {
        "id": "one_time",
        "label": "One-Time Purchase (Flat Fee)",
        "default": 1000000
    },
    {
        "id": "subscription", 
        "label": "Annual Subscription",
        "default": 100000,
        "has_increase": True
    }
]

# Core Parameters with defaults
CORE_PARAMETERS = {
    "build_timeline": 12,
    "build_timeline_std": 0,
    "fte_cost": 130000,
    "fte_cost_std": 15000,
    "fte_count": 3,
    "cap_percent": 75,
    "tax_credit_rate": 17,  # 17% R&D tax credit rate (configurable)
    "misc_costs": 0,  # Miscellaneous one-time costs (migration, training, infrastructure)
    "useful_life": 5,
    "prob_success": 90,
    "wacc": 8
}
