#!/usr/bin/env python3
"""
Test to identify exact Excel vs Simulation discrepancy
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator
import numpy as np

def test_excel_simulation_discrepancy():
    """Test to find the exact discrepancy between Excel and simulation."""
    print("🔍 EXCEL vs SIMULATION DISCREPANCY ANALYSIS")
    print("=" * 60)
    
    # Use deterministic parameters to make comparison easier
    params = {
        'build_timeline': 12,
        'build_timeline_std': 0,  # No uncertainty
        'fte_cost': 120000,
        'fte_cost_std': 0,  # No uncertainty  
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 100,  # No failure risk
        'wacc': 10,
        'product_price': 300000,
        'buy_selector': ['one_time'],
        'misc_costs': 0,
        'capex': 0,
        'amortization': 0,
        'maint_opex': 0,
        'tech_risk': 0,
        'vendor_risk': 0,
        'market_risk': 0
    }
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    results = simulator.simulate(params)
    
    print(f"Simulation Expected Build Cost: ${results['expected_build_cost']:,.2f}")
    print(f"Simulation Buy Cost: ${results['buy_total_cost']:,.2f}")
    
    # Manual calculation following Excel logic (simple)
    print("\nSimple Excel-style calculation:")
    timeline_years = 12 / 12  # 1 year
    labor_cost_nominal = timeline_years * 120000 * 2  # $240,000
    print(f"Labor cost (nominal): ${labor_cost_nominal:,.2f}")
    
    # Simple PV discount
    labor_cost_pv_simple = labor_cost_nominal / (1 + 0.1) ** timeline_years  
    print(f"Labor cost PV (simple): ${labor_cost_pv_simple:,.2f}")
    
    # Manual calculation following simulation logic (sophisticated)
    print("\nSimulation-style calculation:")
    # Timeline in years
    timeline_years = 12 / 12
    # Labor cost with success probability adjustment
    labor_cost_adjusted = labor_cost_nominal / (100/100)  # No adjustment since prob_success = 100%
    print(f"Labor cost (success adjusted): ${labor_cost_adjusted:,.2f}")
    
    # Sophisticated PV discount (during build period)
    discount_factor = (1 + 0.1) ** timeline_years
    labor_cost_pv_simulation = labor_cost_adjusted / discount_factor
    print(f"Labor cost PV (simulation method): ${labor_cost_pv_simulation:,.2f}")
    
    print(f"\nDifference between methods: ${abs(labor_cost_pv_simple - labor_cost_pv_simulation):,.2f}")
    print(f"Difference vs simulation: ${abs(results['expected_build_cost'] - labor_cost_pv_simulation):,.2f}")
    
    # Test with more complex parameters
    print("\n" + "="*60)
    print("COMPLEX SCENARIO TEST")
    
    complex_params = {
        'build_timeline': 18,
        'build_timeline_std': 0,
        'fte_cost': 150000,
        'fte_cost_std': 0,
        'fte_count': 3,
        'useful_life': 5,
        'prob_success': 80,  # 80% success probability
        'wacc': 12,
        'product_price': 500000,
        'buy_selector': ['one_time'],
        'misc_costs': 25000,  # $25k misc
        'capex': 50000,       # $50k CapEx
        'amortization': 3000, # $3k/month
        'maint_opex': 15000,  # $15k/year maintenance
        'tech_risk': 15,      # 15% risk
        'vendor_risk': 10,    # 10% risk
        'market_risk': 5      # 5% risk
    }
    
    complex_results = simulator.simulate(complex_params)
    
    print(f"Complex Simulation Build Cost: ${complex_results['expected_build_cost']:,.2f}")
    print(f"Complex Simulation Buy Cost: ${complex_results['buy_total_cost']:,.2f}")
    
    # Break down the complex calculation
    print("\nComplex manual breakdown:")
    
    # 1. Labor cost
    timeline_years = 18 / 12  # 1.5 years
    base_labor = (18/12) * 150000 * 3  # $675,000
    adjusted_labor = base_labor / (80/100)  # Adjust for success probability = $843,750
    labor_pv = adjusted_labor / ((1 + 0.12) ** timeline_years)  # PV = $708,333
    print(f"1. Labor PV: ${labor_pv:,.2f}")
    
    # 2. CapEx (immediate)
    capex_pv = 50000
    print(f"2. CapEx PV: ${capex_pv:,.2f}")
    
    # 3. Amortization PV (monthly over 18 months)
    monthly_rate = (1.12) ** (1/12) - 1  # ~0.949%
    amort_pv = sum(3000 / ((1 + monthly_rate) ** month) for month in range(1, 19))
    print(f"3. Amortization PV: ${amort_pv:,.2f}")
    
    # 4. OpEx PV (annual over 5 years)
    opex_pv = sum(15000 / ((1.12) ** year) for year in range(1, 6))
    print(f"4. OpEx PV: ${opex_pv:,.2f}")
    
    # 5. Misc costs (immediate)
    misc_pv = 25000
    print(f"5. Misc PV: ${misc_pv:,.2f}")
    
    # 6. Risk factors
    base_total = labor_pv + capex_pv + amort_pv + opex_pv + misc_pv
    total_risk_factor = 1 + (15 + 10 + 5) / 100  # 30% total risk
    risk_adjusted_total = base_total * total_risk_factor
    print(f"6. Base total: ${base_total:,.2f}")
    print(f"7. Risk factor: {total_risk_factor:.2f}")
    print(f"8. Risk adjusted total: ${risk_adjusted_total:,.2f}")
    
    print(f"\nManual vs Simulation difference: ${abs(risk_adjusted_total - complex_results['expected_build_cost']):,.2f}")

if __name__ == "__main__":
    test_excel_simulation_discrepancy()
