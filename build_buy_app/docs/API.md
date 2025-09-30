# API Documentation

This document provides detailed information about the core APIs and interfaces in the Build vs Buy Decision Dashboard.

## Simulation Engine API

### BuildVsBuySimulator Class

The core simulation engine that performs Monte Carlo analysis.

#### Constructor

```python
BuildVsBuySimulator(n_simulations: int = 1000, random_seed: int = 42)
```

**Parameters:**
- `n_simulations`: Number of Monte Carlo iterations (default: 1000)
- `random_seed`: Random seed for reproducible results (default: 42)

#### Main Methods

##### simulate(params: Dict[str, Any]) -> Dict[str, Any]

Performs the complete build vs buy analysis.

**Input Parameters:**

| Parameter | Type | Description | Range/Notes |
|-----------|------|-------------|-------------|
| `build_timeline` | float | Development duration in months | > 0 |
| `fte_cost` | float | Annual FTE cost | > 0 |
| `fte_count` | float | Number of FTEs | > 0 |
| `useful_life` | float | Asset useful life in years | > 0 |
| `prob_success` | float | Success probability (%) | 0-100 |
| `wacc` | float | Discount rate (%) | > 0 |
| `tech_risk` | float | Technical risk (%) | >= 0 |
| `vendor_risk` | float | Vendor risk (%) | >= 0 |
| `market_risk` | float | Market risk (%) | >= 0 |
| `product_price` | float | One-time purchase price | >= 0 |
| `subscription_price` | float | Annual subscription cost | >= 0 |

**Returns:**

```python
{
    'expected_build_cost': float,      # Mean build cost (PV)
    'build_cost_p10': float,           # 10th percentile
    'build_cost_p50': float,           # Median
    'build_cost_p90': float,           # 90th percentile
    'buy_total_cost': float,           # Total buy cost (PV)
    'npv_difference': float,           # Buy - Build
    'recommendation': str,             # 'Build' or 'Buy'
    'cost_distribution': List[float]   # Full distribution
}
```

## Excel Export API

### ExcelExporter Class

Generates comprehensive Excel workbooks with analysis results.

#### Main Methods

##### create_excel_export(scenario_data: Dict, stored_scenarios: List = None) -> bytes

Generates complete Excel workbook.

**Parameters:**
- `scenario_data`: Dictionary with all scenario parameters
- `stored_scenarios`: Optional list of saved scenarios for comparison

**Returns:**
- `bytes`: Excel file content ready for download

#### Sheet Structure

| Sheet Name | Description | Key Features |
|------------|-------------|--------------|
| Input Parameters | Editable parameter values | Yellow input cells, auto-calculations |
| Cost Timeline | Year-by-year breakdown | PV formulas, risk adjustments |
| Executive Summary | High-level results | Key metrics, recommendations |
| Dashboard | Visual charts | Charts reference live data |
| Sensitivity Analysis | Parameter impact | ±20% variation testing |
| Break Even Analysis | Decision thresholds | Critical value calculations |
| Reconciliation | Excel vs Simulation | Formula comparison |
| Methodology | Calculation details | Documentation and formulas |

## Configuration API

### Parameters Module (config/parameters.py)

Central configuration for default values and validation.

#### Key Constants

```python
CORE_PARAMETERS = {
    "build_timeline": 12,      # months
    "fte_cost": 130000,        # annual cost
    "fte_count": 3,            # team size
    "cap_percent": 75,         # capitalization %
    "tax_credit_rate": 17,     # R&D tax credit %
    "useful_life": 5,          # years
    "prob_success": 90,        # percentage
    "wacc": 8                  # percentage
}
```

## Data Management API

### ScenarioManager Class

Handles scenario persistence and comparison.

#### Main Methods

##### save_scenario(scenario: Dict, name: str, description: str = "") -> str

Saves scenario with metadata.

**Returns:** Unique scenario ID

##### load_scenario(scenario_id: str) -> Optional[Dict]

Loads scenario by ID.

##### list_scenarios(tags: List[str] = None) -> List[Dict]

Lists all saved scenarios with optional filtering.

### Data Schemas

#### Scenario Data Structure

```python
{
    "metadata": {
        "id": str,
        "name": str,
        "description": str,
        "created_date": str,     # ISO format
        "last_modified": str,    # ISO format
        "version": int,
        "tags": List[str],
        "author": str
    },
    "parameters": {
        # All simulation parameters
    },
    "results": {
        # Simulation results (optional)
    }
}
```

## UI Component API

### ModernUI Class

Provides responsive web interface components.

#### Key Methods

##### create_modern_layout() -> html.Div

Returns complete dashboard layout.

##### create_parameter_card(title: str, icon: str, children: List, color: str = "primary") -> dbc.Card

