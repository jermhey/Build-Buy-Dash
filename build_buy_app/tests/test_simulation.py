"""
Simple test for the simulation engine
Run with: python -m pytest tests/test_simulation.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import BuildVsBuySimulator


def test_basic_simulation():
    """Test that the simulator runs without errors."""
    simulator = BuildVsBuySimulator(n_simulations=100)  # Smaller for testing
    
    # Simple test parameters
    params = {
        'build_timeline': 12,
        'fte_cost': 150000,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'product_price': 500000,
        'buy_selector': ['one_time']
    }
    
    results = simulator.simulate(params)
    
    # Check that we get expected result keys
    assert 'expected_build_cost' in results
    assert 'buy_total_cost' in results
    assert 'recommendation' in results
    assert results['recommendation'] in ['Build', 'Buy']
    
    # Check that costs are positive
    assert results['expected_build_cost'] > 0
    assert results['buy_total_cost'] >= 0


def test_parameter_validation():
    """Test that the simulator handles edge cases."""
    simulator = BuildVsBuySimulator(n_simulations=10)
    
    # Test with minimal parameters
    params = {
        'build_timeline': 1,
        'fte_cost': 1,
        'fte_count': 1,
        'useful_life': 1,
        'prob_success': 1,
        'wacc': 1
    }
    
    results = simulator.simulate(params)
    assert results is not None
    assert 'recommendation' in results


def test_app_integration():
    """Test that the main app can be imported and initialized."""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from app import BuildVsBuyApp
        app_instance = BuildVsBuyApp()
        assert app_instance.app is not None
        print("✅ App integration test passed")
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        raise


def test_csv_scenario_features():
    """Test scenario saving functionality."""
    scenarios = [
        {'name': 'Test1', 'build_timeline': 12, 'fte_cost': 150000, 'fte_count': 2},
        {'name': 'Test2', 'build_timeline': 18, 'fte_cost': 180000, 'fte_count': 3}
    ]
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from app import BuildVsBuyApp
    app_instance = BuildVsBuyApp()
    
    # Test scenario table creation
    table = app_instance.create_scenario_table(scenarios)
    assert table is not None
    print("✅ Scenario table test passed")


if __name__ == "__main__":
    # Run all tests
    print("🧪 Running Build vs Buy Dashboard Tests...")
    print("=" * 50)
    
    try:
        test_basic_simulation()
        print("✅ Basic simulation test passed")
        
        test_parameter_validation()
        print("✅ Parameter validation test passed")
        
        test_app_integration()
        
        test_csv_scenario_features()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! Your app is ready for production.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("=" * 50)
        print("🔧 Please fix issues before deployment.")
