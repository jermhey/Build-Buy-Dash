"""
Multi-Scenario Excel Export Feature Demo
Demonstrates the new functionality for users
"""
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.excel_export import ExcelExporter


def demo_multi_scenario_export():
    """Demonstrate the multi-scenario export feature."""
    print("🎯 Multi-Scenario Excel Export Feature Demo")
    print("=" * 50)
    
    exporter = ExcelExporter()
    
    # Create sample scenarios (like what users would save)
    scenarios = [
        {
            'name': 'Mobile_App_Project',
            'build_timeline': 8,
            'fte_cost': 120000,
            'fte_count': 3,
            'useful_life': 3,
            'prob_success': 85,
            'wacc': 8,
            'product_price': 400000,
            'buy_selector': ['one_time'],
            'results': {
                'recommendation': 'Build',
                'expected_build_cost': 288000,
                'buy_total_cost': 400000,
                'npv_difference': 112000
            }
        },
        {
            'name': 'Enterprise_Platform',
            'build_timeline': 18,
            'fte_cost': 150000,
            'fte_count': 6,
            'useful_life': 7,
            'prob_success': 75,
            'wacc': 8,
            'product_price': 1500000,
            'buy_selector': ['one_time'],
            'results': {
                'recommendation': 'Buy',
                'expected_build_cost': 1620000,
                'buy_total_cost': 1500000,
                'npv_difference': -120000
            }
        },
        {
            'name': 'Data_Integration_Tool',
            'build_timeline': 12,
            'fte_cost': 140000,
            'fte_count': 4,
            'useful_life': 5,
            'prob_success': 80,
            'wacc': 8,
            'product_price': 750000,
            'buy_selector': ['one_time'],
            'results': {
                'recommendation': 'Build',
                'expected_build_cost': 672000,
                'buy_total_cost': 750000,
                'npv_difference': 78000
            }
        }
    ]
    
    print(f"📊 Created {len(scenarios)} sample scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        rec = scenario['results']['recommendation']
        cost_diff = scenario['results']['npv_difference']
        print(f"  {i}. {scenario['name']} → {rec} (NPV: ${cost_diff:,.0f})")
    
    print()
    print("🔄 Generating Excel exports...")
    
    # Generate individual Excel files
    exports = exporter.create_multiple_scenario_exports(scenarios)
    
    print(f"✅ Created {len(exports)} Excel files:")
    for filename, excel_data in exports:
        size_kb = len(excel_data) / 1024
        print(f"  📄 {filename} ({size_kb:.1f} KB)")
    
    print()
    print("🗜️ Creating ZIP file with all scenarios...")
    
    # Generate ZIP file
    zip_data = exporter.create_scenarios_zip(scenarios)
    
    if zip_data:
        zip_size_kb = len(zip_data) / 1024
        print(f"✅ Created ZIP file ({zip_size_kb:.1f} KB)")
        print(f"   📦 Contains {len(scenarios)} Excel files")
    
    print()
    print("🎯 Feature Benefits:")
    print("• Each scenario gets its own professional Excel workbook")
    print("• 4 comprehensive sheets per file: Parameters, Timeline, Sensitivity, Breakeven")
    print("• Clean filename format: ScenarioName_BuildVsBuyAnalysis_TIMESTAMP.xlsx")
    print("• Multiple scenarios → ZIP download for easy organization")
    print("• Single scenario → Direct Excel download")
    print("• Automatic filename sanitization for special characters")
    
    print()
    print("👥 User Experience:")
    print("• 1 saved scenario → 'Download Excel File' button")
    print("• 2+ saved scenarios → 'Download ZIP with All Scenarios' button")
    print("• Each file is complete and can be shared independently")
    print("• Perfect for stakeholder presentations and documentation")
    
    print()
    print("✨ Implementation Complete!")
    print("🚀 Ready for production use!")


if __name__ == "__main__":
    demo_multi_scenario_export()
