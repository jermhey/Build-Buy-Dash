#!/usr/bin/env python3
"""
Test the corrected Excel formula against simulation with multiple scenarios
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator
from core.excel_export import ExcelExporter

def test_corrected_excel_formula():
    """Test the corrected Excel formula with PV discounting."""
    print("🧪 TESTING CORRECTED EXCEL FORMULA")
    print("=" * 60)
    
    # User's exact parameters
    params = {
        'build_timeline': 10,
        'build_timeline_std': 2,
        'fte_cost': 175000,
        'fte_cost_std': 25000,
        'fte_count': 5,
        'cap_percent': 75,
        'useful_life': 5,
        'prob_success': 90,
        'wacc': 8,
        'tax_credit_rate': 17,
        'misc_costs': 200000,
        'capex': 100000,
        'maint_opex': 50000,
        'amortization': 150,
        'tech_risk': 7,
        'vendor_risk': 9,
        'market_risk': 8,
        'product_price': 1000000,
        'subscription_price': 250000,
        'subscription_increase': 3,
        'buy_selector': ['one_time', 'subscription']
    }
    
    # Run simulation
    simulator = BuildVsBuySimulator(n_simulations=10000, random_seed=42)
    results = simulator.simulate(params)
    
    print(f"Simulation Result: ${results['expected_build_cost']:,.0f}")
    
    # Create Excel export with updated formula
    scenario_data = params.copy()
    scenario_data['results'] = results
    exporter = ExcelExporter()
    excel_bytes = exporter.create_excel_export(scenario_data)
    
    # Save Excel for inspection
    excel_path = "corrected_formula_test.xlsx"
    with open(excel_path, 'wb') as f:
        f.write(excel_bytes)
    
    print(f"Excel export created: {len(excel_bytes)} bytes")
    print(f"Saved to: {excel_path}")
    
    # Manual calculation with corrected formula
    timeline = params['build_timeline']
    fte_cost = params['fte_cost']
    fte_count = params['fte_count']
    prob_success = params['prob_success'] / 100
    wacc = params['wacc'] / 100
    cap_percent = params['cap_percent'] / 100
    tax_credit_rate = params['tax_credit_rate'] / 100
    
    # NEW corrected Excel formula
    total_fte_pv = (((timeline/12) * fte_cost * fte_count) / prob_success) / ((1 + wacc) ** (timeline/12))
    
    print(f"\nCorrected Excel Calculation:")
    print(f"Total FTE (PV): ${total_fte_pv:,.0f}")
    
    # Calculate other components
    capitalized_labor = total_fte_pv * cap_percent
    expensed_labor = total_fte_pv - capitalized_labor
    tax_credit = capitalized_labor * tax_credit_rate
    
    # Other costs
    misc_costs = params['misc_costs']
    capex = params['capex']
    
    # Maintenance PV
    useful_life = params['useful_life']
    maint_pv = sum(params['maint_opex'] / (1 + wacc) ** year for year in range(1, useful_life + 1))
    
    # Amortization PV
    monthly_rate = (1 + wacc) ** (1/12) - 1
    amort_pv = sum(params['amortization'] / (1 + monthly_rate) ** month for month in range(1, timeline + 1))
    
    # Base total
    base_total = expensed_labor + capitalized_labor + misc_costs + capex + maint_pv + amort_pv - tax_credit
    
    # Apply risk factors
    tech_risk = params['tech_risk'] / 100
    vendor_risk = params['vendor_risk'] / 100
    market_risk = params['market_risk'] / 100
    risk_multiplier = (1 + tech_risk) * (1 + vendor_risk) * (1 + market_risk)
    
    excel_final = base_total * risk_multiplier
    
    print(f"Excel Final Result: ${excel_final:,.0f}")
    print(f"Difference: ${excel_final - results['expected_build_cost']:,.0f}")
    
    percentage_diff = abs(excel_final - results['expected_build_cost']) / results['expected_build_cost'] * 100
    print(f"Percentage Difference: {percentage_diff:.2f}%")
    
    if percentage_diff < 5:
        print("✅ SUCCESS: Within 5% tolerance!")
    elif percentage_diff < 10:
        print("⚠️  IMPROVED: Within 10% tolerance (much better than before)")
    else:
        print("❌ Still needs work")
    
    # Test with deterministic case (no uncertainty)
    print(f"\n" + "="*60)
    print("DETERMINISTIC TEST (No Uncertainty)")
    print("="*60)
    
    deterministic_params = params.copy()
    deterministic_params.update({
        'build_timeline_std': 0,
        'fte_cost_std': 0
    })
    
    det_results = simulator.simulate(deterministic_params)
    det_difference = abs(excel_final - det_results['expected_build_cost'])
    det_percentage = det_difference / det_results['expected_build_cost'] * 100
    
    print(f"Deterministic Simulation: ${det_results['expected_build_cost']:,.0f}")
    print(f"Excel (same): ${excel_final:,.0f}")
    print(f"Deterministic Difference: ${det_difference:,.0f} ({det_percentage:.2f}%)")
    
    return percentage_diff < 5

if __name__ == "__main__":
    test_corrected_excel_formula()
