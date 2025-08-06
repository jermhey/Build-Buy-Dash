"""
Callback handlers for Build vs Buy Dashboard
Separates callback logic from main application class
"""
from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc


class CallbackManager:
    """Manages all Dash callbacks for the Build vs Buy application."""
    
    def __init__(self, app, simulator):
        """
        Initialize callback manager.
        
        Args:
            app: Dash application instance
            simulator: BuildVsBuySimulator instance
        """
        self.app = app
        self.simulator = simulator
        self._register_callbacks()
    
    def _register_callbacks(self):
        """Register all callbacks with the Dash app."""
        self._register_input_callbacks()
        self._register_calculation_callbacks()
        self._register_scenario_callbacks()
        self._register_export_callbacks()
    
    def _register_input_callbacks(self):
        """Register input synchronization callbacks."""
        
        @self.app.callback(
            [Output('risk_inputs', 'children')],
            [Input('risk_selector', 'value')]
        )
        def display_risk_inputs(selected):
            """Display risk input fields based on selection."""
            if not selected:
                return [[]]
            
            children = []
            risk_configs = {
                'tech': ('Technical Risk (%)', 'tech_risk'),
                'vendor': ('Vendor Risk (%)', 'vendor_risk'), 
                'market': ('Market Risk (%)', 'market_risk')
            }
            
            for risk_id in selected:
                if risk_id in risk_configs:
                    label, input_id = risk_configs[risk_id]
                    children.extend([
                        html.Label(label, style={'fontWeight': 'bold', 'marginTop': '10px'}),
                        dcc.Input(id=input_id, type='number', value=0, 
                                style={'width': '100%', 'marginBottom': '10px'})
                    ])
            
            return [children]
    
    def _register_calculation_callbacks(self):
        """Register calculation and results callbacks."""
        
        @self.app.callback(
            [Output('results_div', 'children'),
             Output('chart_div', 'children')],
            [Input('calculate_btn', 'n_clicks')],
            [State('build_timeline', 'value'),
             State('fte_cost', 'value'),
             State('fte_count', 'value'),
             # ... other states
             ]
        )
        def calculate_build_vs_buy(n_clicks, build_timeline, fte_cost, fte_count):
            """Handle calculation button click."""
            if not n_clicks:
                return [], []
            
            # Build parameters
            params = {
                'build_timeline': build_timeline or 12,
                'fte_cost': fte_cost or 130000,
                'fte_count': fte_count or 3,
                # ... other parameters
            }
            
            # Run simulation
            results = self.simulator.simulate(params)
            
            # Generate results display
            results_div = self._create_results_display(results)
            chart_div = self._create_charts(results)
            
            return results_div, chart_div
    
    def _register_scenario_callbacks(self):
        """Register scenario management callbacks."""
        pass  # Implementation would go here
    
    def _register_export_callbacks(self):
        """Register export functionality callbacks."""
        pass  # Implementation would go here
    
    def _create_results_display(self, results):
        """Create results display components."""
        return dbc.Card([
            dbc.CardHeader(html.H4("Analysis Results", className="mb-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"Expected Build Cost: ${results['expected_build_cost']:,.0f}"),
                        html.H5(f"Buy Cost: ${results['buy_total_cost']:,.0f}"),
                        html.H5(f"Recommendation: {results['recommendation']}",
                               className="text-success" if results['recommendation'] == 'Build' else "text-warning")
                    ])
                ])
            ])
        ])
    
    def _create_charts(self, results):
        """Create visualization components."""
        # Implementation would create Plotly charts
        return html.Div("Charts would go here")
