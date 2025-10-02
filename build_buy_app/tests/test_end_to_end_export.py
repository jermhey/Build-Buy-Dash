"""
End-to-End Test for Multi-Scenario Excel Export
Tests the complete workflow: create scenarios, save them, export to Excel
"""
import sys
import os
import tempfile
import zipfile
from io import BytesIO

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import BuildVsBuyApp
from src.simulation import BuildVsBuySimulator


def test_complete_workflow():
    """Test the complete workflow from scenario creation to Excel export."""
    print("🧪 Testing complete multi-scenario workflow...")
    
    # Initialize the app
    app_instance = BuildVsBuyApp()
    
    # Create test scenarios with different parameters
    test_scenarios = []
    
    # Scenario 1: Small project
    scenario1 = {
        'name': 'Small_Mobile_App',
        'build_timeline': 6,
        'fte_cost': 120000,
        'fte_count': 2,
        'useful_life': 3,
        'prob_success': 85,
        'wacc': 8,
        'product_price': 300000,
        'buy_selector': ['one_time'],
        'risk_selector': [],
        'cost_selector': [],
        'results': {'recommendation': 'Build', 'expected_build_cost': 240000, 'buy_total_cost': 300000}
    }
    
    # Scenario 2: Large enterprise project
    scenario2 = {
        'name': 'Enterprise_Platform',
        'build_timeline': 24,
        'fte_cost': 160000,
        'fte_count': 8,
        'useful_life': 7,
        'prob_success': 70,
        'wacc': 8,
        'product_price': 2000000,
        'buy_selector': ['one_time'],
        'risk_selector': [],
        'cost_selector': [],
        'results': {'recommendation': 'Buy', 'expected_build_cost': 3200000, 'buy_total_cost': 2000000}
    }
    
    # Scenario 3: Medium complexity project
    scenario3 = {
        'name': 'Integration_Solution',
        'build_timeline': 12,
        'fte_cost': 140000,
        'fte_count': 4,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'product_price': 800000,
        'buy_selector': ['one_time'],
        'risk_selector': [],
        'cost_selector': [],
        'results': {'recommendation': 'Build', 'expected_build_cost': 560000, 'buy_total_cost': 800000}
    }
    
    test_scenarios = [scenario1, scenario2, scenario3]
    
    print(f"✅ Created {len(test_scenarios)} test scenarios")
    
    # Test single scenario export
    print("🧪 Testing single scenario export...")
    single_excel = app_instance.excel_exporter.create_excel_export(scenario1)
    assert single_excel is not None, "Single scenario export should work"
    assert len(single_excel) > 1000, "Excel file should have content"
    print("✅ Single scenario export works")
    
    # Test multiple scenario exports
    print("🧪 Testing multiple scenario exports...")
    multiple_exports = app_instance.excel_exporter.create_multiple_scenario_exports(test_scenarios)
    assert len(multiple_exports) == 3, f"Should create 3 exports, got {len(multiple_exports)}"
    
    # Verify each export
    expected_names = ['Small_Mobile_App', 'Enterprise_Platform', 'Integration_Solution']
    found_names = []
    
    for filename, excel_data in multiple_exports:
        assert excel_data is not None, f"Excel data should not be None for {filename}"
        assert len(excel_data) > 1000, f"Excel file should have content for {filename}"
        
        # Extract scenario name from filename
        for expected_name in expected_names:
            if expected_name in filename:
                found_names.append(expected_name)
                break
    
    assert len(found_names) == 3, f"Should find all scenario names in filenames. Found: {found_names}"
    print("✅ Multiple scenario exports work")
    
    # Test ZIP creation
    print("🧪 Testing ZIP creation...")
    zip_data = app_instance.excel_exporter.create_scenarios_zip(test_scenarios)
    assert zip_data is not None, "ZIP creation should work"
    assert len(zip_data) > 1000, "ZIP file should have content"
    
    # Verify ZIP contents
    zip_buffer = BytesIO(zip_data)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) == 3, f"ZIP should contain 3 files, got {len(file_list)}"
        
        for filename in file_list:
            assert filename.endswith('.xlsx'), f"File should be Excel: {filename}"
            
            # Test that file can be extracted
            with zip_file.open(filename) as excel_file:
                excel_content = excel_file.read()
                assert len(excel_content) > 1000, f"Excel file {filename} should have content"
    
    print("✅ ZIP creation works")
    
    # Test the scenario table creation (this is used in the UI)
    print("🧪 Testing scenario table creation...")
    scenario_table = app_instance.create_scenario_table(test_scenarios)
    assert scenario_table is not None, "Scenario table should be created"
    print("✅ Scenario table creation works")
    
    print("✅ Complete workflow test passed!")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("🧪 Testing edge cases...")
    
    app_instance = BuildVsBuyApp()
    
    # Test with empty scenarios
    empty_exports = app_instance.excel_exporter.create_multiple_scenario_exports([])
    assert empty_exports == [], "Empty scenarios should return empty list"
    
    empty_zip = app_instance.excel_exporter.create_scenarios_zip([])
    assert empty_zip is None, "Empty scenarios should return None for ZIP"
    
    # Test with scenario that has special characters in name
    special_scenario = {
        'name': 'Project/With<>Special*Chars:Test?File|Name',
        'build_timeline': 12,
        'fte_cost': 150000,
        'fte_count': 2,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'product_price': 500000,
        'buy_selector': ['one_time'],
        'risk_selector': [],
        'cost_selector': [],
        'results': {'recommendation': 'Build', 'expected_build_cost': 300000}
    }
    
    special_exports = app_instance.excel_exporter.create_multiple_scenario_exports([special_scenario])
    assert len(special_exports) == 1, "Should handle special characters in names"
    
    filename, excel_data = special_exports[0]
    # Check that problematic characters are replaced
    assert all(char not in filename for char in '/\\<>*?:|'), "Special characters should be replaced"
    assert excel_data is not None, "Excel data should be generated"
    
    print("✅ Edge cases test passed!")


