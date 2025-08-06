"""
Enhanced Configuration Management
Provides better parameter management and user customization
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Display settings
    theme_color: str = "#2E86AB"
    default_currency: str = "USD"
    decimal_places: int = 0
    
    # Simulation settings
    default_simulations: int = 1000
    confidence_level: float = 0.8
    random_seed: int = 42
    
    # Business rules
    max_timeline_months: int = 120
    min_fte_cost: float = 50000
    max_fte_cost: float = 500000
    max_team_size: int = 50
    
    # Export settings
    excel_include_charts: bool = True
    excel_include_sensitivity: bool = True
    auto_save_scenarios: bool = True


@dataclass
class DefaultParameters:
    """Default parameter values."""
    
    build_timeline: float = 12
    build_timeline_std: float = 2
    fte_cost: float = 130000
    fte_cost_std: float = 15000
    fte_count: float = 3
    cap_percent: float = 75
    misc_costs: float = 0
    useful_life: float = 5
    prob_success: float = 90
    wacc: float = 8
    
    # Buy parameters
    product_price: float = 1000000
    subscription_price: float = 100000
    subscription_increase: float = 3
    
    # Risk parameters
    tech_risk: float = 0
    vendor_risk: float = 0
    market_risk: float = 0
    
    # Cost parameters
    maint_opex: float = 0
    maint_opex_std: float = 0
    capex: float = 0
    amortization: float = 0


class UserPreferences:
    """Manage user preferences and settings."""
    
    def __init__(self, config_file: str = "user_preferences.json"):
        self.config_file = Path(config_file)
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
        
        return self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences."""
        return {
            "last_used_parameters": asdict(DefaultParameters()),
            "favorite_scenarios": [],
            "ui_settings": {
                "show_advanced_options": False,
                "auto_calculate": True,
                "show_tooltips": True
            },
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
    
    def save_preferences(self):
        """Save current preferences to file."""
        try:
            self.preferences["last_modified"] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def update_last_used_parameters(self, parameters: Dict[str, Any]):
        """Update last used parameters."""
        self.preferences["last_used_parameters"] = parameters
        self.save_preferences()
    
    def add_favorite_scenario(self, scenario: Dict[str, Any]):
        """Add scenario to favorites."""
        favorites = self.preferences.get("favorite_scenarios", [])
        
        # Avoid duplicates
        scenario_name = scenario.get("name", "")
        if not any(fav.get("name") == scenario_name for fav in favorites):
            favorites.append(scenario)
            self.preferences["favorite_scenarios"] = favorites
            self.save_preferences()
    
    def get_ui_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get UI setting value."""
        return self.preferences.get("ui_settings", {}).get(setting_name, default)
    
    def set_ui_setting(self, setting_name: str, value: Any):
        """Set UI setting value."""
        if "ui_settings" not in self.preferences:
            self.preferences["ui_settings"] = {}
        
        self.preferences["ui_settings"][setting_name] = value
        self.save_preferences()


class TemplateManager:
    """Manage scenario templates and presets."""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict]:
        """Load default scenario templates."""
        return {
            "Enterprise Software": {
                "name": "Enterprise Software Build",
                "build_timeline": 18,
                "fte_count": 8,
                "fte_cost": 140000,
                "useful_life": 7,
                "prob_success": 75,
                "tech_risk": 15,
                "vendor_risk": 5
            },
            "Mobile App": {
                "name": "Mobile Application",
                "build_timeline": 9,
                "fte_count": 4,
                "fte_cost": 120000,
                "useful_life": 3,
                "prob_success": 85,
                "tech_risk": 10,
                "market_risk": 20
            },
            "Data Platform": {
                "name": "Data Analytics Platform",
                "build_timeline": 24,
                "fte_count": 12,
                "fte_cost": 150000,
                "useful_life": 10,
                "prob_success": 70,
                "tech_risk": 20,
                "vendor_risk": 10,
                "capex": 500000
            },
            "Integration Solution": {
                "name": "System Integration",
                "build_timeline": 6,
                "fte_count": 3,
                "fte_cost": 130000,
                "useful_life": 5,
                "prob_success": 90,
                "tech_risk": 5,
                "vendor_risk": 15
            }
        }
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get template by name."""
        return self.templates.get(template_name, {})
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def add_custom_template(self, name: str, parameters: Dict[str, Any]):
        """Add custom template."""
        self.templates[name] = parameters
    
    def create_template_from_scenario(self, scenario: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Create template from existing scenario."""
        template = {
            key: value for key, value in scenario.items()
            if key not in ['created_date', 'last_modified', 'results']
        }
        template['name'] = name
        self.add_custom_template(name, template)
        return template


# Global configuration instances
app_config = AppConfig()
default_params = DefaultParameters()
user_prefs = UserPreferences()
template_manager = TemplateManager()
