#!/usr/bin/env python3
"""
Test Excel export with known parameters to verify calculations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator
from core.excel_export import ExcelExporter

def test_excel_export_calculations():
    """Test Excel export with specific parameters."""
    print("🧪 TESTING EXCEL EXPORT CALCULATIONS")
    print("=" * 60)
    
    # Use the exact parameters from our detailed analysis
    params = {
        'build_timeline': 18,
        'build_timeline_std': 0,
        'fte_cost': 150000,
        'fte_cost_std': 0,
        'fte_count': 3,
        'useful_life': 5,
        'prob_success': 80,  # This should be converted to 0.8 in Excel
        'wacc': 12,
        'product_price': 500000,
        'buy_selector': ['one_time'],
        'misc_costs': 25000,
        'capex': 50000,
        'amortization': 3000,
        'maint_opex': 15000,
        'tech_risk': 15,
        'vendor_risk': 10,
        'market_risk': 5
    }
    
    # Run simulation
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    results = simulator.simulate(params)
    
    print(f"Simulation Build Cost: ${results['expected_build_cost']:,.2f}")
    print(f"Simulation Buy Cost: ${results['buy_total_cost']:,.2f}")
    
    # Create scenario data with results for Excel export
    scenario_data = params.copy()
    scenario_data['results'] = results
    
    # Create Excel export
    exporter = ExcelExporter()
    excel_bytes = exporter.create_excel_export(scenario_data)
    
    print(f"Excel export created: {len(excel_bytes)} bytes")
    
    # Test what the Excel formulas would calculate manually
    print("\n" + "="*60)
    print("MANUAL EXCEL FORMULA CALCULATION")
    print("="*60)
    
    # Parameters as they would appear in Excel (after conversion)
    timeline_months = 18
    fte_cost = 150000
    fte_count = 3
    prob_success = 0.8  # Converted from 80% to decimal in Excel
    wacc = 0.12  # Converted from 12% to decimal in Excel
    
    # Excel FTE formula: =(timeline/12)*fte_cost*fte_count)/prob_success
    excel_fte_nominal = (timeline_months/12) * fte_cost * fte_count / prob_success
    print(f"Excel FTE calculation (nominal): ${excel_fte_nominal:,.2f}")
    
    # Present value: FTE_nominal / (1+WACC)^timeline_years
    timeline_years = timeline_months / 12
    excel_fte_pv = excel_fte_nominal / ((1 + wacc) ** timeline_years)
    print(f"Excel FTE PV: ${excel_fte_pv:,.2f}")
    
    # Other costs (as they would be calculated in Excel)
    capex = 50000  # Immediate
    misc = 25000   # Immediate
    
    # Amortization PV (monthly)
    monthly_rate = (1 + wacc) ** (1/12) - 1
    amort_pv = sum(3000 / (1 + monthly_rate) ** month for month in range(1, 19))
    print(f"Excel Amortization PV: ${amort_pv:,.2f}")
    
    # OpEx PV (annual for 5 years)
    opex_pv = sum(15000 / (1 + wacc) ** year for year in range(1, 6))
    print(f"Excel OpEx PV: ${opex_pv:,.2f}")
    
    # Total before risk
    excel_total_before_risk = excel_fte_pv + capex + misc + amort_pv + opex_pv
    print(f"Excel total before risk: ${excel_total_before_risk:,.2f}")
    
    # Risk factors (1 + 15%) * (1 + 10%) * (1 + 5%)
    risk_multiplier = 1.15 * 1.10 * 1.05
    excel_final = excel_total_before_risk * risk_multiplier
    print(f"Excel final cost (with risk): ${excel_final:,.2f}")
    
    # Compare with simulation
    difference = abs(excel_final - results['expected_build_cost'])
    print(f"\nDifference from simulation: ${difference:,.2f}")
    print(f"Percentage difference: {(difference / results['expected_build_cost']) * 100:.2f}%")
    
    if difference < 1000:  # Within $1000
        print("✅ Excel and simulation calculations match closely!")
    else:
        print("❌ Significant difference found - needs investigation")

if __name__ == "__main__":
    test_excel_export_calculations()