def test_user_experience_scenarios():
    """Test realistic user scenarios."""
    print("🧪 Testing realistic user scenarios...")
    
    app_instance = BuildVsBuyApp()
    
    # Scenario: User has 1 saved scenario (should get single Excel file)
    single_scenario = [{
        'name': 'My_Project',
        'build_timeline': 15,
        'fte_cost': 130000,
        'fte_count': 3,
        'useful_life': 5,
        'prob_success': 75,
        'wacc': 8,
        'results': {'recommendation': 'Build'}
    }]
    
    # Single scenario should use regular export, not ZIP
    single_export = app_instance.excel_exporter.create_excel_export(single_scenario[0])
    assert single_export is not None, "Single scenario export should work"
    
    # Scenario: User has 5 saved scenarios (should get ZIP)
    multiple_scenarios = []
    for i in range(5):
        scenario = {
            'name': f'Project_{chr(65+i)}',  # Project_A, Project_B, etc.
            'build_timeline': 10 + i*2,
            'fte_cost': 130000 + i*10000,
            'fte_count': 2 + i,
            'useful_life': 5,
            'prob_success': 80 - i*2,
            'wacc': 8,
            'results': {'recommendation': 'Build' if i % 2 == 0 else 'Buy'}
        }
        multiple_scenarios.append(scenario)
    
    multiple_zip = app_instance.excel_exporter.create_scenarios_zip(multiple_scenarios)
    assert multiple_zip is not None, "Multiple scenarios should create ZIP"
    
    # Verify ZIP contains all scenarios
    zip_buffer = BytesIO(multiple_zip)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) == 5, f"Should have 5 files in ZIP, got {len(file_list)}"
        
        # Check that each project is represented
        project_names = ['Project_A', 'Project_B', 'Project_C', 'Project_D', 'Project_E']
        for project_name in project_names:
            assert any(project_name in filename for filename in file_list), \
                f"Should find {project_name} in filenames: {file_list}"
    
    print("✅ User experience scenarios test passed!")


if __name__ == "__main__":
    print("🚀 Running End-to-End Multi-Scenario Tests...")
    print("=" * 70)
    
    try:
        test_complete_workflow()
        test_edge_cases()
        test_user_experience_scenarios()
        
        print("=" * 70)
        print("🎉 ALL END-TO-END TESTS PASSED!")
        print("✨ Multi-scenario Excel export feature is fully functional!")
        print()
        print("📋 Feature Summary:")
        print("• ✅ Single scenario → Single Excel file")
        print("• ✅ Multiple scenarios → ZIP with separate Excel files")
        print("• ✅ Filename sanitization for special characters")
        print("• ✅ Professional naming convention")
        print("• ✅ Error handling for edge cases")
        print("• ✅ Integration with existing app functionality")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        print("🔧 Please fix issues before using the feature.")
        sys.exit(1)
