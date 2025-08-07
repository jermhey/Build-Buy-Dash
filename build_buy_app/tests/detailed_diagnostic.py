#!/usr/bin/env python3
"""
Detailed diagnostic tool to compare Excel vs Simulation calculations step by step
This will help identify exactly where the discrepancy occurs
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator
from core.excel_export import ExcelExporter
import numpy as np

def detailed_diagnostic():
    """
    Detailed step-by-step comparison of Excel vs Simulation calculations.
    Uses the exact parameters from the user's example.
    """
    print("🔬 DETAILED EXCEL vs SIMULATION DIAGNOSTIC")
    print("=" * 70)
    
    # Exact parameters from user's input
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
    
    print("USER'S PARAMETERS:")
    print("-" * 30)
    for key, value in params.items():
        if key.endswith('_std'):
            continue
        if isinstance(value, (int, float)):
            if key in ['prob_success', 'wacc', 'cap_percent', 'tax_credit_rate', 'tech_risk', 'vendor_risk', 'market_risk', 'subscription_increase']:
                print(f"{key}: {value}%")
            elif key in ['fte_cost', 'misc_costs', 'capex', 'maint_opex', 'product_price', 'subscription_price']:
                print(f"{key}: ${value:,}")
            else:
                print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")
    
    # Run simulation
    simulator = BuildVsBuySimulator(n_simulations=10000, random_seed=42)
    results = simulator.simulate(params)
    
    print(f"\nSIMULATION RESULT: ${results['expected_build_cost']:,.0f}")
    print(f"User reported difference: -$75,725")
    print(f"User's expected Excel result: ${results['expected_build_cost'] + 75725:,.0f}")
    
    # Step-by-step Excel calculation recreation
    print("\n" + "=" * 70)
    print("STEP-BY-STEP EXCEL CALCULATION RECREATION")
    print("=" * 70)
    
    # Convert percentages to decimals for calculations
    prob_success = params['prob_success'] / 100  # 0.9
    cap_percent = params['cap_percent'] / 100    # 0.75
    tax_credit_rate = params['tax_credit_rate'] / 100  # 0.17
    wacc = params['wacc'] / 100                  # 0.08
    tech_risk = params['tech_risk'] / 100        # 0.07
    vendor_risk = params['vendor_risk'] / 100    # 0.09
    market_risk = params['market_risk'] / 100    # 0.08
    
    print("\nSTEP 1: FTE COST CALCULATIONS")
    print("-" * 40)
    
    # Excel FTE formula: =((timeline/12)*fte_cost*fte_count)/prob_success
    timeline_years = params['build_timeline'] / 12  # 10/12 = 0.833 years
    base_fte_cost = timeline_years * params['fte_cost'] * params['fte_count']
    total_fte_cost = base_fte_cost / prob_success
    
    print(f"Timeline (years): {timeline_years:.3f}")
    print(f"Base FTE Cost: {timeline_years:.3f} * ${params['fte_cost']:,} * {params['fte_count']} = ${base_fte_cost:,.0f}")
    print(f"Success-adjusted FTE: ${base_fte_cost:,.0f} / {prob_success} = ${total_fte_cost:,.0f}")
    
    # Labor breakdown
    capitalized_labor = total_fte_cost * cap_percent
    expensed_labor = total_fte_cost - capitalized_labor
    tax_credit = capitalized_labor * tax_credit_rate
    
    print(f"\nCapitalized Labor: ${total_fte_cost:,.0f} * {cap_percent} = ${capitalized_labor:,.0f}")
    print(f"Expensed Labor: ${total_fte_cost:,.0f} - ${capitalized_labor:,.0f} = ${expensed_labor:,.0f}")
    print(f"Tax Credit: ${capitalized_labor:,.0f} * {tax_credit_rate} = ${tax_credit:,.0f}")
    
    print(f"\nUser's Excel shows:")
    print(f"  Total FTE Costs: $810,185 (vs our calc: ${total_fte_cost:,.0f})")
    print(f"  Capitalized Labor: $607,639 (vs our calc: ${capitalized_labor:,.0f})")
    print(f"  Tax Credit: $103,299 (vs our calc: ${tax_credit:,.0f})")
    
    # Check if there's a discrepancy in FTE calculation
    user_total_fte = 810185
    user_capitalized = 607639
    user_tax_credit = 103299
    
    fte_diff = abs(total_fte_cost - user_total_fte)
    if fte_diff > 1000:
        print(f"⚠️  MAJOR FTE DISCREPANCY: ${fte_diff:,.0f}")
        # Try to reverse-engineer what Excel might be doing
        implied_timeline = user_total_fte * prob_success / (params['fte_cost'] * params['fte_count']) * 12
        print(f"   Implied timeline from Excel: {implied_timeline:.2f} months")
    
    print("\nSTEP 2: OTHER COST COMPONENTS")
    print("-" * 40)
    
    # Amortization PV calculation
    monthly_rate = (1 + wacc) ** (1/12) - 1
    amort_months = params['build_timeline']  # 10 months
    amort_pv = sum(params['amortization'] / (1 + monthly_rate) ** month for month in range(1, amort_months + 1))
    
    print(f"Amortization PV: ${params['amortization']} * {amort_months} months = ${amort_pv:,.0f}")
    
    # Maintenance OpEx PV (starts Year 1)
    maint_pv = sum(params['maint_opex'] / (1 + wacc) ** year for year in range(1, params['useful_life'] + 1))
    print(f"Maintenance OpEx PV: ${maint_pv:,.0f}")
    
    # Immediate costs
    misc_costs = params['misc_costs']
    capex = params['capex']
    print(f"Misc Costs: ${misc_costs:,.0f}")
    print(f"CapEx: ${capex:,.0f}")
    
    print("\nSTEP 3: BASE BUILD TOTAL (PRE-RISK)")
    print("-" * 40)
    
    base_build_total = expensed_labor + capitalized_labor + misc_costs + capex + maint_pv + amort_pv - tax_credit
    print(f"Base Total: ${expensed_labor:,.0f} + ${capitalized_labor:,.0f} + ${misc_costs:,.0f} + ${capex:,.0f} + ${maint_pv:,.0f} + ${amort_pv:,.0f} - ${tax_credit:,.0f}")
    print(f"Base Build Total: ${base_build_total:,.0f}")
    
    print("\nSTEP 4: RISK FACTOR APPLICATION")
    print("-" * 40)
    
    risk_multiplier = (1 + tech_risk) * (1 + vendor_risk) * (1 + market_risk)
    print(f"Risk Multiplier: (1+{tech_risk}) * (1+{vendor_risk}) * (1+{market_risk}) = {risk_multiplier:.6f}")
    
    excel_risk_adjusted = base_build_total * risk_multiplier
    print(f"Excel Risk-Adjusted Total: ${base_build_total:,.0f} * {risk_multiplier:.6f} = ${excel_risk_adjusted:,.0f}")
    
    print("\nSTEP 5: SIMULATION DEEP DIVE")
    print("-" * 40)
    
    # Let's manually recreate key simulation steps
    print("Recreating simulation logic...")
    
    # Simulation uses uncertainty - let's check deterministic case
    sim_timeline_years = params['build_timeline'] / 12
    sim_base_labor = sim_timeline_years * params['fte_cost'] * params['fte_count']
    sim_labor_adjusted = sim_base_labor / prob_success
    
    # Simulation applies present value discounting to labor during build period
    sim_labor_pv = sim_labor_adjusted / ((1 + wacc) ** sim_timeline_years)
    
    print(f"Simulation labor PV: ${sim_labor_pv:,.0f}")
    
    # Add other costs (simulation method)
    sim_total_before_risk = sim_labor_pv + misc_costs + capex + maint_pv + amort_pv
    
    # Apply risk factors
    sim_risk_adjusted = sim_total_before_risk * risk_multiplier
    
    print(f"Simulation risk-adjusted: ${sim_risk_adjusted:,.0f}")
    print(f"Actual simulation result: ${results['expected_build_cost']:,.0f}")
    
    print("\nSTEP 6: COMPARISON SUMMARY")
    print("-" * 40)
    
    print(f"Excel calculation (our recreation): ${excel_risk_adjusted:,.0f}")
    print(f"Simulation result: ${results['expected_build_cost']:,.0f}")
    print(f"Difference: ${excel_risk_adjusted - results['expected_build_cost']:,.0f}")
    print(f"User reported difference: -$75,725")
    
    # Key insight: Check if labor PV discounting is the issue
    labor_pv_diff = sim_labor_pv - (expensed_labor + capitalized_labor)
    print(f"\nKey insight - Labor PV difference: ${labor_pv_diff:,.0f}")
    print("This suggests Excel may not be applying PV discounting to labor costs during build period")
    
    return {
        'excel_estimate': excel_risk_adjusted,
        'simulation_result': results['expected_build_cost'],
        'difference': excel_risk_adjusted - results['expected_build_cost'],
        'user_fte_total': user_total_fte,
        'calc_fte_total': total_fte_cost
    }

if __name__ == "__main__":
    detailed_diagnostic()
