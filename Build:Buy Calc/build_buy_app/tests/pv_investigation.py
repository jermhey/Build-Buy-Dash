#!/usr/bin/env python3
"""
Detailed investigation of present value calculations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import BuildVsBuySimulator

def investigate_pv_calculations():
    """Investigate present value calculation details."""
    print("🔍 DETAILED PRESENT VALUE INVESTIGATION")
    print("=" * 60)
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    
    # Parameters with additional costs
    params = {
        'build_timeline': 12,
        'build_timeline_std': 0,
        'fte_cost': 120000,
        'fte_cost_std': 0,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 100,
        'wacc': 10,
        'product_price': 300000,
        'buy_selector': ['one_time'],
        'misc_costs': 0,
        'capex': 50000,             # $50k upfront
        'amortization': 5000,       # $5k/month during build
        'maint_opex': 20000,        # $20k/year maintenance
        'maint_opex_std': 0,
        'tech_risk': 0,
        'vendor_risk': 0,
        'market_risk': 0
    }
    
    # Base case (no extra costs)
    base_params = params.copy()
    base_params.update({'capex': 0, 'amortization': 0, 'maint_opex': 0})
    
    results_base = simulator.simulate(base_params)
    results_full = simulator.simulate(params)
    
    print(f"Base case cost: ${results_base['expected_build_cost']:,.2f}")
    print(f"Full case cost: ${results_full['expected_build_cost']:,.2f}")
    print(f"Difference: ${results_full['expected_build_cost'] - results_base['expected_build_cost']:,.2f}")
    
    # Manual calculations
    print("\nManual calculations:")
    
    # CapEx (immediate)
    print(f"CapEx: ${50000:,.2f}")
    
    # OpEx PV (5 years at 10%)
    manual_opex_pv = sum(20000 / (1.1 ** year) for year in range(1, 6))
    print(f"OpEx PV: ${manual_opex_pv:,.2f}")
    
    # Amortization PV (12 months)
    monthly_rate = (1 + 0.1) ** (1/12) - 1
    manual_amort_pv = sum(5000 / (1 + monthly_rate) ** month for month in range(1, 13))
    print(f"Amortization PV: ${manual_amort_pv:,.2f}")
    
    print(f"Total manual additional costs: ${50000 + manual_opex_pv + manual_amort_pv:,.2f}")
    
    # Let's test each component individually
    print("\nComponent testing:")
    
    # Test CapEx only
    capex_only = base_params.copy()
    capex_only['capex'] = 50000
    results_capex = simulator.simulate(capex_only)
    capex_diff = results_capex['expected_build_cost'] - results_base['expected_build_cost']
    print(f"CapEx effect: ${capex_diff:,.2f} (expected: $50,000)")
    
    # Test OpEx only
    opex_only = base_params.copy()
    opex_only['maint_opex'] = 20000
    results_opex = simulator.simulate(opex_only)
    opex_diff = results_opex['expected_build_cost'] - results_base['expected_build_cost']
    print(f"OpEx effect: ${opex_diff:,.2f} (expected: ${manual_opex_pv:,.2f})")
    
    # Test Amortization only
    amort_only = base_params.copy()
    amort_only['amortization'] = 5000
    results_amort = simulator.simulate(amort_only)
    amort_diff = results_amort['expected_build_cost'] - results_base['expected_build_cost']
    print(f"Amortization effect: ${amort_diff:,.2f} (expected: ${manual_amort_pv:,.2f})")
    
    # Check if there's any discounting effect on the overall cost
    print(f"\nTotal components: ${capex_diff + opex_diff + amort_diff:,.2f}")
    print(f"Actual difference: ${results_full['expected_build_cost'] - results_base['expected_build_cost']:,.2f}")

if __name__ == "__main__":
    investigate_pv_calculations()
