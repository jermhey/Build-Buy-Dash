"""
Modern UI Components for Build vs Buy Dashboard
This module contains enhanced UI layouts while preserving all functionality
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

class ModernUI:
    """Modern UI layout components for the Build vs Buy Dashboard."""
    
    def __init__(self):
        self.theme = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#F18F01',
            'background': '#F8FFFE',
            'card_bg': '#FFFFFF',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'accent': '#E74C3C'
        }
    
    def create_modern_header(self):
        """Create a modern header with gradient background."""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            html.I(className="fas fa-calculator me-3"),
                            "Build vs Buy Decision Platform"
                        ], className="text-white mb-0 fw-bold"),
                        html.P("Advanced Monte Carlo Analysis for Strategic Decision Making", 
                              className="text-white-50 mb-0 fs-6")
                    ])
                ], width=12)
            ])
        ], fluid=True, className="py-4", style={
            'background': f'linear-gradient(135deg, {self.theme["primary"]} 0%, {self.theme["secondary"]} 100%)',
            'marginBottom': '2rem'
        })
    
    def create_parameter_card(self, title, icon, children, color="primary"):
        """Create a modern parameter input card."""
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.I(className=f"fas fa-{icon} me-2"),
                    html.H5(title, className="mb-0 d-inline")
                ], className="d-flex align-items-center")
            ], className=f"bg-{color} text-white"),
            dbc.CardBody(children, className="p-4")
        ], className="shadow-sm mb-4", style={'border': 'none'})
    
    def create_build_parameters_modern(self):
        """Create modern build parameters section."""
        return self.create_parameter_card(
            "Build Configuration", "tools", [
                # Risk Factors
                html.Div([
                    html.Label("Risk Assessment", className="form-label fw-bold mb-2"),
                    html.Small("Select risk factors to include in the analysis. This will show input fields for risk percentages.", 
                              className="text-muted d-block mb-3"),
                    dbc.Checklist(
                        id="risk_selector",
                        options=[
                            {"label": html.Span([
                                html.I(className="fas fa-exclamation-triangle me-2 text-warning"),
                                "Technical Risk"
                            ]), "value": "tech"},
                            {"label": html.Span([
                                html.I(className="fas fa-users me-2 text-info"),
                                "Vendor Risk"
                            ]), "value": "vendor"},
                            {"label": html.Span([
                                html.I(className="fas fa-chart-line me-2 text-success"),
                                "Market Risk"
                            ]), "value": "market"}
                        ],
                        value=[],
                        inline=False,
                        className="mb-3"
                    ),
                    
                    # Dynamic risk inputs will appear here
                    html.Div(id="risk_inputs_display", className="mb-3")
                ]),
                
                html.Hr(),
                
                # Cost Components
                html.Div([
                    html.Label("Cost Components", className="form-label fw-bold mb-3"),
                    dbc.Checklist(
                        id="cost_selector",
                        options=[
                            {"label": html.Span([
                                html.I(className="fas fa-cogs me-2 text-primary"),
                                "Annual Maintenance/OpEx"
                            ]), "value": "opex"},
                            {"label": html.Span([
                                html.I(className="fas fa-money-bill-wave me-2 text-success"),
                                "CapEx Investment"
                            ]), "value": "capex"},
                            {"label": html.Span([
                                html.I(className="fas fa-calendar-alt me-2 text-info"),
                                "Monthly Amortization"
                            ]), "value": "amortization"}
                        ],
                        value=[],
                        inline=False,
                        className="mb-3"
                    ),
                    
                    # Dynamic cost inputs will appear here
                    html.Div(id="cost_inputs_display", className="mb-3")
                ]),
                
                # Core Parameters in Stacked Rows
                html.Hr(),
                html.Label("Core Parameters", className="form-label fw-bold mb-3"),
                
                # Build Timeline Row
                dbc.Row([
                    dbc.Col([
                        html.Label("Build Timeline (months)", className="form-label"),
                        dbc.Input(id="build_timeline", type="number", value=12, step=1,
                                className="form-control-lg"),
                        html.Small("Project duration", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Label("Timeline Uncertainty (±months)", className="form-label"),
                        dbc.Input(id="build_timeline_std", type="number", value=0, step=0.1,
                                className="form-control-lg"),
                        html.Small("Standard deviation", className="text-muted")
                    ], width=6)
                ], className="mb-3"),
                
                # FTE Cost Row
                dbc.Row([
                    dbc.Col([
                        html.Label("FTE Cost ($/year)", className="form-label"),
                        dbc.Input(id="fte_cost", type="number", value=130000, step=1,
                                className="form-control-lg"),
                        html.Small("Annual salary per FTE", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Label("Cost Uncertainty (±$)", className="form-label"),
                        dbc.Input(id="fte_cost_std", type="number", value=15000, step=1,
                                className="form-control-lg"),
                        html.Small("Salary variance", className="text-muted")
                    ], width=6)
                ], className="mb-3"),
                
                # FTE Count Row
                dbc.Row([
                    dbc.Col([
                        html.Label("FTE Count", className="form-label"),
                        dbc.Input(id="fte_count", type="number", value=3, step=1,
                                className="form-control-lg"),
                        html.Small("Team size", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Label("Capitalization (%)", className="form-label"),
                        dbc.Input(id="cap_percent", type="number", value=75, step=1,
                                className="form-control-lg"),
                        html.Small("Capital allocation", className="text-muted")
                    ], width=6)
                ], className="mb-3"),
                
                # Miscellaneous Costs Row
                dbc.Row([
                    dbc.Col([
                        html.Label("Miscellaneous Costs ($)", className="form-label"),
                        dbc.Input(id="misc_costs", type="number", value=0, step=1,
                                className="form-control-lg"),
                        html.Small("Migration, training, setup", className="text-muted")
                    ], width=12)
                ], className="mb-3")
            ]
        )
    
    def create_buy_parameters_modern(self):
        """Create modern buy parameters section."""
        return self.create_parameter_card(
            "Purchase Options", "shopping-cart", [
                html.Div([
                    html.Label("Purchase Model", className="form-label fw-bold mb-3"),
                    dbc.Checklist(
                        id="buy_selector",
                        options=[
                            {"label": html.Span([
                                html.I(className="fas fa-credit-card me-2 text-success"),
                                "One-Time Purchase"
                            ]), "value": "one_time"},
                            {"label": html.Span([
                                html.I(className="fas fa-sync-alt me-2 text-info"),
                                "Annual Subscription"
                            ]), "value": "subscription"}
                        ],
                        value=[],
                        inline=False,
                        className="mb-4"
                    )
                ]),
                
                # Dynamic buy inputs will appear here
                html.Div(id="buy_inputs_display", className="mb-3"),
                
                html.Hr(),
                
                # Analysis Parameters in Stacked Rows
                html.Hr(),
                html.Label("Analysis Parameters", className="form-label fw-bold mb-3"),
                
                # Useful Life and Success Probability Row
                dbc.Row([
                    dbc.Col([
                        html.Label("Useful Life (years)", className="form-label"),
                        dbc.Input(id="useful_life", type="number", value=5, step=1,
                                className="form-control-lg"),
                        html.Small("Project lifespan", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Label("Success Probability (%)", className="form-label"),
                        dbc.Input(id="prob_success", type="number", value=90, step=1,
                                className="form-control-lg"),
                        html.Small("Build success rate", className="text-muted")
                    ], width=6)
                ], className="mb-3"),
                
                # WACC Row
                dbc.Row([
                    dbc.Col([
                        html.Label("WACC (%)", className="form-label"),
                        dbc.Input(id="wacc", type="number", value=8, step=0.1,
                                className="form-control-lg"),
                        html.Small("Discount rate", className="text-muted")
                    ], width=12)
                ], className="mb-3")
            ], color="info"
        )
    
    def create_action_panel_modern(self):
        """Create modern action panel with scenario management."""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Scenario Name", className="form-label fw-bold"),
                        dbc.Input(id="scenario_name", type="text", placeholder="Enter scenario name",
                                className="form-control-lg mb-3")
                    ], width=12)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-play me-2"),
                            "Run Analysis"
                        ], id="calc_btn", color="primary", size="lg", 
                        className="w-100 mb-2", n_clicks=0)
                    ], width=6),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Save Scenario"
                        ], id="save_scenario_btn", color="warning", size="lg",
                        className="w-100 mb-2", n_clicks=0)
                    ], width=6)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-file-excel me-2"),
                            "Export Excel"
                        ], id="download_btn", color="success", size="lg",
                        className="w-100", n_clicks=0)
                    ], width=12)
                ])
            ])
        ], className="shadow-sm mb-4", style={'border': 'none'})
    
    def create_results_panel_modern(self):
        """Create modern results display panel."""
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.I(className="fas fa-chart-bar me-2"),
                    html.H5("Analysis Results", className="mb-0 d-inline")
                ], className="d-flex align-items-center")
            ], className="bg-dark text-white"),
            dbc.CardBody([
                # Results will be populated by callback
                html.Div(id="results_modern", className="mb-4"),
                
                # Enhanced Chart
                dcc.Graph(id="cost_dist_modern", style={
                    "height": "400px",
                    "backgroundColor": "transparent"
                }),
                
                # Scenario Table
                html.Div(id="scenario_table_container_modern", className="mt-4")
            ], className="p-4")
        ], className="shadow-sm", style={'border': 'none'})
    
    def create_modern_layout(self):
        """Create the complete modern layout."""
        return html.Div([
            # Modern Header
            self.create_modern_header(),
            
            # Main Content
            dbc.Container([
                dbc.Row([
                    # Left Column - Parameters
                    dbc.Col([
                        self.create_build_parameters_modern(),
                        self.create_buy_parameters_modern(),
                        self.create_action_panel_modern()
                    ], width=5),
                    
                    # Right Column - Results
                    dbc.Col([
                        self.create_results_panel_modern()
                    ], width=7)
                ])
            ], fluid=True),
            
            # Loading Overlay
            dbc.Modal([
                dbc.ModalBody([
                    html.Div([
                        dbc.Spinner(color="primary", size="lg"),
                        html.H4("Running Monte Carlo Simulation...", className="mt-3 text-center"),
                        html.P("Analyzing 1000+ scenarios", className="text-center text-muted")
                    ], className="text-center p-4")
                ])
            ], id="loading_modal", is_open=False, backdrop="static", keyboard=False),
            
            # Hidden classic components for callback compatibility
            html.Div(id="results", style={"display": "none"}),
            dcc.Graph(id="cost_dist", style={"display": "none"}),
            html.Div(id="scenario_table_container", style={"display": "none"}),
            html.Div(id="risk_inputs", style={"display": "none"}),
            html.Div(id="cost_inputs", style={"display": "none"}),
            html.Div(id="buy_inputs", style={"display": "none"}),
            dcc.Input(id="maint_opex_modern", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="maint_opex_std_modern", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="maint_escalation_modern", type="number", value=3, style={"display": "none"}),
            dcc.Input(id="capex_modern", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="amortization_modern", type="number", value=0, style={"display": "none"}),
            # Hidden buy input components for callback compatibility - always present
            dcc.Input(id="product_price", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="subscription_price", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="subscription_increase", type="number", value=0, style={"display": "none"}),
            # Hidden risk input components for callback compatibility
            dcc.Input(id="tech_risk", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="vendor_risk", type="number", value=0, style={"display": "none"}),
            dcc.Input(id="market_risk", type="number", value=0, style={"display": "none"}),
            
        ], style={
            'backgroundColor': self.theme['background'],
            'minHeight': '100vh',
            'fontFamily': 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
        })

    def get_custom_css(self):
        """Return custom CSS for modern styling."""
        return f"""
        <style>
        .card {{
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }}
        .form-control-lg {{
            border-radius: 8px;
            border: 1px solid #e0e6ed;
        }}
        .form-control-lg:focus {{
            border-color: {self.theme['primary']};
            box-shadow: 0 0 0 0.2rem rgba(46, 134, 171, 0.25);
        }}
        .btn {{
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
        }}
        .btn:hover {{
            transform: translateY(-1px);
        }}
        .text-gradient {{
            background: linear-gradient(135deg, {self.theme['primary']}, {self.theme['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        </style>
        """
