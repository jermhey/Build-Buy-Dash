"""
Test Multi-Scenario Excel Export Feature
Tests the new functionality for exporting multiple scenarios as separate Excel files
"""
import sys
import os
import tempfile
import zipfile
from io import BytesIO

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.excel_export import ExcelExporter
from src.simulation import BuildVsBuySimulator


def create_test_scenario(name, build_timeline=12, fte_cost=150000, fte_count=2):
    """Create a test scenario with simulation results."""
    simulator = BuildVsBuySimulator(n_simulations=10)  # Small for testing
    
    params = {
        'build_timeline': build_timeline,
        'fte_cost': fte_cost,
        'fte_count': fte_count,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'product_price': 500000,
        'buy_selector': ['one_time']
    }
    
    results = simulator.simulate(params)
    
    scenario = {
        'name': name,
        'build_timeline': build_timeline,
        'fte_cost': fte_cost,
        'fte_count': fte_count,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'product_price': 500000,
        'buy_selector': ['one_time'],
        'risk_selector': [],
        'cost_selector': [],
        'results': results
    }
    
    return scenario


def test_single_scenario_export():
    """Test exporting a single scenario."""
    print("🧪 Testing single scenario export...")
    
    exporter = ExcelExporter()
    scenario = create_test_scenario("Test_Single_Scenario")
    
    # Test single scenario export
    excel_data = exporter.create_excel_export(scenario)
    
    assert excel_data is not None, "Excel export should return data"
    assert len(excel_data) > 1000, "Excel file should have substantial content"
    
    print("✅ Single scenario export test passed")


def test_multiple_scenario_exports():
    """Test creating multiple Excel files from scenarios."""
    print("🧪 Testing multiple scenario exports...")
    
    exporter = ExcelExporter()
    
    # Create test scenarios
    scenarios = [
        create_test_scenario("Project_Alpha", 12, 150000, 2),
        create_test_scenario("Project_Beta", 18, 180000, 3),
        create_test_scenario("Project_Gamma", 9, 120000, 1)
    ]
    
    # Test multiple exports
    exports = exporter.create_multiple_scenario_exports(scenarios)
    
    assert len(exports) == 3, f"Should create 3 exports, got {len(exports)}"
    
    for filename, excel_data in exports:
        assert filename.endswith('.xlsx'), f"Filename should end with .xlsx: {filename}"
        assert 'BuildVsBuyAnalysis' in filename, f"Filename should contain 'BuildVsBuyAnalysis': {filename}"
        assert excel_data is not None, f"Excel data should not be None for {filename}"
        assert len(excel_data) > 1000, f"Excel file should have content for {filename}"
    
    # Check that filenames are unique and contain scenario names
    filenames = [filename for filename, _ in exports]
    assert len(set(filenames)) == 3, "All filenames should be unique"
    
    assert any("Project_Alpha" in fn for fn in filenames), "Should have Project_Alpha file"
    assert any("Project_Beta" in fn for fn in filenames), "Should have Project_Beta file"
    assert any("Project_Gamma" in fn for fn in filenames), "Should have Project_Gamma file"
    
    print("✅ Multiple scenario exports test passed")


def test_zip_creation():
    """Test creating ZIP file with multiple scenarios."""
    print("🧪 Testing ZIP file creation...")
    
    exporter = ExcelExporter()
    
    # Create test scenarios
    scenarios = [
        create_test_scenario("Scenario_One", 12, 150000, 2),
        create_test_scenario("Scenario_Two", 15, 160000, 3)
    ]
    
    # Test ZIP creation
    zip_data = exporter.create_scenarios_zip(scenarios)
    
    assert zip_data is not None, "ZIP data should not be None"
    assert len(zip_data) > 1000, "ZIP file should have substantial content"
    
    # Test that ZIP contains the expected files
    zip_buffer = BytesIO(zip_data)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        
        assert len(file_list) == 2, f"ZIP should contain 2 files, got {len(file_list)}"
        
        for filename in file_list:
            assert filename.endswith('.xlsx'), f"File should be Excel: {filename}"
            assert 'BuildVsBuyAnalysis' in filename, f"Filename should contain 'BuildVsBuyAnalysis': {filename}"
        
        # Test that files can be extracted and have content
        for filename in file_list:
            with zip_file.open(filename) as excel_file:
                excel_content = excel_file.read()
                assert len(excel_content) > 1000, f"Excel file {filename} should have content"
    
    print("✅ ZIP creation test passed")


def test_filename_sanitization():
    """Test that problematic characters in scenario names are handled."""
    print("🧪 Testing filename sanitization...")
    
    exporter = ExcelExporter()
    
    # Create scenarios with problematic names
    scenarios = [
        create_test_scenario("Project/With\\Slashes", 12, 150000, 2),
        create_test_scenario("Project:With*Special?Chars", 15, 160000, 3),
        create_test_scenario("Project<>With|Brackets", 18, 170000, 4)
    ]
    
    exports = exporter.create_multiple_scenario_exports(scenarios)
    
    assert len(exports) == 3, f"Should create 3 exports despite problematic names"
    
    for filename, excel_data in exports:
        # Check that problematic characters are replaced
        assert '/' not in filename, f"Filename should not contain '/': {filename}"
        assert '\\' not in filename, f"Filename should not contain '\\': {filename}"
        assert ':' not in filename, f"Filename should not contain ':': {filename}"
        assert '*' not in filename, f"Filename should not contain '*': {filename}"
        assert '?' not in filename, f"Filename should not contain '?': {filename}"
        assert '<' not in filename, f"Filename should not contain '<': {filename}"
        assert '>' not in filename, f"Filename should not contain '>': {filename}"
        assert '|' not in filename, f"Filename should not contain '|': {filename}"
        
        # Should contain underscores as replacements
        assert '_' in filename, f"Filename should contain replacement underscores: {filename}"
    
    print("✅ Filename sanitization test passed")


def test_empty_scenarios():
    """Test handling of empty scenario list."""
    print("🧪 Testing empty scenarios handling...")
    
    exporter = ExcelExporter()
    
    # Test empty list
    exports = exporter.create_multiple_scenario_exports([])
    assert exports == [], "Empty scenarios should return empty list"
    
    # Test ZIP with empty list
    zip_data = exporter.create_scenarios_zip([])
    assert zip_data is None, "Empty scenarios should return None for ZIP"
    
    print("✅ Empty scenarios handling test passed")


def test_app_integration():
    """Test that the app can be imported and the new functionality works."""
    print("🧪 Testing app integration...")
    
    try:
        from app import BuildVsBuyApp
        app_instance = BuildVsBuyApp()
        
        # Verify the app still works
        assert app_instance.app is not None, "App should initialize successfully"
        assert app_instance.excel_exporter is not None, "Excel exporter should be available"
        
        # Verify new methods exist
        assert hasattr(app_instance.excel_exporter, 'create_multiple_scenario_exports'), \
            "Should have create_multiple_scenario_exports method"
        assert hasattr(app_instance.excel_exporter, 'create_scenarios_zip'), \
            "Should have create_scenarios_zip method"
        
        print("✅ App integration test passed")
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Running Multi-Scenario Excel Export Tests...")
    print("=" * 60)
    
    try:
        test_single_scenario_export()
        test_multiple_scenario_exports()
        test_zip_creation()
        test_filename_sanitization()
        test_empty_scenarios()
        test_app_integration()
        
        print("=" * 60)
        print("🎉 ALL MULTI-SCENARIO EXPORT TESTS PASSED!")
        print("✨ Your new multi-scenario export feature is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        print("🔧 Please fix issues before using the feature.")
        sys.exit(1)
