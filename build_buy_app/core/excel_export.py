"""
Fixed Excel Export Module for Build vs Buy Dashboard
Addresses formula corruption issues causing Excel repair warnings
"""
import xlsxwriter
from io import BytesIO
from datetime import datetime


def safe_float(val, default=0.0):
    """Safely convert value to float."""
    try:
        return float(val) if val not in (None, "") else default
    except Exception:
        return default


def safe_cell_ref(cell_ref):
    """Ensure cell reference is properly formatted."""
    if not cell_ref:
        return "A1"
    if isinstance(cell_ref, str) and not cell_ref.startswith("$"):
        return cell_ref
    return str(cell_ref)


def safe_formula(formula):
    """Validate and fix common formula issues."""
    if not formula:
        return "0"
    
    # Remove any None values that might have crept in
    formula = str(formula).replace('None', '0')
    
    # Ensure formula starts with =
    if not formula.startswith('='):
        formula = '=' + formula
        
    # Fix common issues
    formula = formula.replace('+-', '-')  # Fix double operators
    formula = formula.replace('--', '+')  # Fix double negatives
    
    return formula


class ExcelExporter:
    """Fixed Excel export builder for Build vs Buy analysis."""

    INPUT_SHEET = 'Input Parameters'
    TIMELINE_SHEET = 'Cost Timeline'

    def __init__(self):
        """Initialize the Excel exporter."""
        self.param_cells = {}
        self.build_total_row = None
        self.buy_total_row = None
        self.npv_diff_row = None
        self.pv_col_letter = None
        self.scenario_data = {}
    
    def create_excel_export(self, scenario_data, stored_scenarios=None):
        """
        Create comprehensive Excel workbook with validated formulas.
        
        Args:
            scenario_data: Dictionary containing current scenario parameters
            stored_scenarios: List of stored scenario dictionaries
            
        Returns:
            bytes: Excel workbook as bytes
        """
        try:
            output = BytesIO()
            
            # Use more conservative options to prevent corruption
            workbook_options = {
                'strings_to_numbers': False,  # Prevent automatic conversion issues
                'nan_inf_to_errors': True,    # Convert NaN/Inf to Excel errors
                'default_date_format': 'mm/dd/yyyy'
            }
            
            with xlsxwriter.Workbook(output, workbook_options) as workbook:
                # Define formats
                formats = self._create_formats(workbook)
                
                # Store scenario data for reference
                self.scenario_data = scenario_data

                # Create sheets in order
                self._create_input_parameters_sheet(workbook, formats, scenario_data)
                self._create_cost_breakdown_timeline(workbook, formats, scenario_data)
                # Removed executive summary and methodology sheets per user request
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error creating Excel export: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_formats(self, workbook):
        """Create consistent formatting styles."""
        return {
            'header': workbook.add_format({
                'bold': True, 'font_size': 14, 'bg_color': '#4472C4',
                'font_color': 'white', 'align': 'center', 'valign': 'vcenter',
                'border': 1
            }),
            'subheader': workbook.add_format({
                'bold': True, 'font_size': 12, 'bg_color': '#D9E2F3',
                'align': 'center', 'border': 1
            }),
            'currency': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1
            }),
            'currency_bold': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'bold': True, 'border': 1
            }),
            'percent': workbook.add_format({
                'num_format': '0.0%', 'align': 'right', 'border': 1
            }),
            'number': workbook.add_format({
                'num_format': '0.00', 'align': 'right', 'border': 1
            }),
            'text': workbook.add_format({
                'align': 'left', 'border': 1
            }),
            'text_bold': workbook.add_format({
                'bold': True, 'align': 'left', 'border': 1
            }),
            'input_cell': workbook.add_format({
                'bg_color': '#FFFF99', 'border': 1, 'align': 'right'
            }),
            'calculated_cell': workbook.add_format({
                'bg_color': '#C6EFCE', 'border': 1, 'align': 'right', 'num_format': '$#,##0'
            })
        }
    
    def _create_input_parameters_sheet(self, workbook, formats, scenario_data):
        """Create input parameters sheet with safe formulas."""
        worksheet = workbook.add_worksheet(self.INPUT_SHEET)
        row = 0
        
        # Title
        worksheet.merge_range('A1:C1', 'Build vs Buy Analysis - Input Parameters', formats['header'])
        row += 2
        
        # Helper function to add parameter row
        def add_param(label, key, value, description="", format_type="currency"):
            nonlocal row
            worksheet.write_string(row, 0, label, formats['text_bold'])
            
            # Convert percentage values properly
            if format_type == 'percent':
                display_value = safe_float(value) / 100 if safe_float(value) > 1 else safe_float(value)
                worksheet.write_number(row, 1, display_value, formats['input_cell'])
                worksheet.set_column(1, 1, None, formats['percent'])
            else:
                worksheet.write_number(row, 1, safe_float(value), formats['input_cell'])
            
            worksheet.write_string(row, 2, description, formats['text'])
            
            # Store cell reference
            self.param_cells[key] = f"'Input Parameters'!B{row+1}"
            row += 1
        
        # Core parameters
        add_param('Build Timeline (months)', 'build_timeline', scenario_data.get('build_timeline', 12), 'Development duration')
        add_param('FTE Cost (annual)', 'fte_cost', scenario_data.get('fte_cost', 150000), 'Fully loaded annual cost per developer')
        add_param('FTE Count', 'fte_count', scenario_data.get('fte_count', 2), 'Number of developers')
        add_param('Success Probability', 'prob_success', scenario_data.get('prob_success', 80), 'Probability of successful delivery', 'percent')
        add_param('WACC Discount Rate', 'wacc', scenario_data.get('wacc', 10), 'Weighted average cost of capital', 'percent')
        add_param('Useful Life (years)', 'useful_life', scenario_data.get('useful_life', 5), 'Asset useful life')
        
        # Risk factors
        row += 1
        worksheet.write_string(row, 0, 'Risk Factors', formats['subheader'])
        row += 1
        add_param('Technical Risk', 'tech_risk', scenario_data.get('tech_risk', 10), 'Additional cost risk %', 'percent')
        add_param('Vendor Risk', 'vendor_risk', scenario_data.get('vendor_risk', 5), 'Vendor-related cost risk %', 'percent')
        add_param('Market Risk', 'market_risk', scenario_data.get('market_risk', 5), 'Market change risk %', 'percent')
        
        # Cost components
        row += 1
        worksheet.write_string(row, 0, 'Additional Costs', formats['subheader'])
        row += 1
        add_param('CapEx Investment', 'capex', scenario_data.get('capex', 0), 'Infrastructure/hardware costs')
        add_param('Miscellaneous Costs', 'misc_costs', scenario_data.get('misc_costs', 0), 'Other one-time costs')
        add_param('Monthly Amortization', 'amortization', scenario_data.get('amortization', 0), 'Monthly recurring costs during build')
        add_param('Annual Maintenance', 'maint_opex', scenario_data.get('maint_opex', 0), 'Ongoing annual maintenance')
        add_param('Maintenance Escalation', 'maint_escalation', scenario_data.get('maint_escalation', 3), 'Annual maintenance cost increase %', 'percent')
        
        # Calculated values section
        row += 2
        worksheet.write_string(row, 0, 'Calculated Values', formats['subheader'])
        row += 1
        
        # Total FTE Costs calculation with safe formula
        worksheet.write_string(row, 0, 'Total FTE Costs ($)', formats['text_bold'])
        timeline_ref = safe_cell_ref(self.param_cells['build_timeline'])
        fte_cost_ref = safe_cell_ref(self.param_cells['fte_cost'])
        fte_count_ref = safe_cell_ref(self.param_cells['fte_count'])
        prob_success_ref = safe_cell_ref(self.param_cells['prob_success'])
        
        # Safe formula construction - prob_success is stored as decimal (0.8), so no division issues
        formula = f"=({timeline_ref}/12)*{fte_cost_ref}*{fte_count_ref}/{prob_success_ref}"
        worksheet.write_formula(row, 1, safe_formula(formula), formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Total labor costs (success-adjusted)', formats['text'])
        self.param_cells['total_fte_cost'] = f"'Input Parameters'!B{row+1}"
        row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 50)
    
    def _create_cost_breakdown_timeline(self, workbook, formats, scenario_data):
        """Create comprehensive cost timeline with build vs buy comparison."""
        ws = workbook.add_worksheet(self.TIMELINE_SHEET)
        row = 0
        
        # Get core parameters
        useful_life = int(safe_float(scenario_data.get('useful_life', 5)))
        build_timeline = safe_float(scenario_data.get('build_timeline', 12))
        # Dynamic year columns based on useful life (but minimum of 3 for readability)
        max_years = max(3, useful_life + 1)
        
        # Reference key cells safely
        total_fte_ref = safe_cell_ref(self.param_cells.get('total_fte_cost'))
        wacc_ref = safe_cell_ref(self.param_cells.get('wacc'))
        
        # Dynamic headers based on useful life
        year_headers = ['Year 0'] + [f'Year {y}' for y in range(1, max_years + 1)]
        headers = ['Cost Component'] + year_headers + ['Total NPV', 'Notes']
        
        # Merge title across all columns
        last_col_letter = chr(65 + len(headers) - 1)  # Convert to Excel column letter
        ws.merge_range(f'A1:{last_col_letter}1', 'Build vs Buy Cost Analysis Timeline', formats['header'])
        row += 2
        
        for col, header in enumerate(headers):
            ws.write_string(row, col, header, formats['subheader'])
        row += 1
        
        # BUILD COSTS SECTION
        ws.merge_range(f'A{row+1}:B{row+1}', '🏗️ BUILD OPTION COSTS', formats['header'])
        row += 2
        
        # Build costs breakdown with enhanced organization
        build_components = [
            ('Development Labor (Success-Adjusted)', total_fte_ref, 'labor', 'Risk-adjusted labor costs'),
            ('Infrastructure CapEx', self.param_cells.get('capex', "'Input Parameters'!B1"), 'immediate', 'Hardware, software, setup costs'),
            ('Miscellaneous Costs', self.param_cells.get('misc_costs', "'Input Parameters'!B1"), 'immediate', 'Training, migration, other setup'),
            ('Annual Maintenance & Support', self.param_cells.get('maint_opex', "'Input Parameters'!B1"), 'maintenance', 'Ongoing operational costs')
        ]
        
        total_col = 1 + max_years
        npv_col = total_col + 1
        notes_col = npv_col + 1
        
        build_pv_rows = []  # Track rows for total calculation
        
        for comp_name, cost_ref, timing, description in build_components:
            ws.write_string(row, 0, comp_name, formats['text'])
            
            if timing == 'labor':
                # All labor costs in Year 0 for conservative timing
                ws.write_formula(row, 1, safe_formula(f"={cost_ref}"), formats['currency'])
                for year_col in range(2, total_col):
                    ws.write_number(row, year_col, 0, formats['currency'])
                # NPV calculation - no discounting for Year 0
                ws.write_formula(row, npv_col, safe_formula(f"={cost_ref}"), formats['currency_bold'])
            
            elif timing == 'immediate':
                # All cost in Year 0
                ws.write_formula(row, 1, safe_formula(f"={cost_ref}"), formats['currency'])
                for year_col in range(2, total_col):
                    ws.write_number(row, year_col, 0, formats['currency'])
                # NPV calculation - no discounting for Year 0
                ws.write_formula(row, npv_col, safe_formula(f"={cost_ref}"), formats['currency_bold'])
            
            elif timing == 'maintenance':
                # No cost in Year 0, escalating annual costs in subsequent years
                ws.write_number(row, 1, 0, formats['currency'])
                
                # Get maintenance escalation rate
                maint_escalation_ref = safe_cell_ref(self.param_cells.get('maint_escalation'))
                maint_escalation = safe_float(scenario_data.get('maint_escalation', 3)) / 100
                
                # Calculate escalating maintenance costs
                for year_idx in range(1, useful_life + 1):
                    if year_idx + 1 < total_col:
                        year_col = year_idx + 1
                        # Escalated cost formula: base_cost * (1 + escalation_rate)^(year-1)
                        escalated_formula = f"={cost_ref}*(1+{maint_escalation_ref})^({year_idx-1})"
                        ws.write_formula(row, year_col, safe_formula(escalated_formula), formats['currency'])
                
                # Fill remaining years with zeros
                for year_col in range(useful_life + 2, total_col):
                    ws.write_number(row, year_col, 0, formats['currency'])
                
                # NPV calculation for escalating annuity
                if maint_escalation == 0:
                    # Simple annuity if no escalation
                    npv_formula = f"={cost_ref}*((1-(1+{wacc_ref})^-{useful_life})/{wacc_ref})"
                else:
                    # Growing annuity formula for escalating costs
                    npv_formula = f"={cost_ref}*((1-((1+{maint_escalation_ref})/(1+{wacc_ref}))^{useful_life})/({wacc_ref}-{maint_escalation_ref}))"
                
                ws.write_formula(row, npv_col, safe_formula(npv_formula), formats['currency_bold'])
            
            # Add description
            ws.write_string(row, notes_col, description, formats['text'])
            build_pv_rows.append(row)
            row += 1
        
        
        # Risk adjustment calculation - CRITICAL for accuracy
        row += 1
        ws.write_string(row, 0, 'Risk Premium (Additional Cost)', formats['text_bold'])
        
        # Calculate base build costs for risk calculation (exclude maintenance which gets separate treatment)
        # Base costs include: FTE Labor + Infrastructure + Misc costs
        base_build_rows = build_pv_rows[:-1]  # All except maintenance
        base_cost_npv_refs = [f"{chr(65+npv_col)}{r+1}" for r in base_build_rows]
        base_build_npv_formula = "+".join(base_cost_npv_refs)
        
        # Risk multiplier: total_risk_percentage (matches simulation's additive risk model)
        tech_risk_ref = safe_cell_ref(self.param_cells.get('tech_risk'))
        vendor_risk_ref = safe_cell_ref(self.param_cells.get('vendor_risk'))
        market_risk_ref = safe_cell_ref(self.param_cells.get('market_risk'))
        
        # Risk adjustment formula: base_costs * (tech_risk + vendor_risk + market_risk)
        # This gives us the ADDITIONAL cost due to risk, not the total
        risk_formula = f"=({base_build_npv_formula})*({tech_risk_ref}+{vendor_risk_ref}+{market_risk_ref})"
        ws.write_formula(row, npv_col, safe_formula(risk_formula), formats['currency_bold'])
        ws.write_string(row, notes_col, 'Additional cost due to technical, vendor, and market risks', formats['text'])
        
        risk_adjustment_row = row
        row += 2
        
        # Build subtotal and total
        ws.write_string(row, 0, 'TOTAL BUILD COST (NPV)', formats['header'])
        
        # Sum all build components including risk adjustment
        all_build_rows = build_pv_rows + [risk_adjustment_row]
        all_build_npv_refs = [f"{chr(65+npv_col)}{r+1}" for r in all_build_rows]
        total_build_formula = "+".join(all_build_npv_refs)
        ws.write_formula(row, npv_col, safe_formula(f"={total_build_formula}"), formats['currency_bold'])
        ws.write_string(row, notes_col, 'Total build option cost with risk adjustments', formats['text_bold'])
        
        self.build_total_row = row
        row += 3
        
        # BUY COSTS SECTION
        ws.merge_range(f'A{row+1}:B{row+1}', '🛒 BUY OPTION COSTS', formats['header'])
        row += 2
        
        # Get buy parameters
        buy_selector = scenario_data.get('buy_selector', [])
        product_price = safe_float(scenario_data.get('product_price', 0))
        subscription_price = safe_float(scenario_data.get('subscription_price', 0))
        subscription_increase = safe_float(scenario_data.get('subscription_increase', 0)) / 100
        
        buy_pv_rows = []
        
        if 'one_time' in buy_selector and product_price > 0:
            ws.write_string(row, 0, 'Software License/Purchase', formats['text'])
            ws.write_number(row, 1, product_price, formats['currency'])  # Year 0
            for year_col in range(2, total_col):
                ws.write_number(row, year_col, 0, formats['currency'])
            ws.write_number(row, npv_col, product_price, formats['currency_bold'])  # No discounting for Year 0
            ws.write_string(row, notes_col, 'One-time software purchase', formats['text'])
            buy_pv_rows.append(row)
            row += 1
        
        if 'subscription' in buy_selector and subscription_price > 0:
            ws.write_string(row, 0, 'Annual Subscription', formats['text'])
            ws.write_number(row, 1, 0, formats['currency'])  # No cost in Year 0
            
            # Calculate subscription costs with escalation for the useful life period
            for year_idx in range(1, useful_life + 1):
                if year_idx + 1 < total_col:  # Make sure we don't exceed column range
                    year_col = year_idx + 1
                    escalated_cost = subscription_price * ((1 + subscription_increase) ** (year_idx - 1))
                    ws.write_number(row, year_col, escalated_cost, formats['currency'])
            
            # Fill remaining years with zeros if any
            for year_col in range(useful_life + 2, total_col):
                ws.write_number(row, year_col, 0, formats['currency'])
            
            # NPV calculation for subscription
            if subscription_increase == 0:
                # Simple annuity formula
                npv_formula = f"={subscription_price}*((1-(1+{wacc_ref})^-{useful_life})/{wacc_ref})"
            else:
                # Growing annuity formula
                growth_rate = subscription_increase
                npv_formula = f"={subscription_price}*((1-((1+{growth_rate})/(1+{wacc_ref}))^{useful_life})/({wacc_ref}-{growth_rate}))"
            
            ws.write_formula(row, npv_col, safe_formula(npv_formula), formats['currency_bold'])
            ws.write_string(row, notes_col, f'Subscription with {subscription_increase*100:.1f}% annual increase', formats['text'])
            buy_pv_rows.append(row)
            row += 1
        
        # Buy total
        if buy_pv_rows:
            row += 1
            ws.write_string(row, 0, 'TOTAL BUY COST (NPV)', formats['header'])
            buy_npv_refs = [f"{chr(65+npv_col)}{r+1}" for r in buy_pv_rows]
            total_buy_formula = "+".join(buy_npv_refs) if buy_npv_refs else "0"
            ws.write_formula(row, npv_col, safe_formula(f"={total_buy_formula}"), formats['currency_bold'])
            ws.write_string(row, notes_col, 'Total buy option cost', formats['text_bold'])
            self.buy_total_row = row
        else:
            # No buy option selected
            row += 1
            ws.write_string(row, 0, 'TOTAL BUY COST (NPV)', formats['header'])
            ws.write_number(row, npv_col, 0, formats['currency_bold'])
            ws.write_string(row, notes_col, 'No buy option configured', formats['text'])
            self.buy_total_row = row
        
        row += 3
        
        # COMPARISON SECTION
        ws.merge_range(f'A{row+1}:B{row+1}', '⚖️ DECISION ANALYSIS', formats['header'])
        row += 2
        
        # NPV Difference
        ws.write_string(row, 0, 'NPV Difference (Build - Buy)', formats['text_bold'])
        build_total_ref = f"{chr(65+npv_col)}{self.build_total_row+1}"
        buy_total_ref = f"{chr(65+npv_col)}{self.buy_total_row+1}"
        difference_formula = f"={build_total_ref}-{buy_total_ref}"
        ws.write_formula(row, npv_col, safe_formula(difference_formula), formats['currency_bold'])
        ws.write_string(row, notes_col, 'Positive = Build costs more, Negative = Buy costs more', formats['text'])
        self.npv_diff_row = row
        row += 1
        
        # Recommendation
        ws.write_string(row, 0, 'Recommendation', formats['text_bold'])
        recommendation_formula = f'=IF({chr(65+npv_col)}{self.npv_diff_row+1}<0,"Build","Buy")'
        ws.write_formula(row, npv_col, safe_formula(recommendation_formula), formats['text_bold'])
        ws.write_string(row, notes_col, 'Based on NPV analysis', formats['text'])
        
        # Enhanced column formatting
        ws.set_column('A:A', 25)  # Component names
        ws.set_column('B:B', 12)  # Year 0
        for col in range(2, total_col):  # Year columns
            ws.set_column(col, col, 12)
        ws.set_column(npv_col, npv_col, 15)  # NPV column
        ws.set_column(notes_col, notes_col, 40)  # Notes column
    
    def _create_executive_summary(self, workbook, formats, scenario_data):
        """Create executive summary sheet."""
        ws = workbook.add_worksheet('Executive Summary')
        row = 0
        
        # Title
        ws.merge_range('A1:D1', 'Executive Summary - Build vs Buy Analysis', formats['header'])
        row += 3
        
        # Key results
        ws.write_string(row, 0, 'Analysis Results', formats['subheader'])
        row += 1
        
        # Build cost reference
        if self.build_total_row:
            build_cost_ref = f"'{self.TIMELINE_SHEET}'!{chr(65+7)}{self.build_total_row+1}"  # Assuming PV column is H
            
            ws.write_string(row, 0, 'Total Build Cost (PV):', formats['text_bold'])
            ws.write_formula(row, 1, f"={build_cost_ref}", formats['currency_bold'])
            row += 1
        
        # Buy cost (simplified)
        product_price = safe_float(scenario_data.get('product_price', 0))
        ws.write_string(row, 0, 'Buy Cost:', formats['text_bold'])
        ws.write_number(row, 1, product_price, formats['currency_bold'])
        row += 1
        
        # Recommendation
        if self.build_total_row:
            recommendation_formula = f'=IF({build_cost_ref}<{product_price},"Build","Buy")'
            ws.write_string(row, 0, 'Recommendation:', formats['text_bold'])
            ws.write_formula(row, 1, safe_formula(recommendation_formula), formats['text_bold'])
        
        # Set column widths
        ws.set_column('A:A', 25)
        ws.set_column('B:B', 15)
    
    def _create_methodology_documentation(self, workbook, formats):
        """Create methodology documentation sheet."""
        ws = workbook.add_worksheet('Methodology')
        row = 0
        
        # Title
        ws.merge_range('A1:C1', 'Calculation Methodology', formats['header'])
        row += 2
        
        methodology_text = [
            'Build Cost Calculation:',
            '1. Labor costs adjusted for probability of success',
            '2. Risk factors applied additively (tech + vendor + market)',
            '3. Present value calculated using WACC discount rate',
            '4. Maintenance costs discounted over useful life',
            '',
            'Risk Model:',
            'Total Risk = Technical Risk + Vendor Risk + Market Risk',
            'Risk-Adjusted Cost = Base Cost × (1 + Total Risk %)',
            '',
            'Present Value Formula:',
            'PV = Future Value / (1 + WACC)^years',
            'For recurring costs: PV = Annual Cost × ((1-(1+WACC)^-n)/WACC)',
        ]
        
        for text in methodology_text:
            if text.endswith(':'):
                ws.write_string(row, 0, text, formats['text_bold'])
            else:
                ws.write_string(row, 0, text, formats['text'])
            row += 1
        
        # Set column width
        ws.set_column('A:A', 60)
