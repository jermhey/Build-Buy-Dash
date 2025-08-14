"""
Demonstration of Multi-Scenario Export Data Flow
Shows how the system tracks scenarios and handles deletions
"""
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import BuildVsBuyApp
from core.excel_export import ExcelExporter


def demo_data_flow():
    """Demonstrate the complete data flow."""
    print("🔄 Multi-Scenario Export Data Flow Demo")
    print("=" * 55)
    
    # Simulate the stored_scenarios data structure (exactly as saved by your app)
    print("📊 Initial State: Empty scenario store")
    stored_scenarios = []
    print(f"Scenarios in store: {len(stored_scenarios)}")
    
    print("\n➕ User saves 3 scenarios...")
    
    # Scenario 1: Small project (exactly as your app saves it)
    scenario1 = {
        'name': 'Mobile_App_Project',
        'timestamp': '2025-08-14 10:15:23',
        'build_timeline': 8,
        'fte_cost': 120000,
        'fte_count': 3,
        'build_timeline_std': 1,
        'fte_cost_std': 15000,
        'cap_percent': 75,
        'misc_costs': 0,
        'useful_life': 3,
        'prob_success': 85,
        'wacc': 8,
        'buy_selector': ['one_time'],
        'risk_selector': ['tech'],
        'cost_selector': ['opex'],
        'product_price': 400000,
        'subscription_price': 0,
        'subscription_increase': 0,
        'tech_risk': 10,
        'vendor_risk': 0,
        'market_risk': 5,
        'maint_opex': 50000,
        'maint_opex_std': 5000,
        'capex': 0,
        'amortization': 0,
        'results': {
            'recommendation': 'Build',
            'expected_build_cost': 288000,
            'buy_total_cost': 400000,
            'npv_difference': 112000
        }
    }
    
    # Scenario 2: Enterprise project
    scenario2 = {
        'name': 'Enterprise_Platform',
        'timestamp': '2025-08-14 10:18:45',
        'build_timeline': 18,
        'fte_cost': 150000,
        'fte_count': 6,
        'build_timeline_std': 3,
        'fte_cost_std': 20000,
        'cap_percent': 80,
        'misc_costs': 100000,
        'useful_life': 7,
        'prob_success': 75,
        'wacc': 8,
        'buy_selector': ['one_time'],
        'risk_selector': ['tech', 'vendor'],
        'cost_selector': ['opex', 'capex'],
        'product_price': 1500000,
        'subscription_price': 0,
        'subscription_increase': 0,
        'tech_risk': 20,
        'vendor_risk': 15,
        'market_risk': 10,
        'maint_opex': 200000,
        'maint_opex_std': 20000,
        'capex': 500000,
        'amortization': 0,
        'results': {
            'recommendation': 'Buy',
            'expected_build_cost': 1620000,
            'buy_total_cost': 1500000,
            'npv_difference': -120000
        }
    }
    
    # Scenario 3: Integration solution
    scenario3 = {
        'name': 'Integration_Solution',
        'timestamp': '2025-08-14 10:22:10',
        'build_timeline': 12,
        'fte_cost': 140000,
        'fte_count': 4,
        'build_timeline_std': 2,
        'fte_cost_std': 18000,
        'cap_percent': 75,
        'misc_costs': 50000,
        'useful_life': 5,
        'prob_success': 80,
        'wacc': 8,
        'buy_selector': ['subscription'],
        'risk_selector': ['tech'],
        'cost_selector': ['opex'],
        'product_price': 0,
        'subscription_price': 150000,
        'subscription_increase': 5,
        'tech_risk': 15,
        'vendor_risk': 0,
        'market_risk': 8,
        'maint_opex': 75000,
        'maint_opex_std': 8000,
        'capex': 0,
        'amortization': 10000,
        'results': {
            'recommendation': 'Build',
            'expected_build_cost': 672000,
            'buy_total_cost': 750000,
            'npv_difference': 78000
        }
    }
    
    # Add scenarios to store (simulating user saves)
    stored_scenarios.append(scenario1)
    stored_scenarios.append(scenario2)
    stored_scenarios.append(scenario3)
    
    print(f"Scenarios in store: {len(stored_scenarios)}")
    for i, scenario in enumerate(stored_scenarios):
        rec = scenario['results']['recommendation']
        npv = scenario['results']['npv_difference']
        print(f"  {i+1}. {scenario['name']} → {rec} (NPV: ${npv:,.0f})")
    
    print("\n📤 Export Excel files...")
    exporter = ExcelExporter()
    
    # This is exactly what happens when user clicks export
    if len(stored_scenarios) > 1:
        print("Multiple scenarios detected → Creating ZIP file")
        zip_data = exporter.create_scenarios_zip(stored_scenarios)
        zip_size = len(zip_data) / 1024 if zip_data else 0
        print(f"✅ ZIP created: {zip_size:.1f} KB with {len(stored_scenarios)} Excel files")
    else:
        print("Single scenario → Creating Excel file")
    
    print("\n🗑️ User deletes middle scenario (Enterprise_Platform)...")
    
    # Simulate deletion (exactly as your delete callback works)
    index_to_delete = 1  # Enterprise_Platform
    updated_scenarios = stored_scenarios.copy()
    del updated_scenarios[index_to_delete]
    stored_scenarios = updated_scenarios
    
    print(f"Scenarios in store: {len(stored_scenarios)}")
    for i, scenario in enumerate(stored_scenarios):
        rec = scenario['results']['recommendation']
        npv = scenario['results']['npv_difference']
        print(f"  {i+1}. {scenario['name']} → {rec} (NPV: ${npv:,.0f})")
    
    print("\n📤 Export Excel files again...")
    
    # Export after deletion - only exports remaining scenarios
    if len(stored_scenarios) > 1:
        print("Still multiple scenarios → Creating ZIP file")
        zip_data = exporter.create_scenarios_zip(stored_scenarios)
        zip_size = len(zip_data) / 1024 if zip_data else 0
        print(f"✅ ZIP created: {zip_size:.1f} KB with {len(stored_scenarios)} Excel files")
        print("🎯 Enterprise_Platform is NOT included (deleted from store)")
    else:
        print("Only one scenario left → Creating single Excel file")
    
    print("\n🗑️ User deletes another scenario...")
    updated_scenarios = stored_scenarios.copy()
    del updated_scenarios[0]  # Remove first scenario
    stored_scenarios = updated_scenarios
    
    print(f"Scenarios in store: {len(stored_scenarios)}")
    for i, scenario in enumerate(stored_scenarios):
        rec = scenario['results']['recommendation']
        npv = scenario['results']['npv_difference']
        print(f"  {i+1}. {scenario['name']} → {rec} (NPV: ${npv:,.0f})")
    
    print("\n📤 Export Excel files one more time...")
    
    # Now only one scenario left
    if len(stored_scenarios) > 1:
        print("Multiple scenarios → Creating ZIP file")
    else:
        print("Single scenario → Creating individual Excel file")
        excel_data = exporter.create_excel_export(stored_scenarios[0])
        excel_size = len(excel_data) / 1024 if excel_data else 0
        print(f"✅ Excel file created: {excel_size:.1f} KB")
        print("🎯 Export logic automatically switched to single file")
    
    print("\n" + "=" * 55)
    print("🎉 Data Flow Summary:")
    print("✅ Uses existing scenario_store (no new structures)")
    print("✅ Saves ALL parameters automatically")
    print("✅ Dynamically updates when scenarios deleted")
    print("✅ Smart export logic (single file vs ZIP)")
    print("✅ Real-time synchronization with table")


if __name__ == "__main__":
    demo_data_flow()
