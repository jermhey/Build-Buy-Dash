"""
Simulation Engine for Build vs Buy Analysis
Extracted from Jupyter notebook for production use
"""
import numpy as np
from typing import Dict, Any, List


class BuildVsBuySimulator:
    """
    Core simulation engine for build vs buy financial analysis.
    Uses Monte Carlo simulation to model uncertainty and risk.
    """
    
    def __init__(self, n_simulations: int = 1000, random_seed: int = 42):
        """
        Initialize the simulator.
        
        Args:
            n_simulations: Number of Monte Carlo simulations to run
            random_seed: Random seed for reproducible results
        """
        self.n_simulations = n_simulations
        self.random_seed = random_seed
    
    def simulate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the build vs buy simulation.
        
        Args:
            params: Dictionary of input parameters
            
        Returns:
            Dictionary containing simulation results
        """
        np.random.seed(self.random_seed)
        
        # Extract and validate parameters
        core_params = self._extract_core_parameters(params)
        risk_params = self._extract_risk_parameters(params)
        cost_params = self._extract_cost_parameters(params)
        buy_params = self._extract_buy_parameters(params)
        
        # Run Monte Carlo simulation for build costs
        build_cost_distribution = self._simulate_build_costs(
            core_params, risk_params, cost_params
        )
        
        # Calculate buy costs (deterministic)
        buy_total_cost = self._calculate_buy_costs(buy_params, core_params)
        
        # Calculate results
        results = self._calculate_results(build_cost_distribution, buy_total_cost)
        
        # Add input parameters to results for tracking and display
        results.update({
            'tech_risk': risk_params.get('tech_risk', 0),
            'vendor_risk': risk_params.get('vendor_risk', 0),
            'market_risk': risk_params.get('market_risk', 0),
            'prob_success': core_params.get('prob_success', 0.8) * 100,  # Convert to percentage
            'confidence_level': 80,  # Standard confidence level for Monte Carlo
            'wacc': core_params.get('wacc', 0.08) * 100,  # Convert to percentage
            'useful_life': core_params.get('useful_life', 5)
        })
        
        return results
    
    def _extract_core_parameters(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Extract and validate core parameters."""
        return {
            'build_timeline': float(params.get('build_timeline', 12.0) or 12.0),
            'build_timeline_std': max(float(params.get('build_timeline_std', 0.0) or 0.0), 0),
            'fte_cost': float(params.get('fte_cost', 150000.0) or 150000.0),
            'fte_cost_std': max(float(params.get('fte_cost_std', 0.0) or 0.0), 0),
            'fte_count': float(params.get('fte_count', 1.0) or 1.0),
            'useful_life': float(params.get('useful_life', 5.0) or 5.0),
            'prob_success': np.clip(float(params.get('prob_success', 80.0) or 80.0) / 100.0, 0.01, 1.0),
            'wacc': float(params.get('wacc', 8.0) or 8.0) / 100.0,
            'misc_costs': float(params.get('misc_costs', 0) or 0)
        }
    
    def _extract_risk_parameters(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Extract risk parameters."""
        return {
            'tech_risk': float(params.get('tech_risk', 0) or 0),
            'vendor_risk': float(params.get('vendor_risk', 0) or 0),
            'market_risk': float(params.get('market_risk', 0) or 0)
        }
    
    def _extract_cost_parameters(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Extract optional cost parameters."""
        return {
            'maint_opex': float(params.get('maint_opex', 0) or 0),
            'maint_opex_std': max(float(params.get('maint_opex_std', 0) or 0), 0),
            'capex': float(params.get('capex', 0) or 0),
            'amortization': float(params.get('amortization', 0) or 0)
        }
    
    def _extract_buy_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract buy-side parameters."""
        return {
            'product_price': float(params.get('product_price', 0) or 0),
            'subscription_price': float(params.get('subscription_price', 0) or 0),
            'subscription_increase': float(params.get('subscription_increase', 0) or 0),
            'buy_selector': params.get('buy_selector', [])
        }
    
    def _simulate_build_costs(self, core_params: Dict, risk_params: Dict, cost_params: Dict) -> np.ndarray:
        """Simulate build costs using Monte Carlo method with improved PV calculations."""
        n_sim = self.n_simulations
        
        # Simulate timeline and FTE cost uncertainty
        timeline_samples = self._generate_samples(
            core_params['build_timeline'], 
            core_params['build_timeline_std'], 
            n_sim
        )
        fte_cost_samples = self._generate_samples(
            core_params['fte_cost'],
            core_params['fte_cost_std'],
            n_sim
        )
        
        # Calculate nominal labor cost over timeline
        timeline_years = timeline_samples / 12
        nominal_labor_cost = timeline_years * fte_cost_samples * core_params['fte_count']
        
        # Apply probability of success adjustment (probability cost adjustment)
        success_adjusted_labor = nominal_labor_cost / core_params['prob_success']
        
        # Apply year-by-year PV discounting for labor costs
        # This is more accurate than end-of-timeline discounting
        labor_cost_pv = self._calculate_labor_pv_year_by_year(
            success_adjusted_labor, timeline_samples, core_params['wacc']
        )
        
        # Add other cost components with appropriate timing
        total_cost_pv = labor_cost_pv
        total_cost_pv += cost_params['capex']  # CapEx (immediate, Year 0)
        total_cost_pv += self._calculate_amortization_pv(cost_params['amortization'], timeline_samples, core_params['wacc'])
        total_cost_pv += self._calculate_opex_pv(cost_params, core_params, n_sim)
        total_cost_pv += core_params['misc_costs']  # Miscellaneous (immediate, Year 0)
        
        # Apply risk factors to base costs (before any additional adjustments)
        total_cost_pv = self._apply_risk_factors(total_cost_pv, risk_params, n_sim)
        
        # Clean up any invalid values
        return self._clean_samples(total_cost_pv)
    
    def _generate_samples(self, mean: float, std: float, n_sim: int) -> np.ndarray:
        """Generate samples with uncertainty, handling edge cases."""
        if std > 0:
            samples = np.random.normal(mean, std, n_sim)
            # Remove negative values
            samples = np.where(samples <= 0, mean, samples)
        else:
            samples = np.full(n_sim, mean)
        return samples
    
    def _calculate_labor_pv_year_by_year(self, nominal_labor: np.ndarray, timeline_samples: np.ndarray, wacc: float) -> np.ndarray:
        """Calculate present value of labor costs with year-by-year discounting."""
        labor_pv = np.zeros_like(nominal_labor)
        
        for i, (labor_cost, timeline_months) in enumerate(zip(nominal_labor, timeline_samples)):
            timeline_years = timeline_months / 12
            
            if timeline_years <= 1:
                # Single year: cost occurs at midpoint of year (6 months)
                pv = labor_cost / ((1 + wacc) ** 0.5)
            else:
                # Multi-year: distribute costs and discount year by year
                pv = 0.0
                years_full = int(timeline_years)
                remaining_fraction = timeline_years - years_full
                
                # Full years: assume costs occur at midpoint of each year
                cost_per_year = labor_cost / timeline_years
                for year in range(years_full):
                    year_midpoint = year + 0.5
                    pv += cost_per_year / ((1 + wacc) ** year_midpoint)
                
                # Partial year: assume costs occur at midpoint of partial year
                if remaining_fraction > 0:
                    partial_year_cost = cost_per_year * remaining_fraction
                    partial_year_midpoint = years_full + (remaining_fraction / 2)
                    pv += partial_year_cost / ((1 + wacc) ** partial_year_midpoint)
            
            labor_pv[i] = pv
        
        return labor_pv
    
    def _calculate_amortization_pv(self, amortization: float, timeline_samples: np.ndarray, wacc: float) -> np.ndarray:
        """Calculate present value of amortization over build timeline."""
        if amortization <= 0:
            return np.zeros(len(timeline_samples))
        
        # Convert annual WACC to monthly rate correctly
        monthly_rate = (1 + wacc) ** (1/12) - 1
        
        amortization_pv = np.zeros(len(timeline_samples))
        for i, timeline in enumerate(timeline_samples):
            months = int(np.round(timeline))
            pv = sum(amortization / ((1 + monthly_rate) ** m) for m in range(1, months + 1))
            amortization_pv[i] = pv
        
        return amortization_pv
    
    def _calculate_opex_pv(self, cost_params: Dict, core_params: Dict, n_sim: int) -> np.ndarray:
        """Calculate present value of operational expenses."""
        maint_opex = cost_params['maint_opex']
        if maint_opex <= 0:
            return np.zeros(n_sim)
        
        # Generate OpEx samples with uncertainty
        opex_samples = self._generate_samples(
            maint_opex,
            cost_params['maint_opex_std'],
            n_sim
        )
        
        # Calculate present value over useful life
        opex_pv = np.zeros(n_sim)
        useful_life = int(np.round(core_params['useful_life']))
        wacc = core_params['wacc']
        
        for i, opex in enumerate(opex_samples):
            pv = sum(opex / ((1 + wacc) ** y) for y in range(1, useful_life + 1))
            opex_pv[i] = pv
        
        return opex_pv
    
    def _apply_risk_factors(self, costs: np.ndarray, risk_params: Dict, n_sim: int) -> np.ndarray:
        """Apply risk factors as multiplicative adjustments with more conservative modeling."""
        # Calculate total risk percentage (additive)
        total_risk_percent = (
            risk_params.get('tech_risk', 0) + 
            risk_params.get('vendor_risk', 0) + 
            risk_params.get('market_risk', 0)
        )
        
        if total_risk_percent <= 0:
            return costs
        
        # Apply risk as a deterministic multiplier for consistency
        # This approach is more predictable and aligns with validation expectations
        risk_multiplier = 1 + (total_risk_percent / 100)
        
        # For Monte Carlo variation, add small stochastic component
        if n_sim > 1:
            # Small random variation around the base multiplier (±5% relative)
            risk_variation = np.random.normal(0, 0.05, n_sim)
            risk_multipliers = risk_multiplier * (1 + risk_variation)
            risk_multipliers = np.clip(risk_multipliers, 1.0, None)  # Ensure >= 1.0
        else:
            risk_multipliers = np.full(n_sim, risk_multiplier)
        
        return costs * risk_multipliers
    
    def _calculate_buy_costs(self, buy_params: Dict, core_params: Dict) -> float:
        """Calculate total buy costs (deterministic)."""
        buy_total_cost = 0.0
        buy_selector = buy_params.get('buy_selector', [])
        
        # One-time purchase
        if 'one_time' in buy_selector:
            buy_total_cost += buy_params['product_price']
        
        # Subscription with escalation
        if 'subscription' in buy_selector:
            subscription_price = buy_params['subscription_price']
            subscription_increase = buy_params['subscription_increase'] / 100.0  # Convert percentage to decimal
            useful_life = int(np.round(core_params['useful_life']))
            wacc = core_params['wacc']
            
            # Calculate NPV of subscription payments
            # Use 1-based indexing to match Excel: payments in years 1,2,3,4,5 for 5-year life
            for year in range(1, useful_life + 1):
                payment = subscription_price * ((1 + subscription_increase) ** (year - 1))
                pv = payment / ((1 + wacc) ** year)  # Discount to present value
                buy_total_cost += pv
        
        return buy_total_cost
    
    def _calculate_results(self, build_cost_distribution: np.ndarray, buy_total_cost: float) -> Dict[str, Any]:
        """Calculate final results and recommendation."""
        expected_build_cost = float(np.mean(build_cost_distribution))
        ci_low = float(np.percentile(build_cost_distribution, 10))
        ci_high = float(np.percentile(build_cost_distribution, 90))
        ci_median = float(np.percentile(build_cost_distribution, 50))
        
        # Calculate risk-adjusted cost (using P90 as conservative estimate)
        risk_adjusted_cost = ci_high
        
        npv_difference = buy_total_cost - expected_build_cost
        recommendation = 'Build' if npv_difference > 0 else 'Buy'
        
        return {
            'expected_build_cost': expected_build_cost,
            'build_cost_p10': ci_low,
            'build_cost_p50': ci_median,
            'build_cost_p90': ci_high,
            'risk_adjusted_cost': risk_adjusted_cost,
            'buy_total_cost': float(buy_total_cost),
            'npv_difference': npv_difference,
            'recommendation': recommendation,
            'cost_distribution': build_cost_distribution.tolist()
        }
    
    def _clean_samples(self, samples: np.ndarray) -> np.ndarray:
        """Clean up invalid values in sample array."""
        # Replace NaN and inf values with mean of valid values
        valid_mask = ~(np.isnan(samples) | np.isinf(samples))
        if np.any(valid_mask):
            mean_valid = np.mean(samples[valid_mask])
            samples = np.where(valid_mask, samples, mean_valid)
        else:
            # If no valid values, return zeros
            samples = np.zeros_like(samples)
        return samples
