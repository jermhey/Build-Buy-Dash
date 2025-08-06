"""
Enhanced Analytics Features for Build vs Buy Dashboard
Adds advanced visualization and analysis capabilities
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


class AdvancedAnalytics:
    """Advanced analytics and visualization features."""
    
    def create_waterfall_chart(self, build_costs, buy_costs):
        """Create waterfall chart showing cost breakdown."""
        categories = ['Build Labor', 'Build OpEx', 'Build CapEx', 'Build Misc', 'Buy Total']
        values = [
            build_costs.get('labor', 0),
            build_costs.get('opex', 0), 
            build_costs.get('capex', 0),
            build_costs.get('misc', 0),
            -buy_costs.get('total', 0)  # Negative to show as alternative
        ]
        
        fig = go.Figure(go.Waterfall(
            name="Cost Analysis",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=categories,
            textposition="outside",
            text=[f"${v:,.0f}" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Build vs Buy Cost Waterfall Analysis",
            showlegend=False,
            height=500
        )
        
        return fig
    
    def create_tornado_chart(self, sensitivity_data):
        """Create tornado chart for sensitivity analysis."""
        fig = go.Figure()
        
        for i, (param, low, high) in enumerate(sensitivity_data):
            fig.add_trace(go.Bar(
                name=param,
                y=[param],
                x=[high - low],
                orientation='h',
                marker_color=px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)]
            ))
        
        fig.update_layout(
            title="Sensitivity Analysis - Impact on NPV",
            xaxis_title="NPV Change Range ($)",
            yaxis_title="Parameters",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_risk_heatmap(self, scenarios):
        """Create risk vs return heatmap."""
        if not scenarios:
            return go.Figure()
        
        # Extract risk and return data
        x_values = [s.get('total_risk', 0) for s in scenarios]
        y_values = [s.get('expected_return', 0) for s in scenarios]
        names = [s.get('name', f'Scenario {i}') for i, s in enumerate(scenarios)]
        
        fig = go.Figure(data=go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers+text',
            text=names,
            textposition="top center",
            marker=dict(
                size=[abs(s.get('npv', 0))/10000 for s in scenarios],
                color=y_values,
                colorscale='RdYlBu',
                showscale=True,
                colorbar=dict(title="Expected Return")
            )
        ))
        
        fig.update_layout(
            title="Risk vs Return Analysis",
            xaxis_title="Total Risk Score",
            yaxis_title="Expected Return ($)",
            height=500
        )
        
        return fig
    
    def create_monte_carlo_distribution(self, simulation_results):
        """Create Monte Carlo distribution visualization."""
        if 'distribution' not in simulation_results:
            return go.Figure()
        
        distribution = simulation_results['distribution']
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Cost Distribution', 'Cumulative Probability'),
            vertical_spacing=0.1
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=distribution, nbinsx=30, name="Cost Distribution"),
            row=1, col=1
        )
        
        # Cumulative distribution
        sorted_values = np.sort(distribution)
        cumulative_prob = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
        
        fig.add_trace(
            go.Scatter(x=sorted_values, y=cumulative_prob, name="Cumulative Probability"),
            row=2, col=1
        )
        
        # Add percentile lines
        p10 = np.percentile(distribution, 10)
        p90 = np.percentile(distribution, 90)
        
        fig.add_vline(x=p10, line_dash="dash", line_color="red", 
                     annotation_text="10th percentile", row=1, col=1)
        fig.add_vline(x=p90, line_dash="dash", line_color="red",
                     annotation_text="90th percentile", row=1, col=1)
        
        fig.update_layout(
            title="Monte Carlo Simulation Results",
            height=600,
            showlegend=False
        )
        
        return fig


class ReportGenerator:
    """Generate comprehensive analysis reports."""
    
    def generate_executive_summary(self, results, scenarios=None):
        """Generate executive summary text."""
        recommendation = results.get('recommendation', 'Unknown')
        build_cost = results.get('expected_build_cost', 0)
        buy_cost = results.get('buy_total_cost', 0)
        savings = abs(build_cost - buy_cost)
        
        summary = f"""
        ## Executive Summary
        
        **Recommendation: {recommendation}**
        
        ### Key Findings:
        - Expected Build Cost: ${build_cost:,.0f}
        - Buy Option Cost: ${buy_cost:,.0f}
        - Potential Savings: ${savings:,.0f}
        
        ### Risk Assessment:
        - 10th Percentile Build Cost: ${results.get('ci_low', 0):,.0f}
        - 90th Percentile Build Cost: ${results.get('ci_high', 0):,.0f}
        - Confidence Interval Width: ${results.get('ci_high', 0) - results.get('ci_low', 0):,.0f}
        
        ### Next Steps:
        1. Validate key assumptions with stakeholders
        2. Conduct detailed risk assessment
        3. Prepare implementation timeline
        4. Secure necessary approvals
        """
        
        return summary
    
    def generate_detailed_analysis(self, results, parameters):
        """Generate detailed technical analysis."""
        return f"""
        ## Detailed Analysis
        
        ### Methodology:
        This analysis used Monte Carlo simulation with {parameters.get('n_simulations', 1000)} iterations
        to model uncertainty in build costs while treating buy costs as deterministic.
        
        ### Assumptions:
        - Build Timeline: {parameters.get('build_timeline', 12)} months
        - Team Size: {parameters.get('fte_count', 3)} FTEs
        - Success Probability: {parameters.get('prob_success', 90)}%
        - Discount Rate (WACC): {parameters.get('wacc', 8)}%
        
        ### Statistical Results:
        - Mean Build Cost: ${results.get('expected_build_cost', 0):,.0f}
        - Standard Deviation: ${results.get('std_dev', 0):,.0f}
        - Coefficient of Variation: {results.get('cv', 0):.1%}
        
        ### Recommendations:
        Based on the analysis, the recommended approach is **{results.get('recommendation', 'Unknown')}**.
        """