Creates styled parameter input cards.

## Error Handling

### Common Exceptions

```python
class ValidationError(Exception):
    """Raised when parameter validation fails."""
    pass

class CalculationError(Exception):
    """Raised when mathematical calculations fail."""
    pass

class ExportError(Exception):
    """Raised when Excel export fails."""
    pass
```

### Error Response Format

```python
{
    "error": True,
    "message": "Human-readable error description",
    "code": "ERROR_CODE",
    "details": {
        # Additional error context
    }
}
```

## Utility Functions

### src/utils.py

#### safe_float(value: Any, default: float = 0.0) -> float

Safely converts values to float with fallback.

#### format_currency(amount: float) -> str

Formats numbers as currency strings.

#### validate_parameters(params: dict) -> List[str]

Validates parameter dictionary, returns list of error messages.

## Performance Considerations

### Simulation Performance

- **Memory Usage**: ~8 bytes per simulation per parameter
- **CPU Usage**: O(n) with simulation count
- **Typical Runtime**: 1000 simulations in <1 second

### Excel Generation Performance

- **Memory Usage**: ~10-50MB for complex workbooks
- **File Size**: Typically 1-5MB for standard analysis
- **Generation Time**: 2-5 seconds for full workbook

### Optimization Tips

```python
# For faster testing
simulator = BuildVsBuySimulator(n_simulations=100)

# For production accuracy
simulator = BuildVsBuySimulator(n_simulations=10000)

# Memory-efficient large runs
import gc
results = simulator.simulate(params)
gc.collect()  # Force garbage collection
```

## Mathematical Formulas

### Present Value Calculation

**Labor PV (Year-by-year):**
```
PV = Σ(cost_year_i / (1 + WACC)^(year_i + 0.5))
```

**Subscription PV:**
```
PV = Σ(payment_i * (1 + escalation)^i / (1 + WACC)^i)
```

**Risk Adjustment:**
```
Risk_Multiplier = 1 + (tech_risk + vendor_risk + market_risk)
```

### Monte Carlo Implementation

```python
# Pseudo-code for simulation loop
for i in range(n_simulations):
    timeline_i = normal(timeline_mean, timeline_std)
    cost_i = normal(cost_mean, cost_std)
    total_cost_i = calculate_pv(timeline_i, cost_i, ...)
    results.append(total_cost_i)

return {
    'mean': np.mean(results),
    'p10': np.percentile(results, 10),
    'p50': np.percentile(results, 50),
    'p90': np.percentile(results, 90)
}
```

## Integration Examples

### Basic Usage

```python
from src.simulation import BuildVsBuySimulator
from core.excel_export import ExcelExporter

# Create simulator
sim = BuildVsBuySimulator(n_simulations=1000)

# Define parameters
params = {
    'build_timeline': 18,
    'fte_cost': 150000,
    'fte_count': 4,
    'useful_life': 5,
    'prob_success': 80,
    'wacc': 10,
    'product_price': 2000000
}

# Run simulation
results = sim.simulate(params)
print(f"Recommendation: {results['recommendation']}")

# Generate Excel
exporter = ExcelExporter()
excel_bytes = exporter.create_excel_export(params)
```

### Advanced Usage with Scenarios

```python
from data.scenario_manager import scenario_manager

# Save scenario
scenario_id = scenario_manager.save_scenario(
    params, 
    "High-Risk Scenario",
    "Conservative estimates with high risk factors"
)

# Load and compare
saved_scenario = scenario_manager.load_scenario(scenario_id)
comparison_results = sim.simulate(saved_scenario['parameters'])

# Export comparison
excel_bytes = exporter.create_excel_export(
    params, 
    stored_scenarios=[saved_scenario]
)
```

## Testing API

### Test Utilities

```python
def assert_simulation_valid(results: Dict):
    """Validate simulation results structure."""
    required_keys = [
        'expected_build_cost', 'buy_total_cost', 
        'recommendation', 'cost_distribution'
    ]
    for key in required_keys:
        assert key in results
    
    assert results['expected_build_cost'] > 0
    assert results['recommendation'] in ['Build', 'Buy']
    assert len(results['cost_distribution']) > 0
```

### Performance Testing

```python
import time

def test_simulation_performance():
    """Test simulation runs within acceptable time."""
    sim = BuildVsBuySimulator(n_simulations=1000)
    
    start_time = time.time()
    results = sim.simulate(test_params)
    elapsed = time.time() - start_time
    
    assert elapsed < 5.0  # Should complete within 5 seconds
```

This API documentation provides the foundation for extending and maintaining the Build vs Buy Decision Dashboard. For implementation details, refer to the source code and inline documentation.
