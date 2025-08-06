#!/usr/bin/env python3
"""
Quick test to verify the probability calculation fixes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator

def test_probability_calculation():
    """Test that probability calculations are working correctly."""
    print("🧪 Testing Build vs Buy Probability Calculations...")
    print("=" * 60)
    
    simulator = BuildVsBuySimulator(n_simulations=1000)
    
    # Test case 1: Build should clearly be cheaper
    params1 = {
        'build_timeline': 6,        # Short timeline
        'fte_cost': 100000,         # Low cost
        'fte_count': 1,             # Few people
        'useful_life': 5,
        'prob_success': 95,         # High probability
        'wacc': 8,
        'product_price': 500000,    # Expensive buy option
        'buy_selector': ['one_time']
    }
    
    results1 = simulator.simulate(params1)
    cost_distribution = results1.get('cost_distribution', [])
    buy_cost = results1.get('buy_total_cost', 0)
    
    # Manual calculation
    build_costs_less = sum(1 for cost in cost_distribution if cost < buy_cost)
    manual_probability = (build_costs_less / len(cost_distribution)) * 100
    
    print(f"Test Case 1 - Build should be cheaper:")
    print(f"  Expected Build Cost: ${results1.get('expected_build_cost', 0):,.0f}")
    print(f"  Buy Cost: ${buy_cost:,.0f}")
    print(f"  Build P10/P50/P90: ${results1.get('build_cost_p10', 0):,.0f} / ${results1.get('build_cost_p50', 0):,.0f} / ${results1.get('build_cost_p90', 0):,.0f}")
    print(f"  Simulations where build < buy: {build_costs_less}/{len(cost_distribution)}")
    print(f"  Manual probability calculation: {manual_probability:.1f}%")
    print(f"  Recommendation: {results1.get('recommendation')}")
    print()
    
    # Test case 2: Buy should clearly be cheaper
    params2 = {
        'build_timeline': 24,       # Long timeline
        'fte_cost': 200000,         # High cost
        'fte_count': 5,             # Many people
        'useful_life': 5,
        'prob_success': 70,         # Lower probability
        'wacc': 8,
        'product_price': 100000,    # Cheap buy option
        'buy_selector': ['one_time'],
        'tech_risk': 20,            # Add some risk
        'vendor_risk': 15
    }
    
    results2 = simulator.simulate(params2)
    cost_distribution2 = results2.get('cost_distribution', [])
    buy_cost2 = results2.get('buy_total_cost', 0)
    
    # Manual calculation
    build_costs_less2 = sum(1 for cost in cost_distribution2 if cost < buy_cost2)
    manual_probability2 = (build_costs_less2 / len(cost_distribution2)) * 100
    
    print(f"Test Case 2 - Buy should be cheaper:")
    print(f"  Expected Build Cost: ${results2.get('expected_build_cost', 0):,.0f}")
    print(f"  Buy Cost: ${buy_cost2:,.0f}")
    print(f"  Build P10/P50/P90: ${results2.get('build_cost_p10', 0):,.0f} / ${results2.get('build_cost_p50', 0):,.0f} / ${results2.get('build_cost_p90', 0):,.0f}")
    print(f"  Simulations where build < buy: {build_costs_less2}/{len(cost_distribution2)}")
    print(f"  Manual probability calculation: {manual_probability2:.1f}%")
    print(f"  Recommendation: {results2.get('recommendation')}")
    print()
    
    # Test importing the app class to make sure the helper methods work
    from app import BuildVsBuyApp
    app_instance = BuildVsBuyApp()
    
    # Test the helper methods
    prob1 = app_instance._calculate_probability_build_costs_less(results1)
    prob2 = app_instance._calculate_probability_build_costs_less(results2)
    var1 = app_instance._calculate_cost_variability(results1)
    var2 = app_instance._calculate_cost_variability(results2)
    
    print(f"App Helper Method Results:")
    print(f"  Test 1 - App calculated probability: {prob1:.1f}% (should match {manual_probability:.1f}%)")
    print(f"  Test 1 - Cost variability: ±${var1:,.0f}")
    print(f"  Test 2 - App calculated probability: {prob2:.1f}% (should match {manual_probability2:.1f}%)")
    print(f"  Test 2 - Cost variability: ±${var2:,.0f}")
    
    print("=" * 60)
    print("✅ Test completed! Check that probabilities match manual calculations.")

if __name__ == "__main__":
    test_probability_calculation()
