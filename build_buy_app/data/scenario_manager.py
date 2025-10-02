"""
Advanced Scenario Management System
Provides save/load, comparison, and version control for scenarios
"""
import json
import uuid
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from dataclasses import dataclass, asdict


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


@dataclass
class ScenarioMetadata:
    """Metadata for a scenario."""
    id: str
    name: str
    description: str
    created_date: str
    last_modified: str
    version: int
    tags: List[str]
    author: str = "User"


class ScenarioManager:
    """Manage scenario persistence and operations."""
    
    def __init__(self, storage_dir: str = "scenarios"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.metadata_file = self.storage_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load scenario metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save scenario metadata."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def save_scenario(self, scenario: Dict[str, Any], name: str, 
                     description: str = "", tags: List[str] = None) -> str:
        """Save a scenario with metadata."""
        # Sanitize inputs
        name = sanitize_string(name, 100)
        description = sanitize_string(description, 500)
        
        if not name.strip():
            raise ValueError("Scenario name cannot be empty")
        
        scenario_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create metadata
        metadata = ScenarioMetadata(
            id=scenario_id,
            name=name,
            description=description,
            created_date=timestamp,
            last_modified=timestamp,
            version=1,
            tags=[sanitize_string(tag, 50) for tag in (tags or [])]
        )
        
        # Save scenario data
        scenario_file = self.storage_dir / f"{scenario_id}.json"
        try:
            scenario_data = {
                "metadata": asdict(metadata),
                "parameters": scenario,
                "results": scenario.get("results", {})
            }
            
            with open(scenario_file, 'w') as f:
                json.dump(scenario_data, f, indent=2)
            
            # Update metadata index
            self.metadata[scenario_id] = asdict(metadata)
            self._save_metadata()
            
            return scenario_id
            
        except Exception as e:
            print(f"Error saving scenario: {e}")
            return ""
    
    def load_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Load a scenario by ID."""
        scenario_file = self.storage_dir / f"{scenario_id}.json"
        
        if not scenario_file.exists():
            return None
        
        try:
            with open(scenario_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scenario: {e}")
            return None
    
    def list_scenarios(self, tags: List[str] = None) -> List[Dict[str, Any]]:
        """List all scenarios with optional tag filtering."""
        scenarios = []
        
        for scenario_id, metadata in self.metadata.items():
            if tags:
                scenario_tags = set(metadata.get("tags", []))
                if not any(tag in scenario_tags for tag in tags):
                    continue
            
            scenarios.append({
                "id": scenario_id,
                **metadata
            })
        
        # Sort by last modified date
        scenarios.sort(key=lambda x: x["last_modified"], reverse=True)
        return scenarios
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario."""
        scenario_file = self.storage_dir / f"{scenario_id}.json"
        
        try:
            if scenario_file.exists():
                scenario_file.unlink()
            
            if scenario_id in self.metadata:
                del self.metadata[scenario_id]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting scenario: {e}")
            return False
    
    def update_scenario(self, scenario_id: str, scenario: Dict[str, Any], 
                       name: str = None, description: str = None, 
                       tags: List[str] = None) -> bool:
        """Update an existing scenario."""
        existing = self.load_scenario(scenario_id)
        if not existing:
            return False
        
        # Update metadata
        metadata = existing["metadata"]
        if name:
            metadata["name"] = name
        if description is not None:
            metadata["description"] = description
        if tags is not None:
            metadata["tags"] = tags
        
        metadata["last_modified"] = datetime.now().isoformat()
        metadata["version"] = metadata.get("version", 1) + 1
        
        # Update scenario data
        scenario_data = {
            "metadata": metadata,
            "parameters": scenario,
            "results": scenario.get("results", {})
        }
        
        scenario_file = self.storage_dir / f"{scenario_id}.json"
        try:
            with open(scenario_file, 'w') as f:
                json.dump(scenario_data, f, indent=2)
            
            # Update metadata index
            self.metadata[scenario_id] = metadata
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error updating scenario: {e}")
            return False


class ScenarioComparison:
    """Compare multiple scenarios."""
    
    def __init__(self, scenarios: List[Dict[str, Any]]):
        self.scenarios = scenarios
    
    def create_comparison_table(self) -> pd.DataFrame:
        """Create comparison table of key metrics."""
        comparison_data = []
        
        for scenario in self.scenarios:
            params = scenario.get("parameters", {})
            results = scenario.get("results", {})
            metadata = scenario.get("metadata", {})
            
            row = {
                "Scenario": metadata.get("name", "Unnamed"),
                "Build Cost (PV)": results.get("pv_build_cost", 0),
                "Buy Cost (PV)": results.get("pv_buy_cost", 0),
                "NPV Difference": results.get("npv_difference", 0),
                "Recommendation": results.get("recommendation", "Unknown"),
                "Success Probability": params.get("prob_success", 0),
                "Timeline (months)": params.get("build_timeline", 0),
                "Team Size": params.get("fte_count", 0),
                "Risk Score": self._calculate_risk_score(params)
            }
            comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def _calculate_risk_score(self, params: Dict[str, Any]) -> float:
        """Calculate overall risk score."""
        tech_risk = params.get("tech_risk", 0)
        vendor_risk = params.get("vendor_risk", 0)
        market_risk = params.get("market_risk", 0)
        
        # Weight technical risk higher for build scenarios
        weights = {"tech": 0.5, "vendor": 0.3, "market": 0.2}
        
        risk_score = (
            tech_risk * weights["tech"] +
            vendor_risk * weights["vendor"] +
            market_risk * weights["market"]
        )
        
        return round(risk_score, 1)
    
    def get_best_scenario(self, criteria: str = "npv") -> Dict[str, Any]:
        """Get best scenario based on criteria."""
        if not self.scenarios:
            return {}
        
        if criteria == "npv":
            # Highest NPV difference
            best = max(self.scenarios, 
                      key=lambda x: x.get("results", {}).get("npv_difference", 0))
        elif criteria == "risk":
            # Lowest risk
            best = min(self.scenarios,
                      key=lambda x: self._calculate_risk_score(x.get("parameters", {})))
        elif criteria == "timeline":
            # Shortest timeline
            best = min(self.scenarios,
                      key=lambda x: x.get("parameters", {}).get("build_timeline", float('inf')))
        else:
            best = self.scenarios[0]
        
        return best
    
    def export_comparison(self, filename: str = None) -> str:
        """Export comparison to Excel."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scenario_comparison_{timestamp}.xlsx"
        
        df = self.create_comparison_table()
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Comparison', index=False)
            
            # Add formatting
            workbook = writer.book
            worksheet = writer.sheets['Comparison']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Format currency columns
            currency_format = workbook.add_format({'num_format': '$#,##0'})
            percent_format = workbook.add_format({'num_format': '0%'})
            
            # Apply formatting
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)
                
                if 'Cost' in column or 'NPV' in column:
                    worksheet.set_column(col_num, col_num, 15, currency_format)
                elif 'Probability' in column:
                    worksheet.set_column(col_num, col_num, 12, percent_format)
                else:
                    worksheet.set_column(col_num, col_num, 12)
        
        return filename


# Global scenario manager instance
scenario_manager = ScenarioManager()
