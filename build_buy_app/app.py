"""
Complete Build vs Buy Dashboard - Production Version
Clean, maintainable architecture with separated concerns
"""
import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, dash_table, no_update, ALL
import dash_bootstrap_components as dbc
from ui.modern_ui import ModernUI
from core.excel_export import ExcelExporter
from data.config_manager import app_config, user_prefs, template_manager
from data.scenario_manager import scenario_manager, ScenarioComparison
from core.advanced_analytics import AdvancedAnalytics, ReportGenerator
from src.simulation import BuildVsBuySimulator
import plotly.graph_objects as go


def safe_float(val, default=0.0):
    """Safely convert value to float."""
    try:
        return float(val) if val not in (None, "") else default
    except Exception:
        return default


class BuildVsBuyApp:
    """Complete Build vs Buy Dashboard Application."""
    
    def __init__(self):
        """Initialize the Dash app."""
        self.app = dash.Dash(
            __name__, 
            external_stylesheets=[dbc.themes.FLATLY,
                                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'],
            suppress_callback_exceptions=True,
            serve_locally=True,  # Serve assets locally to avoid loading issues
            assets_ignore=r'.*\.map$'  # Ignore source map files that can cause conflicts
        )
        
        # Configure server settings for better asset handling
        self.app.server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development
        
        # Initialize modules
        self.modern_ui = ModernUI()
        self.excel_exporter = ExcelExporter()
        self.advanced_analytics = AdvancedAnalytics()
        self.simulator = BuildVsBuySimulator()
        self.current_results = {}
        
        self.setup_layout()
        self.setup_callbacks()
        self.setup_scenario_callbacks()
    
    def setup_layout(self):
        """Set up the main layout structure."""
        self.app.layout = html.Div([
            dcc.Store(id="scenario_store", data=[], storage_type='session'),
            dcc.Download(id="download_csv"),
            self.modern_ui.create_modern_layout()
        ], style={
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "backgroundColor": "#f4f6f8",
            "padding": "24px"
        })
    
    def setup_callbacks(self):
        """Set up the main calculation callbacks."""
        
        # Main calculation callback - including all dynamic inputs
        @self.app.callback(
            [Output('results_modern', 'children'),
             Output('cost_dist_modern', 'figure')],
            [Input('calc_btn', 'n_clicks')],
            [State('build_timeline', 'value'),
             State('fte_cost', 'value'),
             State('fte_count', 'value'),
             State('build_timeline_std', 'value'),
             State('fte_cost_std', 'value'),
             State('cap_percent', 'value'),
             State('misc_costs', 'value'),
             State('useful_life', 'value'),
             State('prob_success', 'value'),
             State('wacc', 'value'),
             State('buy_selector', 'value'),
             State('risk_selector', 'value'),
             State('cost_selector', 'value'),
             # Dynamic buy option inputs - using correct IDs from UI
             State('product_price', 'value'),
             State('subscription_price', 'value'),
             State('subscription_increase', 'value'),
             # Dynamic risk inputs
             State('tech_risk', 'value'),
             State('vendor_risk', 'value'),
             State('market_risk', 'value'),
             # Dynamic cost inputs
             State('maint_opex_modern', 'value'),
             State('maint_opex_std_modern', 'value'),
             State('maint_escalation_modern', 'value'),
             State('capex_modern', 'value'),
             State('amortization_modern', 'value')],
            prevent_initial_call=True
        )
        def update_modern_calculations(n_clicks, build_timeline, fte_cost, fte_count, 
                                     build_timeline_std, fte_cost_std, cap_percent, misc_costs,
                                     useful_life, prob_success, wacc, buy_selector, 
                                     risk_selector, cost_selector,
                                     product_price, subscription_price, subscription_increase,
                                     tech_risk, vendor_risk, market_risk,
                                     maint_opex, maint_opex_std, maint_escalation, capex, amortization):
            """Update calculations using modern UI inputs."""
            if not n_clicks:
                return [html.Div("Click 'Run Analysis' to see results")], {}
            
            try:
                # Debug: Print received values
                print(f"DEBUG - Core build parameters:")
                print(f"  build_timeline: {build_timeline}")
                print(f"  fte_cost: {fte_cost}")
                print(f"  fte_count: {fte_count}")
                print(f"  cap_percent: {cap_percent}")
                print(f"  prob_success: {prob_success}")
                print(f"  wacc: {wacc}")
                
                print(f"DEBUG - Dynamic values:")
                print("DEBUG - Dynamic values:")
                print(f"  product_price: {product_price}")
                print(f"  subscription_price: {subscription_price}")
                print(f"  subscription_increase: {subscription_increase}")
                print(f"  tech_risk: {tech_risk}")
                print(f"  vendor_risk: {vendor_risk}")
                print(f"  market_risk: {market_risk}")
                print(f"  maint_opex: {maint_opex}")
                print(f"  capex: {capex}")
                print(f"  amortization: {amortization}")
                print(f"DEBUG - Risk selector value: {risk_selector}")
                print(f"DEBUG - Individual risk values: tech={tech_risk}, vendor={vendor_risk}, market={market_risk}")
                
                # Prepare parameters using actual input values
                params = {
                    'build_timeline': safe_float(build_timeline, 12),
                    'build_timeline_std': safe_float(build_timeline_std, 0),
                    'fte_cost': safe_float(fte_cost, 130000),
                    'fte_cost_std': safe_float(fte_cost_std, 15000),
                    'fte_count': safe_float(fte_count, 3),
                    'cap_percent': safe_float(cap_percent, 75),
                    'misc_costs': safe_float(misc_costs, 0),
                    'useful_life': safe_float(useful_life, 5),
                    'prob_success': safe_float(prob_success, 90),
                    'wacc': safe_float(wacc, 8),
                    'buy_selector': buy_selector or [],
                    'risk_selector': risk_selector or [],
                    'cost_selector': cost_selector or [],
                    # Use actual dynamic input values
                    'product_price': safe_float(product_price, 0),
                    'subscription_price': safe_float(subscription_price, 0),
                    'subscription_increase': safe_float(subscription_increase, 0),
                    'tech_risk': safe_float(tech_risk, 0),
                    'vendor_risk': safe_float(vendor_risk, 0),
                    'market_risk': safe_float(market_risk, 0),
                    'maint_opex': safe_float(maint_opex, 0),
                    'maint_opex_std': safe_float(maint_opex_std, 0),
                    'maint_escalation': safe_float(maint_escalation, 3),
                    'capex': safe_float(capex, 0),
                    'amortization': safe_float(amortization, 0)
                }
                
                # Debug: Print final parameters
                print(f"DEBUG - Final parameters sent to simulation:")
                for key, value in params.items():
                    print(f"  {key}: {value}")
                
                # Run simulation
                results = self.simulator.simulate(params)
                self.current_results = results
                
                # Return results and chart
                return [self.create_results_display(results), self.create_chart_figure(results)]
                
            except Exception as e:
                error_msg = f"Error in calculation: {str(e)}"
                print(error_msg)
                return [html.Div(error_msg, className="alert alert-danger")], {}
        
        # Excel download callback
        @self.app.callback(
            Output("download_csv", "data"),
            [Input("download_btn", "n_clicks")],
            [State("scenario_name", "value"),
             State("scenario_store", "data"),
             State('build_timeline', 'value'),
             State('fte_cost', 'value'),
             State('fte_count', 'value'),
             State('build_timeline_std', 'value'),
             State('fte_cost_std', 'value'),
             State('cap_percent', 'value'),
             State('misc_costs', 'value'),
             State('useful_life', 'value'),
             State('prob_success', 'value'),
             State('wacc', 'value'),
             State('buy_selector', 'value'),
             State('risk_selector', 'value'),
             State('cost_selector', 'value'),
             # Dynamic inputs - using correct IDs
             State('product_price', 'value'),
             State('subscription_price', 'value'),
             State('subscription_increase', 'value'),
             State('tech_risk', 'value'),
             State('vendor_risk', 'value'),
             State('market_risk', 'value'),
             State('maint_opex_modern', 'value'),
             State('maint_opex_std_modern', 'value'),
             State('maint_escalation_modern', 'value'),
             State('capex_modern', 'value'),
             State('amortization_modern', 'value')]
        )
        def download_excel(n_clicks, scenario_name, stored_scenarios, 
                          build_timeline, fte_cost, fte_count, build_timeline_std,
                          fte_cost_std, cap_percent, misc_costs, useful_life,
                          prob_success, wacc, buy_selector, risk_selector, cost_selector,
                          product_price, subscription_price, subscription_increase,
                          tech_risk, vendor_risk, market_risk,
                          maint_opex, maint_opex_std, maint_escalation, capex, amortization):
            """Generate and download Excel report using the most recent scenario."""
            if not n_clicks:
                return no_update
            
            try:
                print(f"Excel export button clicked. Stored scenarios count: {len(stored_scenarios) if stored_scenarios else 0}")
                
                # Use the most recent scenario from the table if available
                if stored_scenarios and len(stored_scenarios) > 0:
                    # Get the most recent scenario (last in the list)
                    most_recent_scenario = stored_scenarios[-1]
                    print(f"Using most recent scenario: {most_recent_scenario.get('name', 'Unnamed')}")
                    
                    # Use the stored scenario data
                    scenario_data = {
                        'name': most_recent_scenario.get('name', 'Recent_Scenario'),
                        'timestamp': pd.Timestamp.now().strftime('%Y%m%d_%H%M%S'),
                        'results': most_recent_scenario.get('results', self.current_results),
                        'build_timeline': most_recent_scenario.get('build_timeline', build_timeline),
                        'fte_cost': most_recent_scenario.get('fte_cost', fte_cost),
                        'fte_count': most_recent_scenario.get('fte_count', fte_count),
                        'build_timeline_std': most_recent_scenario.get('build_timeline_std', build_timeline_std),
                        'fte_cost_std': most_recent_scenario.get('fte_cost_std', fte_cost_std),
                        'cap_percent': most_recent_scenario.get('cap_percent', cap_percent),
                        'misc_costs': most_recent_scenario.get('misc_costs', misc_costs),
                        'useful_life': most_recent_scenario.get('useful_life', useful_life),
                        'prob_success': most_recent_scenario.get('prob_success', prob_success),
                        'wacc': most_recent_scenario.get('wacc', wacc),
                        'buy_selector': most_recent_scenario.get('buy_selector', buy_selector or []),
                        'risk_selector': most_recent_scenario.get('risk_selector', risk_selector or []),
                        'cost_selector': most_recent_scenario.get('cost_selector', cost_selector or []),
                        # Include dynamic input values
                        'product_price': most_recent_scenario.get('product_price', product_price),
                        'subscription_price': most_recent_scenario.get('subscription_price', subscription_price),
                        'subscription_increase': most_recent_scenario.get('subscription_increase', subscription_increase),
                        'tech_risk': most_recent_scenario.get('tech_risk', tech_risk),
                        'vendor_risk': most_recent_scenario.get('vendor_risk', vendor_risk),
                        'market_risk': most_recent_scenario.get('market_risk', market_risk),
                        'maint_opex': most_recent_scenario.get('maint_opex', maint_opex),
                        'maint_opex_std': most_recent_scenario.get('maint_opex_std', maint_opex_std),
                        'maint_escalation': most_recent_scenario.get('maint_escalation', maint_escalation),
                        'capex': most_recent_scenario.get('capex', capex),
                        'amortization': most_recent_scenario.get('amortization', amortization)
                    }
                else:
                    # No saved scenarios - use current form values and run simulation if needed
                    print("No saved scenarios - using current form values")
                    
                    if not self.current_results:
                        print("No current results available - running simulation first")
                        # Run simulation with current parameters
                        params = {
                            'build_timeline': safe_float(build_timeline, 12),
                            'fte_cost': safe_float(fte_cost, 130000),
                            'fte_count': safe_float(fte_count, 1),
                            'build_timeline_std': safe_float(build_timeline_std, 0),
                            'fte_cost_std': safe_float(fte_cost_std, 0),
                            'cap_percent': safe_float(cap_percent, 75),
                            'misc_costs': safe_float(misc_costs, 0),
                            'useful_life': safe_float(useful_life, 5),
                            'prob_success': safe_float(prob_success, 90),
                            'wacc': safe_float(wacc, 8),
                            'buy_selector': buy_selector or [],
                            'product_price': safe_float(product_price, 0),
                            'subscription_price': safe_float(subscription_price, 0),
                            'subscription_increase': safe_float(subscription_increase, 0),
                            'tech_risk': safe_float(tech_risk, 0),
                            'vendor_risk': safe_float(vendor_risk, 0),
                            'market_risk': safe_float(market_risk, 0),
                            'maint_opex': safe_float(maint_opex, 0),
                            'maint_opex_std': safe_float(maint_opex_std, 0),
                            'maint_escalation': safe_float(maint_escalation, 3),
                            'capex': safe_float(capex, 0),
                            'amortization': safe_float(amortization, 0)
                        }
                        
                        # Run simulation to get results
                        self.current_results = self.simulator.simulate(params)
                        print(f"Generated results for Excel export: {self.current_results.get('recommendation', 'N/A')}")
                    
                    scenario_data = {
                        'name': scenario_name or 'Current_Analysis',
                        'timestamp': pd.Timestamp.now().strftime('%Y%m%d_%H%M%S'),
                        'results': self.current_results,
                        'build_timeline': safe_float(build_timeline, 12),
                        'fte_cost': safe_float(fte_cost, 130000),
                        'fte_count': safe_float(fte_count, 1),
                        'build_timeline_std': safe_float(build_timeline_std, 0),
                        'fte_cost_std': safe_float(fte_cost_std, 0),
                        'cap_percent': safe_float(cap_percent, 75),
                        'misc_costs': safe_float(misc_costs, 0),
                        'useful_life': safe_float(useful_life, 5),
                        'prob_success': safe_float(prob_success, 90),
                        'wacc': safe_float(wacc, 8),
                        'buy_selector': buy_selector or [],
                        'risk_selector': risk_selector or [],
                        'cost_selector': cost_selector or [],
                        # Include dynamic input values
                        'product_price': safe_float(product_price, 0),
                        'subscription_price': safe_float(subscription_price, 0),
                        'subscription_increase': safe_float(subscription_increase, 0),
                        'tech_risk': safe_float(tech_risk, 0),
                        'vendor_risk': safe_float(vendor_risk, 0),
                        'market_risk': safe_float(market_risk, 0),
                        'maint_opex': safe_float(maint_opex, 0),
                        'maint_opex_std': safe_float(maint_opex_std, 0),
                        'maint_escalation': safe_float(maint_escalation, 3),
                        'capex': safe_float(capex, 0),
                        'amortization': safe_float(amortization, 0)
                    }
                
                print(f"Creating Excel export with scenario: {scenario_data['name']}")
                
                # Create Excel export (note: we no longer pass stored_scenarios since we removed those sheets)
                excel_data = self.excel_exporter.create_excel_export(scenario_data)
                
                if excel_data:
                    filename = f"BuildVsBuy_Analysis_{scenario_data['timestamp']}.xlsx"
                    print(f"Excel export successful, filename: {filename}")
                    return dcc.send_bytes(excel_data, filename)
                else:
                    print("Excel export returned None - check excel_export.py for errors")
                    return no_update
                    
            except Exception as e:
                print(f"Error creating Excel export: {e}")
                import traceback
                traceback.print_exc()
                return no_update
        
        # Dynamic UI callbacks for risk factors
        @self.app.callback(
            Output('risk_inputs_display', 'children'),
            [Input('risk_selector', 'value')]
        )
        def update_risk_inputs(selected_risks):
            """Show risk input fields based on selection."""
            if not selected_risks:
                return []
                
            inputs = []
            risk_configs = {
                'tech': {
                    'label': 'Technical Risk (%)', 
                    'icon': 'exclamation-triangle', 
                    'color': 'warning',
                    'description': 'Risk of technical challenges causing cost overruns'
                },
                'vendor': {
                    'label': 'Vendor Risk (%)', 
                    'icon': 'users', 
                    'color': 'info',
                    'description': 'Risk of vendor delays or price increases'
                },
                'market': {
                    'label': 'Market Risk (%)', 
                    'icon': 'chart-line', 
                    'color': 'success',
                    'description': 'Risk of market changes affecting solution value'
                }
            }
            
            for risk in selected_risks:
                if risk in risk_configs:
                    config = risk_configs[risk]
                    inputs.extend([
                        html.Div([
                            html.Label(config['label'], className="form-label fw-bold mt-3 mb-2"),
                            dbc.InputGroup([
                                dbc.InputGroupText([
                                    html.I(className=f"fas fa-{config['icon']} text-{config['color']}")
                                ]),
                                dbc.Input(
                                    id=f"{risk}_risk_display",  # Different ID to avoid conflict with hidden input
                                    type="number",
                                    placeholder=config['label'],
                                    value=0,
                                    min=0,
                                    max=100,
                                    className="form-control-lg"
                                ),
                                dbc.InputGroupText("%")
                            ], className="mb-2"),
                            html.Small(config['description'], className="text-muted d-block mb-3")
                        ])
                    ])
            
            return inputs
        
        # Sync callbacks to update hidden inputs from display inputs
        @self.app.callback(
            Output('tech_risk', 'value'),
            [Input('tech_risk_display', 'value')],
            prevent_initial_call=True
        )
        def sync_tech_risk(value):
            return value or 0
        
        @self.app.callback(
            Output('vendor_risk', 'value'),
            [Input('vendor_risk_display', 'value')],
            prevent_initial_call=True
        )
        def sync_vendor_risk(value):
            return value or 0
        
        @self.app.callback(
            Output('market_risk', 'value'),
            [Input('market_risk_display', 'value')],
            prevent_initial_call=True
        )
        def sync_market_risk(value):
            return value or 0
        
        # Dynamic UI callbacks for cost components
        @self.app.callback(
            Output('cost_inputs_display', 'children'),
            [Input('cost_selector', 'value')]
        )
        def update_cost_inputs(selected_costs):
            """Show cost input fields based on selection."""
            if not selected_costs:
                return []
                
            inputs = []
            cost_configs = {
                'opex': {
                    'label': 'Annual Maintenance/OpEx ($)', 
                    'icon': 'cogs', 
                    'has_std': True,
                    'has_escalation': True,
                    'description': 'Ongoing annual operational and maintenance costs',
                    'std_description': 'Uncertainty in annual OpEx costs',
                    'escalation_description': 'Annual escalation rate for maintenance costs'
                },
                'capex': {
                    'label': 'CapEx Investment ($)', 
                    'icon': 'building', 
                    'has_std': False,
                    'description': 'One-time capital expenditure for infrastructure'
                },
                'amortization': {
                    'label': 'Monthly Amortization ($)', 
                    'icon': 'calendar-alt', 
                    'has_std': False,
                    'description': 'Monthly recurring costs during build phase'
                }
            }
            
            for cost in selected_costs:
                if cost in cost_configs:
                    config = cost_configs[cost]
                    
                    # Main cost input with label in a container div
                    inputs.append(
                        html.Div([
                            html.Label(config['label'], className="form-label fw-bold mt-3 mb-2"),
                            dbc.InputGroup([
                                dbc.InputGroupText([
                                    html.I(className=f"fas fa-{config['icon']} text-primary"),
                                    "$"
                                ]),
                                dbc.Input(
                                    id=f"maint_{cost}_display" if cost == 'opex' else f"{cost}_display",
                                    type="number",
                                    placeholder=config['label'],
                                    value=0,
                                    min=0,
                                    className="form-control-lg"
                                )
                            ], className="mb-2"),
                            html.Small(config['description'], className="text-muted d-block mb-3")
                        ])
                    )
                    
                    # Standard deviation input for opex with label in a container div
                    if config.get('has_std'):
                        inputs.append(
                            html.Div([
                                html.Label(f"{config['label']} Uncertainty (±$)", className="form-label fw-bold mt-2 mb-2"),
                                dbc.InputGroup([
                                    dbc.InputGroupText([
                                        html.I(className="fas fa-chart-bar text-secondary"),
                                        "± $"
                                    ]),
                                    dbc.Input(
                                        id=f"maint_{cost}_std_display",
                                        type="number",
                                        placeholder="Standard deviation",
                                        value=0,
                                        min=0,
                                        className="form-control-lg"
                                    )
                                ], className="mb-2"),
                                html.Small(config['std_description'], className="text-muted d-block mb-4")
                            ])
                        )
                    
                    # Escalation input for opex
                    if config.get('has_escalation'):
                        inputs.append(
                            html.Div([
                                html.Label("Annual Escalation Rate (%)", className="form-label fw-bold mt-2 mb-2"),
                                dbc.InputGroup([
                                    dbc.InputGroupText([
                                        html.I(className="fas fa-trending-up text-warning"),
                                        "%"
                                    ]),
                                    dbc.Input(
                                        id="maint_escalation_display",
                                        type="number",
                                        placeholder="Annual increase rate",
                                        value=3,
                                        min=0,
                                        max=20,
                                        step=0.1,
                                        className="form-control-lg"
                                    )
                                ], className="mb-2"),
                                html.Small(config['escalation_description'], className="text-muted d-block mb-4")
                            ])
                        )
            
            return inputs
        
        # Sync callbacks to update hidden cost inputs from display inputs
        @self.app.callback(
            Output('maint_opex_modern', 'value'),
            [Input('maint_opex_display', 'value')],
            prevent_initial_call=True
        )
        def sync_maint_opex(value):
            return value or 0
        
        @self.app.callback(
            Output('maint_opex_std_modern', 'value'),
            [Input('maint_opex_std_display', 'value')],
            prevent_initial_call=True
        )
        def sync_maint_opex_std(value):
            return value or 0
        
        @self.app.callback(
            Output('maint_escalation_modern', 'value'),
            [Input('maint_escalation_display', 'value')],
            prevent_initial_call=True
        )
        def sync_maint_escalation(value):
            return value or 3
        
        @self.app.callback(
            Output('capex_modern', 'value'),
            [Input('capex_display', 'value')],
            prevent_initial_call=True
        )
        def sync_capex(value):
            return value or 0
        
        @self.app.callback(
            Output('amortization_modern', 'value'),
            [Input('amortization_display', 'value')],
            prevent_initial_call=True
        )
        def sync_amortization(value):
            return value or 0
        
        # Dynamic UI callbacks for buy options
        @self.app.callback(
            Output('buy_inputs_display', 'children'),
            [Input('buy_selector', 'value')],
            [State('product_price', 'value'),
             State('subscription_price', 'value'),
             State('subscription_increase', 'value')],
            prevent_initial_call=False
        )
        def update_buy_inputs(selected_options, current_product_price, current_subscription_price, current_subscription_increase):
            """Show buy option input fields based on selection, preserving current values."""
            if not selected_options:
                return []
            
            inputs = []
            
            # Use current values if they exist and are not zero/empty, otherwise use defaults
            product_price_value = current_product_price if (current_product_price is not None and current_product_price != 0) else 1000000
            subscription_price_value = current_subscription_price if (current_subscription_price is not None and current_subscription_price != 0) else 100000
            subscription_increase_value = current_subscription_increase if (current_subscription_increase is not None and current_subscription_increase != 0) else 3
            
            if 'one_time' in selected_options:
                inputs.append(
                    html.Div([
                        html.Label("One-Time Purchase Price ($)", className="form-label fw-bold mt-3 mb-2"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-dollar-sign text-success"),
                                "$"
                            ]),
                            dbc.Input(
                                id="product_price_display",
                                type="number",
                                placeholder="One-time purchase price",
                                value=product_price_value,
                                min=0,
                                className="form-control-lg"
                            )
                        ], className="mb-2"),
                        html.Small("Flat fee for permanent software license or product", className="text-muted d-block mb-4")
                    ])
                )

            if 'subscription' in selected_options:
                inputs.extend([
                    html.Div([
                        html.Label("Annual Subscription Price ($)", className="form-label fw-bold mt-3 mb-2"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-calendar text-info"),
                                "$"
                            ]),
                            dbc.Input(
                                id="subscription_price_display",
                                type="number",
                                placeholder="Annual subscription cost",
                                value=subscription_price_value,
                                min=0,
                                className="form-control-lg"
                            )
                        ], className="mb-2"),
                        html.Small("Recurring annual subscription or licensing fee", className="text-muted d-block mb-3")
                    ]),
                    
                    html.Div([
                        html.Label("Annual Price Increase (%)", className="form-label fw-bold mt-2 mb-2"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-percentage text-warning")
                            ]),
                            dbc.Input(
                                id="subscription_increase_display",
                                type="number",
                                placeholder="Annual increase rate",
                                value=subscription_increase_value,
                                min=0,
                                max=50,
                                className="form-control-lg"
                            ),
                            dbc.InputGroupText("%")
                        ], className="mb-2"),
                        html.Small("Expected annual price increase rate", className="text-muted d-block mb-4")
                    ])
                ])
            
            return inputs
        
        # Sync display inputs with hidden inputs for callbacks
        @self.app.callback(
            Output('product_price', 'value'),
            [Input('product_price_display', 'value')],
            prevent_initial_call=True
        )
        def sync_product_price(value):
            return value or 0
        
        @self.app.callback(
            Output('subscription_price', 'value'),
            [Input('subscription_price_display', 'value')],
            prevent_initial_call=True
        )
        def sync_subscription_price(value):
            return value or 0
        
        @self.app.callback(
            Output('subscription_increase', 'value'),
            [Input('subscription_increase_display', 'value')],
            prevent_initial_call=True
        )
        def sync_subscription_increase(value):
            return value or 0
    
    def create_results_display(self, results):
        """Create modern results display."""
        if not results:
            return html.Div("No results to display")
        
        # Main metrics
        build_cost = results.get('expected_build_cost', 0)
        buy_cost = results.get('buy_total_cost', 0)
        recommendation = results.get('recommendation', 'Unknown')
        npv_diff = results.get('npv_difference', 0)
        
        # Create cards for key metrics
        cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${build_cost:,.0f}", className="text-primary"),
                        html.P("Expected Build Cost", className="mb-0")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${buy_cost:,.0f}", className="text-info"),
                        html.P("Buy Cost", className="mb-0")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${npv_diff:,.0f}", 
                               className="text-success" if npv_diff > 0 else "text-warning"),
                        html.P("NPV Difference", className="mb-0")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(recommendation, 
                               className="text-success" if recommendation == "Build" else "text-info"),
                        html.P("Recommendation", className="mb-0")
                    ])
                ], className="text-center")
            ], width=3)
        ], className="mb-4")
        
        # Detailed results table
        details = dbc.Card([
            dbc.CardHeader([
                html.H5("Detailed Analysis", className="mb-0 d-inline me-3"),
                dbc.Badge("Monte Carlo Simulation", color="info", className="fs-6")
            ]),
            dbc.CardBody([
                # Risk Analysis Section
                html.H6("Build Cost Risk Analysis", className="text-primary mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Strong("P10 (Optimistic): "),
                            html.Span(f"${results.get('build_cost_p10', 0):,.0f}", className="text-success")
                        ], className="mb-2"),
                        html.Small("10% chance costs will be below this amount", className="text-muted d-block mb-3"),
                        
                        html.Div([
                            html.Strong("P50 (Most Likely): "),
                            html.Span(f"${results.get('build_cost_p50', 0):,.0f}", className="text-info")
                        ], className="mb-2"),
                        html.Small("50% chance costs will be below this amount (median)", className="text-muted d-block mb-3"),
                        
                        html.Div([
                            html.Strong("P90 (Conservative): "),
                            html.Span(f"${results.get('build_cost_p90', 0):,.0f}", className="text-warning")
                        ], className="mb-2"),
                        html.Small("90% chance costs will be below this amount", className="text-muted d-block")
                    ], width=6),
                    dbc.Col([
                        html.H6("Decision Insights", className="text-secondary mb-3"),
                        
                        # Cost sensitivity analysis
                        html.Div([
                            html.Strong("Cost Variability: "),
                            html.Span(
                                f"±${self._calculate_cost_variability(results):,.0f}",
                                className="text-warning"
                            ),
                            html.Small(" (1 std dev)", className="text-muted")
                        ], className="mb-2"),
                        html.Small("Typical deviation from the expected cost", className="text-muted d-block mb-3"),
                        
                        # Break-even analysis
                        html.Div([
                            html.Strong("Build Budget Range: "),
                            html.Span(f"${results.get('build_cost_p10', 0):,.0f} - ${results.get('build_cost_p90', 0):,.0f}", 
                                    className="text-warning")
                        ], className="mb-2"),
                        html.Small("80% of outcomes will fall within this range", className="text-muted d-block mb-3"),
                        
                        # Risk assessment
                        html.Div([
                            html.Strong("Probability Build Costs Less: "),
                            html.Span(
                                f"{self._calculate_probability_build_costs_less(results):.0f}%" 
                                if results.get('buy_total_cost', 0) > 0 else "N/A",
                                className="text-success" if results.get('npv_difference', 0) > 0 else "text-info"
                            )
                        ], className="mb-2"),
                        html.Small("Likelihood build will cost less than buy option", className="text-muted d-block mb-3"),
                        
                        # Show active risk factors if any
                        html.Div([
                            html.H6("Risk Factors Applied:", className="text-muted mb-2 mt-3") 
                            if (results.get('tech_risk', 0) > 0 or results.get('vendor_risk', 0) > 0 or results.get('market_risk', 0) > 0)
                            else "",
                            html.Div([
                                html.Span([
                                    html.I(className="fas fa-exclamation-triangle text-warning me-1"),
                                    f"Technical: +{results.get('tech_risk', 0):.0f}% cost uncertainty"
                                ], className="d-block mb-1") if results.get('tech_risk', 0) > 0 else "",
                                html.Span([
                                    html.I(className="fas fa-handshake text-info me-1"),
                                    f"Vendor: +{results.get('vendor_risk', 0):.0f}% cost uncertainty"
                                ], className="d-block mb-1") if results.get('vendor_risk', 0) > 0 else "",
                                html.Span([
                                    html.I(className="fas fa-chart-line text-danger me-1"),
                                    f"Market: +{results.get('market_risk', 0):.0f}% cost uncertainty"
                                ], className="d-block mb-1") if results.get('market_risk', 0) > 0 else "",
                            ])
                        ], className="mb-3") if (results.get('tech_risk', 0) > 0 or results.get('vendor_risk', 0) > 0 or results.get('market_risk', 0) > 0) else "",
                        
                        # Decision guidance
                        dbc.Alert([
                            html.I(className="fas fa-lightbulb me-2"),
                            html.Strong("Decision Guidance:"),
                            html.Br(),
                            f"• {results.get('recommendation', 'Build')} option has {abs(results.get('npv_difference', 0)):,.0f} cost advantage",
                            html.Br(),
                            f"• Budget ${results.get('build_cost_p90', 0):,.0f} for conservative build planning",
                            html.Br(),
                            "• Consider non-financial factors (control, expertise, timeline)",
                            html.Br(),
                            "• Review assumptions if results are close"
                        ], color="light", className="mt-3")
                    ], width=6)
                ])
            ])
        ])
        
        return html.Div([cards, details])
    
    def create_chart_figure(self, results):
        """Create chart figure for results visualization."""
        if not results or 'cost_distribution' not in results:
            return {}
        
        # Cost distribution histogram
        cost_dist = results['cost_distribution']
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=cost_dist,
            nbinsx=50,
            name='Build Cost Distribution',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Add buy cost line
        buy_cost = results.get('buy_total_cost', 0)
        if buy_cost > 0:
            fig.add_vline(
                x=buy_cost, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Buy Cost: ${buy_cost:,.0f}"
            )
        
        fig.update_layout(
            title="Build Cost Distribution vs Buy Cost",
            xaxis_title="Cost ($)",
            yaxis_title="Frequency",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def setup_scenario_callbacks(self):
        """Setup scenario management callbacks."""
        
        # Save scenario callback
        @self.app.callback(
            Output('scenario_store', 'data'),
            [Input('save_scenario_btn', 'n_clicks')],
            [State('scenario_name', 'value'),
             State('scenario_store', 'data'),
             State('build_timeline', 'value'),
             State('fte_cost', 'value'),
             State('fte_count', 'value'),
             State('build_timeline_std', 'value'),
             State('fte_cost_std', 'value'),
             State('cap_percent', 'value'),
             State('misc_costs', 'value'),
             State('useful_life', 'value'),
             State('prob_success', 'value'),
             State('wacc', 'value'),
             State('buy_selector', 'value'),
             State('risk_selector', 'value'),
             State('cost_selector', 'value'),
             # Add dynamic buy and risk inputs - using correct IDs
             State('product_price', 'value'),
             State('subscription_price', 'value'),
             State('subscription_increase', 'value'),
             State('tech_risk', 'value'),
             State('vendor_risk', 'value'),
             State('market_risk', 'value'),
             State('maint_opex_modern', 'value'),
             State('maint_opex_std_modern', 'value'),
             State('capex_modern', 'value'),
             State('amortization_modern', 'value')]
        )
        def save_scenario(n_clicks, scenario_name, stored_scenarios,
                         build_timeline, fte_cost, fte_count, build_timeline_std,
                         fte_cost_std, cap_percent, misc_costs, useful_life,
                         prob_success, wacc, buy_selector, risk_selector, cost_selector,
                         product_price, subscription_price, subscription_increase,
                         tech_risk, vendor_risk, market_risk,
                         maint_opex, maint_opex_std, capex, amortization):
            """Save current scenario to store."""
            if not n_clicks or not scenario_name:
                return stored_scenarios or []
            
            scenario_data = {
                'name': scenario_name,
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': self.current_results,
                'build_timeline': build_timeline,
                'fte_cost': fte_cost,
                'fte_count': fte_count,
                'build_timeline_std': build_timeline_std,
                'fte_cost_std': fte_cost_std,
                'cap_percent': cap_percent,
                'misc_costs': misc_costs,
                'useful_life': useful_life,
                'prob_success': prob_success,
                'wacc': wacc,
                'buy_selector': buy_selector,
                'risk_selector': risk_selector,
                'cost_selector': cost_selector,
                # Include all dynamic inputs
                'product_price': product_price,
                'subscription_price': subscription_price,
                'subscription_increase': subscription_increase,
                'tech_risk': tech_risk,
                'vendor_risk': vendor_risk,
                'market_risk': market_risk,
                'maint_opex': maint_opex,
                'maint_opex_std': maint_opex_std,
                'capex': capex,
                'amortization': amortization
            }
            
            # Add to stored scenarios
            stored_scenarios = stored_scenarios or []
            stored_scenarios.append(scenario_data)
            
            return stored_scenarios
        
        # Update scenario table callback
        @self.app.callback(
            Output('scenario_table_container_modern', 'children'),
            [Input('scenario_store', 'data'),
             Input('results_modern', 'children')]  # Add results as input to trigger updates
        )
        def update_scenario_table(stored_scenarios, results_children):
            """Update the scenario comparison table."""
            if not stored_scenarios:
                return html.Div("No saved scenarios yet. Save a scenario to see comparisons here.", 
                              className="text-muted text-center p-4")
            
            return self.create_scenario_table(stored_scenarios)
        
        # Delete scenario callback for modern buttons
        @self.app.callback(
            Output('scenario_store', 'data', allow_duplicate=True),
            [Input({'type': 'delete-scenario-btn', 'index': ALL}, 'n_clicks')],
            [State('scenario_store', 'data')],
            prevent_initial_call=True
        )
        def delete_scenario(n_clicks_list, stored_scenarios):
            """Handle scenario deletion when delete button is clicked."""
            if not stored_scenarios or not any(n_clicks_list):
                return stored_scenarios or []
            
            # Find which button was clicked
            for i, n_clicks in enumerate(n_clicks_list):
                if n_clicks and n_clicks > 0:
                    # Remove the scenario at index i
                    if 0 <= i < len(stored_scenarios):
                        updated_scenarios = stored_scenarios.copy()
                        del updated_scenarios[i]
                        return updated_scenarios
            
            return stored_scenarios or []
    
    def create_scenario_table(self, scenarios):
        """Create modern scenario table using clean HTML structure."""
        if not scenarios:
            return html.Div("No scenarios saved yet.", className="text-muted text-center py-4")
        
        # Define columns for the table
        columns = [
            {'key': 'action', 'label': '', 'style': {'width': '60px', 'textAlign': 'center'}},
            {'key': 'name', 'label': 'Scenario Name', 'style': {'width': '200px'}},
            {'key': 'build_timeline', 'label': 'Build Timeline', 'style': {'width': '120px', 'textAlign': 'center'}},
            {'key': 'fte_count', 'label': 'FTE Count', 'style': {'width': '100px', 'textAlign': 'center'}},
            {'key': 'fte_cost', 'label': 'FTE Cost', 'style': {'width': '120px', 'textAlign': 'right'}},
            {'key': 'build_cost', 'label': 'Build Cost', 'style': {'width': '140px', 'textAlign': 'right'}},
            {'key': 'buy_cost', 'label': 'Buy Cost', 'style': {'width': '140px', 'textAlign': 'right'}},
            {'key': 'npv_difference', 'label': 'NPV Difference', 'style': {'width': '140px', 'textAlign': 'right'}},
            {'key': 'est_tax_credit', 'label': 'Est. Tax Credit', 'style': {'width': '140px', 'textAlign': 'right'}},
            {'key': 'recommendation', 'label': 'Recommendation', 'style': {'width': '120px', 'textAlign': 'center'}}
        ]
        
        # Create table headers
        header_cells = []
        for col in columns:
            header_style = {
                **col['style'],
                'background': 'linear-gradient(135deg, #2E86AB 0%, #1e5f82 100%)',
                'color': 'white',
                'fontWeight': '600',
                'fontSize': '13px',
                'padding': '12px 8px',
                'border': '1px solid #dee2e6',
                'borderBottom': '2px solid #1e5f82'
            }
            
            # Special styling for delete button column
            if col['key'] == 'action':
                header_style['background'] = '#f8f9fa'
                header_style['color'] = '#6c757d'
            
            header_cells.append(
                html.Th(
                    col['label'],
                    style=header_style
                )
            )
        
        # Create table rows
        table_rows = []
        for i, scenario in enumerate(scenarios):
            # Get actual results from simulation
            results = scenario.get('results', {})
            build_cost = results.get('expected_build_cost', 0)
            buy_cost = results.get('buy_total_cost', 0)
            
            # Use the actual NPV difference from results if available, otherwise calculate
            npv_diff = results.get('npv_difference', 0)
            if npv_diff == 0:  # Fallback calculation if not in results
                npv_diff = build_cost - buy_cost
            
            # Calculate tax credit correctly: 17% of cap_percent of total FTE costs
            # Total FTE cost = FTE cost per year * number of FTEs * build timeline in years
            fte_cost_per_year = scenario.get('fte_cost', 0)
            fte_count = scenario.get('fte_count', 0)
            build_timeline_months = scenario.get('build_timeline', 0)
            build_timeline_years = build_timeline_months / 12
            
            total_fte_costs = fte_cost_per_year * fte_count * build_timeline_years
            cap_rate = scenario.get('cap_percent', 75) / 100  # Use actual cap_percent from scenario
            tax_credit = total_fte_costs * cap_rate * 0.17  # 17% tax credit rate
            
            recommendation = results.get('recommendation', 'Build' if npv_diff < 0 else 'Buy')
            
            # Create row cells
            row_cells = [
                # Delete button cell
                html.Td([
                    html.Button(
                        "×",
                        id={'type': 'delete-scenario-btn', 'index': i},
                        className="delete-btn-modern",
                        style={
                            'backgroundColor': '#dc3545',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '50%',
                            'width': '28px',
                            'height': '28px',
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'cursor': 'pointer',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'transition': 'all 0.2s ease',
                            'margin': '0 auto'
                        }
                    )
                ], style={
                    'textAlign': 'center', 
                    'verticalAlign': 'middle', 
                    'padding': '8px',
                    'backgroundColor': '#ffffff',
                    'border': '1px solid #dee2e6'
                }),
                
                # Data cells
                html.Td(scenario.get('name', f'Scenario {i+1}'), style={
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6',
                    'fontWeight': '500'
                }),
                html.Td(f"{scenario.get('build_timeline', 0):.0f} months", style={
                    'textAlign': 'center',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6'
                }),
                html.Td(f"{scenario.get('fte_count', 0):.0f}", style={
                    'textAlign': 'center',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6'
                }),
                html.Td(f"${scenario.get('fte_cost', 0):,.0f}", style={
                    'textAlign': 'right',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6',
                    'fontFamily': 'Monaco, Consolas, monospace',
                    'fontSize': '13px'
                }),
                html.Td(f"${build_cost:,.0f}", style={
                    'textAlign': 'right',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6',
                    'fontFamily': 'Monaco, Consolas, monospace',
                    'fontSize': '13px'
                }),
                html.Td(f"${buy_cost:,.0f}", style={
                    'textAlign': 'right',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6',
                    'fontFamily': 'Monaco, Consolas, monospace',
                    'fontSize': '13px'
                }),
                html.Td(
                    f"${npv_diff:,.0f}",
                    style={
                        'textAlign': 'right',
                        'padding': '10px 8px',
                        'border': '1px solid #dee2e6',
                        'fontFamily': 'Monaco, Consolas, monospace',
                        'fontSize': '13px',
                        'color': '#dc3545' if npv_diff > 0 else '#28a745',
                        'fontWeight': '600'
                    }
                ),
                html.Td(f"${tax_credit:,.0f}", style={
                    'textAlign': 'right',
                    'padding': '10px 8px',
                    'border': '1px solid #dee2e6',
                    'fontFamily': 'Monaco, Consolas, monospace',
                    'fontSize': '13px'
                }),
                html.Td(
                    recommendation,
                    style={
                        'textAlign': 'center',
                        'padding': '10px 8px',
                        'border': '1px solid #dee2e6',
                        'fontWeight': '600',
                        'color': '#28a745' if recommendation == 'Build' else '#fd7e14'
                    }
                )
            ]
            
            # Create row with hover effect
            table_rows.append(html.Tr(
                row_cells,
                style={
                    'backgroundColor': '#ffffff' if i % 2 == 0 else '#f8f9fa',
                    'transition': 'background-color 0.15s ease'
                },
                className="table-row-hover"
            ))
        
        # Create complete HTML table
        table = html.Table([
            html.Thead([
                html.Tr(header_cells)
            ]),
            html.Tbody(table_rows)
        ], 
        className="modern-html-table",
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
            'backgroundColor': 'white',
            'fontFamily': "'Segoe UI', system-ui, -apple-system, sans-serif",
            'fontSize': '14px'
        })
        
        return html.Div([
            html.Div([
                html.I(className="fas fa-table me-2"),
                html.H5("Saved Scenarios", className="mb-0 d-inline"),
                html.Span(f"({len(scenarios)} scenarios)", className="text-muted ms-2")
            ], className="mb-3 d-flex align-items-center"),
            html.Div([
                table
            ], className="table-responsive", style={'overflowX': 'auto'})
        ])
    
    def _calculate_probability_build_costs_less(self, results):
        """Calculate the probability that build costs less than buy using actual Monte Carlo distribution."""
        cost_distribution = results.get('cost_distribution', [])
        buy_total_cost = results.get('buy_total_cost', 0)
        
        if not cost_distribution or buy_total_cost <= 0:
            return 0.0
        
        # Count how many simulations resulted in build cost < buy cost
        build_costs_less = sum(1 for cost in cost_distribution if cost < buy_total_cost)
        probability = (build_costs_less / len(cost_distribution)) * 100
        
        return max(0, min(100, probability))
    
    def _calculate_cost_variability(self, results):
        """Calculate the standard deviation of the build cost distribution."""
        cost_distribution = results.get('cost_distribution', [])
        
        if not cost_distribution:
            return 0.0
        
        import numpy as np
        return float(np.std(cost_distribution))
    
    def _create_html_scenario_table(self, table_data, columns):
        """Create a modern, styled HTML table as fallback when dash_table has loading issues."""
        if not table_data:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
                    html.H5("No scenarios saved yet", className="text-muted"),
                    html.P("Run an analysis and save it to see scenarios here.", className="text-muted small")
                ], className="text-center py-5")
            ], className="scenario-table-container")
        
        # Create table header with modern styling
        header_cells = []
        for col in columns:
            if col['id'] != 'Delete':  # Skip delete column in header
                # Format column names to be more readable
                display_name = col['name'].replace('_', ' ')
                header_cells.append(html.Th(display_name, className="text-start"))
        
        # Add Actions column for delete button
        header_cells.append(html.Th("Actions", className="text-center"))
        
        # Create table rows with enhanced formatting
        table_rows = [html.Thead(html.Tr(header_cells))]
        tbody_rows = []
        
        for i, row in enumerate(table_data):
            cells = []
            for col in columns:
                if col['id'] == 'Delete':
                    continue  # Skip delete column data, handle in Actions
                
                value = row.get(col['id'], '')
                
                # Format different types of data appropriately
                if col['id'] == 'Recommendation':
                    if value == 'Build':
                        formatted_cell = html.Span(value, className="recommendation-build")
                    elif value == 'Buy':
                        formatted_cell = html.Span(value, className="recommendation-buy")
                    else:
                        formatted_cell = html.Span(value, className="text-muted")
                    cells.append(html.Td(formatted_cell, className="text-center"))
                
                elif col['id'] in ['Build Cost', 'Buy Cost', 'NPV Difference', 'Savings', 'FTE Cost']:
                    # Currency formatting with right alignment
                    cells.append(html.Td(value, className="currency-cell"))
                
                elif col['id'] in ['ROI %', 'Success Prob', 'WACC']:
                    # Percentage formatting
                    cells.append(html.Td(value, className="text-end"))
                
                else:
                    # Default formatting
                    cells.append(html.Td(value))
            
            # Add delete button as last cell
            cells.append(html.Td([
                dbc.Button([
                    html.I(className="fas fa-trash-alt me-1"),
                    "Delete"
                ], 
                color="danger", 
                size="sm", 
                id={"type": "delete-btn", "index": i},
                className="delete-btn-small")
            ], className="text-center"))
            
            tbody_rows.append(html.Tr(cells))
        
        table_rows.append(html.Tbody(tbody_rows))
        
        # Wrap table in responsive container with modern styling
        return html.Div([
            html.Div([
                html.Table(table_rows, className="scenario-table table-hover")
            ], className="table-responsive-custom")
        ], className="scenario-table-container")
    
    
    def run(self, debug=False, host='127.0.0.1', port=8060):
        """Run the Dash app."""
        # Use environment port for production deployment
        import os
        port = int(os.environ.get('PORT', port))
        host = '0.0.0.0' if not debug else host
        
        self.app.run_server(debug=debug, host=host, port=port)


if __name__ == "__main__":
    # Running directly with python app.py
    app = BuildVsBuyApp()
    is_production = os.environ.get('PORT') is not None
    app.run(debug=not is_production, port=int(os.environ.get('PORT', 8060)))
else:
    # Running with Gunicorn - create app instance and expose server
    app = BuildVsBuyApp()
    server = app.app.server
