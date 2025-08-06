#!/usr/bin/env python3
"""
Edge Cases and User Experience Impact Validation
Test scenarios that most impact user decision-making
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import BuildVsBuySimulator
from app import BuildVsBuyApp

def test_critical_edge_cases():
    """Test edge cases that most impact user experience."""
    print("🎯 CRITICAL EDGE CASES & USER EXPERIENCE VALIDATION")
    print("=" * 70)
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    app = BuildVsBuyApp()
    
    print("\n1️⃣ ZERO/MINIMAL INPUT HANDLING")
    print("-" * 40)
    
    # Test with minimal inputs (common user scenario)
    minimal_params = {
        'build_timeline': 12,
        'fte_cost': 100000,
        'fte_count': 1,
        'useful_life': 5,
        'prob_success': 90,
        'wacc': 8,
        'product_price': 200000,
        'buy_selector': ['one_time']
        # All other parameters should default to 0
    }
    
    results_minimal = simulator.simulate(minimal_params)
    prob_minimal = app._calculate_probability_build_costs_less(results_minimal)
    
    print(f"Minimal inputs result: {results_minimal['recommendation']}")
    print(f"Build cost: ${results_minimal['expected_build_cost']:,.0f}")
    print(f"Buy cost: ${results_minimal['buy_total_cost']:,.0f}")
    print(f"Probability: {prob_minimal:.1f}%")
    
    # Should handle gracefully
    minimal_ok = all([
        results_minimal['expected_build_cost'] > 0,
        results_minimal['buy_total_cost'] > 0,
        results_minimal['recommendation'] in ['Build', 'Buy'],
        0 <= prob_minimal <= 100
    ])
    print(f"✅ Minimal inputs handled correctly: {minimal_ok}")
    
    print("\n2️⃣ HIGH UNCERTAINTY SCENARIO")
    print("-" * 40)
    
    # High uncertainty - critical for user confidence
    uncertain_params = {
        'build_timeline': 18,
        'build_timeline_std': 6,        # ±6 months uncertainty
        'fte_cost': 150000,
        'fte_cost_std': 30000,          # ±$30k uncertainty  
        'fte_count': 3,
        'useful_life': 5,
        'prob_success': 70,             # Lower success probability
        'wacc': 10,
        'product_price': 800000,
        'buy_selector': ['one_time'],
        'tech_risk': 25,                # High technical risk
        'vendor_risk': 15,              # Vendor risk
        'market_risk': 10               # Market risk
    }
    
    results_uncertain = simulator.simulate(uncertain_params)
    prob_uncertain = app._calculate_probability_build_costs_less(results_uncertain)
    var_uncertain = app._calculate_cost_variability(results_uncertain)
    
    print(f"High uncertainty result: {results_uncertain['recommendation']}")
    print(f"Build P10/P50/P90: ${results_uncertain['build_cost_p10']:,.0f} / ${results_uncertain['build_cost_p50']:,.0f} / ${results_uncertain['build_cost_p90']:,.0f}")
    print(f"Cost variability: ±${var_uncertain:,.0f}")
    print(f"Probability: {prob_uncertain:.1f}%")
    
    # Should show meaningful spread
    meaningful_spread = (results_uncertain['build_cost_p90'] - results_uncertain['build_cost_p10']) > 100000
    high_variability = var_uncertain > 50000
    
    print(f"✅ Meaningful cost spread: {meaningful_spread}")
    print(f"✅ High variability captured: {high_variability}")
    
    print("\n3️⃣ CLOSE DECISION SCENARIO")
    print("-" * 40)
    
    # Close call - most critical for user decision making
    close_params = {
        'build_timeline': 15,
        'fte_cost': 130000,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 85,
        'wacc': 8,
        'product_price': 340000,        # Tuned to be close
        'buy_selector': ['one_time'],
        'build_timeline_std': 2,        # Some uncertainty
        'fte_cost_std': 10000
    }
    
    results_close = simulator.simulate(close_params)
    prob_close = app._calculate_probability_build_costs_less(results_close)
    
    print(f"Close decision result: {results_close['recommendation']}")
    print(f"NPV difference: ${abs(results_close['npv_difference']):,.0f}")
    print(f"Probability: {prob_close:.1f}%")
    
    # For close decisions, probability should be meaningful (not 0% or 100%)
    meaningful_probability = 10 <= prob_close <= 90
    print(f"✅ Meaningful probability for close decision: {meaningful_probability}")
    
    print("\n4️⃣ SUBSCRIPTION VS ONE-TIME COMPARISON")
    print("-" * 40)
    
    # Critical business decision - subscription vs one-time
    subscription_params = {
        'build_timeline': 12,
        'fte_cost': 120000,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 90,
        'wacc': 8,
        'buy_selector': ['subscription'],
        'subscription_price': 80000,    # $80k/year
        'subscription_increase': 5      # 5% annual increase
    }
    
    onetime_params = subscription_params.copy()
    onetime_params.update({
        'buy_selector': ['one_time'],
        'product_price': 350000         # $350k one-time
    })
    
    results_sub = simulator.simulate(subscription_params)
    results_one = simulator.simulate(onetime_params)
    
    print(f"Subscription total cost: ${results_sub['buy_total_cost']:,.0f}")
    print(f"One-time total cost: ${results_one['buy_total_cost']:,.0f}")
    print(f"Subscription recommendation: {results_sub['recommendation']}")
    print(f"One-time recommendation: {results_one['recommendation']}")
    
    # Should produce different costs
    different_costs = abs(results_sub['buy_total_cost'] - results_one['buy_total_cost']) > 10000
    print(f"✅ Subscription vs one-time produces different costs: {different_costs}")
    
    print("\n5️⃣ EXTREME WACC SCENARIOS")
    print("-" * 40)
    
    # Test extreme WACC values that users might input
    low_wacc_params = minimal_params.copy()
    low_wacc_params['wacc'] = 2  # Very low discount rate
    
    high_wacc_params = minimal_params.copy()  
    high_wacc_params['wacc'] = 15  # High discount rate
    
    results_low_wacc = simulator.simulate(low_wacc_params)
    results_high_wacc = simulator.simulate(high_wacc_params)
    
    print(f"Low WACC (2%) build cost: ${results_low_wacc['expected_build_cost']:,.0f}")
    print(f"High WACC (15%) build cost: ${results_high_wacc['expected_build_cost']:,.0f}")
    
    # High WACC should result in lower present values
    wacc_effect_correct = results_high_wacc['expected_build_cost'] < results_low_wacc['expected_build_cost']
    print(f"✅ WACC effect on discounting correct: {wacc_effect_correct}")
    
    print("\n" + "=" * 70)
    print("🎯 CRITICAL VALIDATION SUMMARY")
    print("=" * 70)
    
    all_checks = [
        minimal_ok,
        meaningful_spread,
        high_variability,
        meaningful_probability,
        different_costs,
        wacc_effect_correct
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"✅ Minimal input handling: {minimal_ok}")
    print(f"✅ Uncertainty properly captured: {meaningful_spread and high_variability}")
    print(f"✅ Close decisions show meaningful probability: {meaningful_probability}")
    print(f"✅ Buy options properly differentiated: {different_costs}")
    print(f"✅ WACC effects working correctly: {wacc_effect_correct}")
    
    print(f"\nCRITICAL VALIDATION SCORE: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL CRITICAL USER EXPERIENCE FUNCTIONS WORKING PERFECTLY!")
        print("✅ Edge cases handled gracefully")
        print("✅ Uncertainty properly communicated to users")
        print("✅ Close decisions provide meaningful guidance")
        print("✅ All calculation components mathematically sound")
        print("✅ User-facing metrics provide business value")
    else:
        print("⚠️  Some critical user experience issues detected")
    
    return passed == total

if __name__ == "__main__":
    test_critical_edge_cases()
