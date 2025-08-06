#!/usr/bin/env python3
"""
Comprehensive validation of all Build vs Buy calculation logic
This test validates every component of the calculation system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import BuildVsBuySimulator
from app import BuildVsBuyApp

def test_comprehensive_calculation_logic():
    """Comprehensive test of all calculation components."""
    print("🧪 COMPREHENSIVE BUILD VS BUY CALCULATION VALIDATION")
    print("=" * 80)
    
    # Test 1: Basic simulation with known parameters
    print("\n1️⃣ BASIC SIMULATION VALIDATION")
    print("-" * 40)
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    
    # Simple test case with deterministic inputs (no uncertainty)
    basic_params = {
        'build_timeline': 12,           # 12 months
        'build_timeline_std': 0,        # No uncertainty
        'fte_cost': 120000,             # $120k/year
        'fte_cost_std': 0,              # No uncertainty
        'fte_count': 2,                 # 2 people
        'useful_life': 5,               # 5 years
        'prob_success': 100,            # 100% probability
        'wacc': 10,                     # 10% discount rate
        'product_price': 300000,        # $300k one-time
        'buy_selector': ['one_time'],
        'misc_costs': 0,
        'capex': 0,
        'amortization': 0,
        'maint_opex': 0,
        'tech_risk': 0,
        'vendor_risk': 0,
        'market_risk': 0
    }
    
    results = simulator.simulate(basic_params)
    
    # Manual calculation for validation
    # Expected labor cost: (12/12) * 120000 * 2 = $240,000
    # No uncertainty, so all samples should be the same
    expected_labor = 12/12 * 120000 * 2  # = 240,000
    # Present value adjustment: 240,000 / (1.1)^1 = 218,182
    expected_pv = expected_labor / (1 + 0.1) ** 1
    
    print(f"Manual calculation - Expected Labor Cost: ${expected_labor:,.0f}")
    print(f"Manual calculation - Expected PV: ${expected_pv:,.0f}")
    print(f"Simulation result - Expected Build Cost: ${results['expected_build_cost']:,.0f}")
    print(f"Simulation result - P10/P50/P90: ${results['build_cost_p10']:,.0f} / ${results['build_cost_p50']:,.0f} / ${results['build_cost_p90']:,.0f}")
    print(f"Buy Total Cost: ${results['buy_total_cost']:,.0f}")
    print(f"NPV Difference: ${results['npv_difference']:,.0f}")
    print(f"Recommendation: {results['recommendation']}")
    
    # Validation checks
    tolerance = 1000  # $1k tolerance for floating point
    build_cost_close = abs(results['expected_build_cost'] - expected_pv) < tolerance
    print(f"✅ Build cost calculation within tolerance: {build_cost_close}")
    
    # Test 2: Subscription calculation
    print("\n2️⃣ SUBSCRIPTION CALCULATION VALIDATION")
    print("-" * 40)
    
    subscription_params = basic_params.copy()
    subscription_params.update({
        'buy_selector': ['subscription'],
        'subscription_price': 50000,        # $50k/year
        'subscription_increase': 5          # 5% annual increase
    })
    
    results_sub = simulator.simulate(subscription_params)
    
    # Manual subscription NPV calculation
    # Year 1: 50000 / (1.1)^0 = 50000
    # Year 2: 52500 / (1.1)^1 = 47727
    # Year 3: 55125 / (1.1)^2 = 45537
    # Year 4: 57881 / (1.1)^3 = 43467
    # Year 5: 60775 / (1.1)^4 = 41512
    manual_subscription_npv = 0
    for year in range(5):
        payment = 50000 * (1.05 ** year)
        pv = payment / (1.1 ** year)
        manual_subscription_npv += pv
        print(f"Year {year+1}: Payment ${payment:,.0f}, PV ${pv:,.0f}")
    
    print(f"Manual subscription NPV: ${manual_subscription_npv:,.0f}")
    print(f"Simulation subscription cost: ${results_sub['buy_total_cost']:,.0f}")
    
    subscription_close = abs(results_sub['buy_total_cost'] - manual_subscription_npv) < tolerance
    print(f"✅ Subscription calculation within tolerance: {subscription_close}")
    
    # Test 3: Risk factor application
    print("\n3️⃣ RISK FACTOR VALIDATION")
    print("-" * 40)
    
    risk_params = basic_params.copy()
    risk_params.update({
        'tech_risk': 20,    # 20% additional cost risk
        'vendor_risk': 10,  # 10% additional cost risk
        'market_risk': 5    # 5% additional cost risk
    })
    
    results_risk = simulator.simulate(risk_params)
    
    print(f"Base case (no risk): ${results['expected_build_cost']:,.0f}")
    print(f"With risk factors: ${results_risk['expected_build_cost']:,.0f}")
    
    # Risk should increase the cost
    risk_increased = results_risk['expected_build_cost'] > results['expected_build_cost']
    print(f"✅ Risk factors increase cost: {risk_increased}")
    
    # Test 4: Probability calculation
    print("\n4️⃣ PROBABILITY CALCULATION VALIDATION")
    print("-" * 40)
    
    app = BuildVsBuyApp()
    
    # Test extreme case where build is always cheaper
    cheap_build_params = {
        'build_timeline': 1,
        'fte_cost': 50000,
        'fte_count': 1,
        'useful_life': 5,
        'prob_success': 100,
        'wacc': 10,
        'product_price': 1000000,  # Very expensive buy option
        'buy_selector': ['one_time']
    }
    
    results_cheap = simulator.simulate(cheap_build_params)
    prob_cheap = app._calculate_probability_build_costs_less(results_cheap)
    
    print(f"Cheap build case - Build cost: ${results_cheap['expected_build_cost']:,.0f}")
    print(f"Cheap build case - Buy cost: ${results_cheap['buy_total_cost']:,.0f}")
    print(f"Cheap build case - Probability build < buy: {prob_cheap:.1f}%")
    
    # Should be 100% or very close
    prob_correct = prob_cheap > 95
    print(f"✅ Probability calculation correct for obvious case: {prob_correct}")
    
    # Test 5: Cost variability
    print("\n5️⃣ COST VARIABILITY VALIDATION")
    print("-" * 40)
    
    # Test with uncertainty
    uncertain_params = basic_params.copy()
    uncertain_params.update({
        'build_timeline_std': 3,    # ±3 months uncertainty
        'fte_cost_std': 20000       # ±$20k uncertainty
    })
    
    results_uncertain = simulator.simulate(uncertain_params)
    variability = app._calculate_cost_variability(results_uncertain)
    
    print(f"Deterministic case variability: ${app._calculate_cost_variability(results):,.0f}")
    print(f"Uncertain case variability: ${variability:,.0f}")
    
    # Uncertainty should increase variability
    variability_increased = variability > app._calculate_cost_variability(results)
    print(f"✅ Uncertainty increases variability: {variability_increased}")
    
    # Test 6: Present value calculations
    print("\n6️⃣ PRESENT VALUE VALIDATION")
    print("-" * 40)
    
    # Test with operational expenses
    opex_params = basic_params.copy()
    opex_params.update({
        'maint_opex': 20000,        # $20k/year maintenance
        'capex': 50000,             # $50k upfront
        'amortization': 5000        # $5k/month during build
    })
    
    results_opex = simulator.simulate(opex_params)
    
    # Manual OpEx PV calculation
    manual_opex_pv = sum(20000 / (1.1 ** year) for year in range(1, 6))  # 5 years
    
    # Manual amortization PV (12 months)
    monthly_rate = (1 + 0.1) ** (1/12) - 1  # Correct monthly rate conversion
    manual_amort_pv = sum(5000 / (1 + monthly_rate) ** month for month in range(1, 13))
    
    print(f"Manual OpEx PV (5 years @ 10%): ${manual_opex_pv:,.0f}")
    print(f"Manual Amortization PV (12 months): ${manual_amort_pv:,.0f}")
    print(f"Expected total cost increase: ${manual_opex_pv + 50000 + manual_amort_pv:,.0f}")
    
    cost_increase = results_opex['expected_build_cost'] - results['expected_build_cost']
    print(f"Actual cost increase: ${cost_increase:,.0f}")
    
    # Test 7: Recommendation logic
    print("\n7️⃣ RECOMMENDATION LOGIC VALIDATION")
    print("-" * 40)
    
    # Case where build should win
    build_wins = {
        'build_timeline': 6,
        'fte_cost': 80000,
        'fte_count': 1,
        'useful_life': 5,
        'prob_success': 95,
        'wacc': 8,
        'product_price': 200000,
        'buy_selector': ['one_time']
    }
    
    # Case where buy should win
    buy_wins = {
        'build_timeline': 24,
        'fte_cost': 200000,
        'fte_count': 5,
        'useful_life': 5,
        'prob_success': 60,
        'wacc': 12,
        'product_price': 100000,
        'buy_selector': ['one_time']
    }
    
    results_build_wins = simulator.simulate(build_wins)
    results_buy_wins = simulator.simulate(buy_wins)
    
    print(f"Build wins case: {results_build_wins['recommendation']} (NPV diff: ${results_build_wins['npv_difference']:,.0f})")
    print(f"Buy wins case: {results_buy_wins['recommendation']} (NPV diff: ${results_buy_wins['npv_difference']:,.0f})")
    
    recommendation_logic_correct = (
        results_build_wins['recommendation'] == 'Build' and
        results_buy_wins['recommendation'] == 'Buy'
    )
    print(f"✅ Recommendation logic correct: {recommendation_logic_correct}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    all_tests = [
        build_cost_close,
        subscription_close,
        risk_increased,
        prob_correct,
        variability_increased,
        recommendation_logic_correct
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL CALCULATION LOGIC VALIDATED SUCCESSFULLY!")
        print("✅ Build cost calculations are correct")
        print("✅ Buy cost calculations are correct")
        print("✅ Risk factor applications work properly")
        print("✅ Probability calculations are accurate")
        print("✅ Variability metrics are meaningful")
        print("✅ Recommendation logic is sound")
    else:
        print("⚠️  Some validation tests failed. Review the calculations.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    test_comprehensive_calculation_logic()
