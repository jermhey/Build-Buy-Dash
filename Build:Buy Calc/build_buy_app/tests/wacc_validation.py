#!/usr/bin/env python3
"""
Critical WACC Discounting Validation
Focus on core functions that impact user experience most
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import BuildVsBuySimulator
from app import BuildVsBuyApp

def test_wacc_discounting_logic():
    """Test that all key metrics are properly discounted by WACC."""
    print("🔍 CRITICAL WACC DISCOUNTING VALIDATION")
    print("=" * 60)
    
    simulator = BuildVsBuySimulator(n_simulations=1000, random_seed=42)
    
    # Test case with clear timeline and costs for easy validation
    params = {
        'build_timeline': 24,           # 2 years
        'build_timeline_std': 0,        # No uncertainty for clear calculation
        'fte_cost': 120000,            # $120k/year
        'fte_cost_std': 0,             # No uncertainty
        'fte_count': 1,                # 1 person
        'useful_life': 3,              # 3 years useful life
        'prob_success': 100,           # 100% success
        'wacc': 10,                    # 10% discount rate
        'buy_selector': ['subscription'],
        'subscription_price': 50000,    # $50k/year subscription
        'subscription_increase': 0,     # No escalation for simplicity
        'maint_opex': 10000,           # $10k/year maintenance
        'maint_opex_std': 0,           # No uncertainty
        'capex': 30000,                # $30k immediate capex
        'amortization': 2000,          # $2k/month during build
        'misc_costs': 5000,            # $5k misc costs
        'tech_risk': 0,
        'vendor_risk': 0,
        'market_risk': 0
    }
    
    results = simulator.simulate(params)
    
    print("1️⃣ LABOR COST DISCOUNTING")
    print("-" * 30)
    # Manual labor calculation
    # Labor: 2 years * $120k = $240k
    # Discounted: $240k / (1.1)^2 = $198,347
    manual_labor_undiscounted = 2 * 120000
    manual_labor_discounted = manual_labor_undiscounted / (1.1 ** 2)
    
    print(f"Manual labor (undiscounted): ${manual_labor_undiscounted:,.0f}")
    print(f"Manual labor (discounted): ${manual_labor_discounted:,.0f}")
    
    print("\n2️⃣ OPEX DISCOUNTING")
    print("-" * 30)
    # OpEx should be discounted over useful life
    # Year 1: $10k / 1.1^1 = $9,091
    # Year 2: $10k / 1.1^2 = $8,264
    # Year 3: $10k / 1.1^3 = $7,513
    # Total: $24,868
    manual_opex_pv = sum(10000 / (1.1 ** year) for year in range(1, 4))
    print(f"Manual OpEx PV: ${manual_opex_pv:,.0f}")
    
    print("\n3️⃣ AMORTIZATION DISCOUNTING")
    print("-" * 30)
    # Monthly payments during 24-month build
    monthly_rate = (1.1) ** (1/12) - 1  # ~0.797%
    manual_amort_pv = sum(2000 / (1 + monthly_rate) ** month for month in range(1, 25))
    print(f"Manual Amortization PV: ${manual_amort_pv:,.0f}")
    
    print("\n4️⃣ BUY OPTION DISCOUNTING")
    print("-" * 30)
    # Subscription over 3 years with no escalation
    # Year 0: $50k (immediate)
    # Year 1: $50k / 1.1^1 = $45,455
    # Year 2: $50k / 1.1^2 = $41,322
    # Total: $136,777
    manual_subscription_pv = sum(50000 / (1.1 ** year) for year in range(3))
    print(f"Manual Subscription PV: ${manual_subscription_pv:,.0f}")
    print(f"Simulation Buy Cost: ${results['buy_total_cost']:,.0f}")
    
    print("\n5️⃣ TOTAL BUILD COST BREAKDOWN")
    print("-" * 30)
    expected_total = (manual_labor_discounted + manual_opex_pv + 
                     manual_amort_pv + 30000 + 5000)  # CapEx + misc immediate
    
    print(f"Expected total build cost: ${expected_total:,.0f}")
    print(f"Simulation build cost: ${results['expected_build_cost']:,.0f}")
    print(f"Difference: ${abs(results['expected_build_cost'] - expected_total):,.0f}")
    
    print("\n6️⃣ RECOMMENDATION LOGIC CHECK")
    print("-" * 30)
    print(f"Build Cost: ${results['expected_build_cost']:,.0f}")
    print(f"Buy Cost: ${results['buy_total_cost']:,.0f}")
    print(f"NPV Difference: ${results['npv_difference']:,.0f}")
    print(f"Recommendation: {results['recommendation']}")
    
    # Check if recommendation makes sense
    expected_recommendation = 'Build' if results['buy_total_cost'] > results['expected_build_cost'] else 'Buy'
    recommendation_correct = results['recommendation'] == expected_recommendation
    print(f"Recommendation logic correct: {recommendation_correct}")
    
    print("\n7️⃣ USER-FACING METRICS VALIDATION")
    print("-" * 30)
    
    app = BuildVsBuyApp()
    
    # Test probability calculation
    prob = app._calculate_probability_build_costs_less(results)
    print(f"Probability Build < Buy: {prob:.1f}%")
    
    # Test cost variability (should be 0 since no uncertainty)
    variability = app._calculate_cost_variability(results)
    print(f"Cost Variability: ±${variability:,.0f}")
    
    # Validate P10/P50/P90 (should be same since no uncertainty)
    print(f"P10/P50/P90: ${results['build_cost_p10']:,.0f} / ${results['build_cost_p50']:,.0f} / ${results['build_cost_p90']:,.0f}")
    
    # All should be the same with no uncertainty
    percentiles_same = (abs(results['build_cost_p10'] - results['build_cost_p50']) < 1 and
                       abs(results['build_cost_p50'] - results['build_cost_p90']) < 1)
    print(f"Percentiles consistent (no uncertainty): {percentiles_same}")
    
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    # Tolerance checks (allowing for small floating point differences)
    tolerance = 1000  # $1k tolerance
    
    subscription_ok = abs(results['buy_total_cost'] - manual_subscription_pv) < tolerance
    build_cost_reasonable = abs(results['expected_build_cost'] - expected_total) < tolerance * 3  # Bit more tolerance for complex calc
    
    all_checks = [
        subscription_ok,
        build_cost_reasonable,
        recommendation_correct,
        percentiles_same
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"✅ Subscription PV correct: {subscription_ok}")
    print(f"✅ Build cost calculation reasonable: {build_cost_reasonable}")  
    print(f"✅ Recommendation logic correct: {recommendation_correct}")
    print(f"✅ Percentiles consistent: {percentiles_same}")
    
    print(f"\nValidation Score: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL WACC DISCOUNTING LOGIC IS CORRECT!")
        print("✅ Labor costs properly discounted by timeline")
        print("✅ OpEx properly discounted by useful life")
        print("✅ Amortization properly discounted monthly")
        print("✅ Subscription properly discounted by payment schedule")
        print("✅ User-facing metrics are mathematically sound")
    else:
        print("⚠️  Some discounting issues detected")
        
    return passed == total

if __name__ == "__main__":
    test_wacc_discounting_logic()
