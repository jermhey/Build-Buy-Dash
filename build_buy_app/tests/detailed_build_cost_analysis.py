#!/usr/bin/env python3
"""
Detailed analysis of build cost calculation differences between Excel and simulation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator
import numpy as np

def detailed_build_cost_analysis():
    """Detailed breakdown of build cost calculations."""
    print("🔍 DETAILED BUILD COST ANALYSIS")
    print("=" * 60)
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    
    # Use the complex parameters that showed discrepancy
    params = {
        'build_timeline': 18,
        'build_timeline_std': 0,
        'fte_cost': 150000,
        'fte_cost_std': 0,
        'fte_count': 3,
        'useful_life': 5,
        'prob_success': 80,  # This is the key parameter
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
    
    results = simulator.simulate(params)
    
    print(f"Simulation Build Cost: ${results['expected_build_cost']:,.2f}")
    print(f"Simulation Buy Cost: ${results['buy_total_cost']:,.2f}")
    
    # Let's manually recreate the simulation logic step by step
    print("\n" + "="*60)
    print("MANUAL SIMULATION RECREATION")
    print("="*60)
    
    # 1. Extract parameters like the simulator does
    timeline_years = 18 / 12  # 1.5 years
    fte_cost = 150000
    fte_count = 3
    prob_success = 80 / 100  # Convert to decimal
    wacc = 12 / 100  # Convert to decimal
    
    print(f"Timeline (years): {timeline_years}")
    print(f"FTE cost: ${fte_cost:,.0f}")
    print(f"FTE count: {fte_count}")
    print(f"Success probability: {prob_success}")
    print(f"WACC: {wacc}")
    
    # 2. Calculate base labor cost
    base_labor = timeline_years * fte_cost * fte_count
    print(f"\nBase labor cost: ${base_labor:,.2f}")
    
    # 3. Apply success probability adjustment (this might be the issue)
    # In simulation, costs are divided by success probability
    labor_adjusted = base_labor / prob_success
    print(f"Labor cost adjusted for success probability: ${labor_adjusted:,.2f}")
    
    # 4. Apply present value discounting
    labor_pv = labor_adjusted / ((1 + wacc) ** timeline_years)
    print(f"Labor cost PV: ${labor_pv:,.2f}")
    
    # 5. Add other costs
    # CapEx (immediate)
    capex = 50000
    print(f"CapEx: ${capex:,.2f}")
    
    # Amortization PV (monthly during build)
    monthly_rate = (1 + wacc) ** (1/12) - 1
    months = 18
    amort_monthly = 3000
    amort_pv = sum(amort_monthly / (1 + monthly_rate) ** month for month in range(1, months + 1))
    print(f"Amortization PV: ${amort_pv:,.2f}")
    
    # OpEx PV (annual during useful life)
    opex_annual = 15000
    useful_life = 5
    opex_pv = sum(opex_annual / (1 + wacc) ** year for year in range(1, useful_life + 1))
    print(f"OpEx PV: ${opex_pv:,.2f}")
    
    # Misc costs (immediate)
    misc = 25000
    print(f"Misc costs: ${misc:,.2f}")
    
    # 6. Total before risk adjustment
    total_before_risk = labor_pv + capex + amort_pv + opex_pv + misc
    print(f"\nTotal before risk adjustment: ${total_before_risk:,.2f}")
    
    # 7. Apply risk factors
    tech_risk = 15 / 100
    vendor_risk = 10 / 100
    market_risk = 5 / 100
    
    # Risk factors are multiplicative: (1 + risk1) * (1 + risk2) * (1 + risk3)
    risk_multiplier = (1 + tech_risk) * (1 + vendor_risk) * (1 + market_risk)
    print(f"Risk multiplier: {risk_multiplier:.4f}")
    
    final_cost = total_before_risk * risk_multiplier
    print(f"Final cost after risk adjustment: ${final_cost:,.2f}")
    
    # Compare with simulation
    difference = abs(final_cost - results['expected_build_cost'])
    print(f"\nDifference from simulation: ${difference:,.2f}")
    print(f"Percentage difference: {(difference / results['expected_build_cost']) * 100:.2f}%")
    
    # Let's also test what happens if we don't apply success probability
    print("\n" + "="*60)
    print("WITHOUT SUCCESS PROBABILITY ADJUSTMENT")
    print("="*60)
    
    # Without success probability adjustment
    labor_no_success = base_labor / ((1 + wacc) ** timeline_years)
    total_no_success = labor_no_success + capex + amort_pv + opex_pv + misc
    final_no_success = total_no_success * risk_multiplier
    
    print(f"Labor PV (no success adjustment): ${labor_no_success:,.2f}")
    print(f"Final cost (no success adjustment): ${final_no_success:,.2f}")
    
    # Test with Excel-style calculation (might not apply success probability to all costs)
    print("\n" + "="*60)
    print("EXCEL-STYLE CALCULATION")
    print("="*60)
    
    # In Excel, success probability might only apply to labor
    labor_excel = (base_labor / prob_success) / ((1 + wacc) ** timeline_years)
    other_costs = capex + amort_pv + opex_pv + misc
    total_excel = labor_excel + other_costs
    final_excel = total_excel * risk_multiplier
    
    print(f"Labor cost (Excel style): ${labor_excel:,.2f}")
    print(f"Other costs: ${other_costs:,.2f}")
    print(f"Total (Excel style): ${total_excel:,.2f}")
    print(f"Final with risk (Excel style): ${final_excel:,.2f}")
    
    excel_diff = abs(final_excel - results['expected_build_cost'])
    print(f"Difference from simulation: ${excel_diff:,.2f}")

if __name__ == "__main__":
    detailed_build_cost_analysis()
