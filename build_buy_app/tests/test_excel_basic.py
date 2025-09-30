"""
Simple test to check if Excel export is working
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.excel_export import ExcelExporter

def test_excel_basic():
    """Test basic Excel export functionality."""
    
    test_params = {
        'build_timeline': 12,
        'fte_cost': 150000,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 10,
        'tech_risk': 10,
        'vendor_risk': 5,
        'market_risk': 5,
        'misc_costs': 50000,
        'capex': 100000,
        'amortization': 5000,
        'maint_opex': 20000,
        'product_price': 500000,
        'subscription_price': 0,
        'buy_selector': ['one_time']
    }
    
    print("Testing basic Excel export...")
    
    try:
        exporter = ExcelExporter()
        excel_bytes = exporter.create_excel_export(test_params)
        
        if excel_bytes:
            print(f"✅ Excel export successful - {len(excel_bytes)} bytes generated")
            return True
        else:
            print("❌ Excel export returned None")
            return False
            
    except Exception as e:
        print(f"❌ Excel export failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_basic()
    if success:
        print("Excel export is working!")
    else:
        print("Excel export has issues!")
