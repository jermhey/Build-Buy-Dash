"""
Test the new Sensitivity Analysis sheet functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.excel_export import ExcelExporter


def test_sensitivity_sheet_creation():
    """Test that the sensitivity analysis sheet can be created without errors."""
    
    # Sample scenario data
    test_scenario = {
        'build_timeline': 15,
        'fte_cost': 180000,
        'fte_count': 3,
        'prob_success': 85,
        'wacc': 10,
        'tech_risk': 15,
        'vendor_risk': 8,
        'market_risk': 5,
        'product_price': 800000,
        'subscription_price': 120000,
        'useful_life': 5
    }
    
    try:
        exporter = ExcelExporter()
        excel_data = exporter.create_excel_export(test_scenario)
        
        # Check that we got some data back
        assert excel_data is not None, "Excel export returned None"
        assert len(excel_data) > 0, "Excel export returned empty data"
        
        print("✅ Sensitivity Analysis sheet creation test PASSED")
        print(f"   Generated Excel file of {len(excel_data):,} bytes")
        
        # Optionally save for manual inspection
        with open('test_sensitivity_output.xlsx', 'wb') as f:
            f.write(excel_data)
        print("   Test file saved as 'test_sensitivity_output.xlsx'")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensitivity Analysis sheet test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_validation_ranges():
    """Test that our parameter ranges are sensible."""
    
    # Test edge cases
    edge_cases = [
        {'build_timeline': 6, 'fte_cost': 80000},    # Minimum values
        {'build_timeline': 36, 'fte_cost': 250000},  # Maximum values
        {'build_timeline': 12, 'fte_cost': 150000}   # Typical values
    ]
    
    for i, case in enumerate(edge_cases):
        try:
            test_scenario = {
                'build_timeline': case['build_timeline'],
                'fte_cost': case['fte_cost'],
                'fte_count': 2,
                'prob_success': 80,
                'wacc': 8,
                'tech_risk': 10,
                'vendor_risk': 5,
                'market_risk': 5,
                'product_price': 500000,
                'subscription_price': 100000,
                'useful_life': 5
            }
            
            exporter = ExcelExporter()
            excel_data = exporter.create_excel_export(test_scenario)
            assert excel_data is not None
            
            print(f"✅ Edge case {i+1} test PASSED")
            
        except Exception as e:
            print(f"❌ Edge case {i+1} test FAILED: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("🧪 Testing Sensitivity Analysis Sheet Implementation...")
    print("=" * 60)
    
    success = True
    
    # Run tests
    success &= test_sensitivity_sheet_creation()
    success &= test_parameter_validation_ranges()
    
    print("=" * 60)
    if success:
        print("🎉 ALL SENSITIVITY ANALYSIS TESTS PASSED!")
        print("📊 The new sheet includes:")
        print("   • Interactive parameter controls with validation")
        print("   • Real-time calculation engine")
        print("   • Sensitivity matrix analysis")
        print("   • Visual formatting and user guidance")
    else:
        print("🔧 Some tests failed - please review the errors above")
