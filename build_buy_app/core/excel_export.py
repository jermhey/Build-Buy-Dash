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
    except (ValueError, TypeError, OverflowError) as e:
        # Log specific error types for monitoring
        print(f"Warning: Failed to convert value {val} to float: {e}")
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
    SENSITIVITY_SHEET = 'Sensitivity Analysis'
    BREAKEVEN_SHEET = 'Breakeven Analysis'

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
                self._create_sensitivity_analysis_sheet(workbook, formats, scenario_data)
                self._create_breakeven_analysis_sheet(workbook, formats, scenario_data)
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
            }),
            'sensitivity_control': workbook.add_format({
                'bg_color': '#FFE6CC', 'border': 1, 'align': 'center', 'bold': True
            }),
            'sensitivity_result': workbook.add_format({
                'bg_color': '#E6F3FF', 'border': 1, 'align': 'right', 'num_format': '$#,##0'
            }),
            'green_highlight': workbook.add_format({
                'bg_color': '#C6EFCE', 'border': 1, 'align': 'right', 'num_format': '$#,##0'
            }),
            'red_highlight': workbook.add_format({
                'bg_color': '#FFC7CE', 'border': 1, 'align': 'right', 'num_format': '$#,##0'
            }),
            'small_text': workbook.add_format({
                'font_size': 8, 'align': 'center', 'border': 1
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
        # Dynamic year columns: Year 0 through Year {useful_life} (no extra year)
        max_years = max(3, useful_life)  # Remove the +1 to fix empty column issue
        
        # Reference key cells safely
        total_fte_ref = safe_cell_ref(self.param_cells.get('total_fte_cost'))
        wacc_ref = safe_cell_ref(self.param_cells.get('wacc'))
        
        # Dynamic headers based on useful life
        year_headers = ['Year 0'] + [f'Year {y}' for y in range(1, max_years + 1)]
        headers = ['Cost Component'] + year_headers + ['Total NPV', 'Notes']
        
        # Calculate column positions for better formatting
        total_col = len(year_headers) + 1  # Position of Total NPV column
        npv_col = total_col
        notes_col = npv_col + 1
        
        # Merge title across all columns with enhanced formatting
        last_col_letter = chr(65 + len(headers) - 1)
        ws.merge_range(f'A1:{last_col_letter}1', 'Build vs Buy Cost Analysis Timeline', formats['header'])
        ws.set_row(0, 25)  # Make title row taller
        row += 2
        
        # Create headers with enhanced formatting
        for col, header in enumerate(headers):
            ws.write_string(row, col, header, formats['subheader'])
            # Set column widths for better readability
            if col == 0:  # Cost Component column
                ws.set_column(col, col, 25)
            elif col <= len(year_headers):  # Year columns
                ws.set_column(col, col, 12)
            elif col == npv_col:  # Total NPV column
                ws.set_column(col, col, 15)
            else:  # Notes column
                ws.set_column(col, col, 35)
        
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
        row += 2
        
        # Add BUILD year-by-year totals for analytical insight
        ws.write_string(row, 0, 'Annual Build Costs Summary', formats['text_bold'])
        # Calculate year-by-year totals (excluding risk premium)
        for year_idx in range(len(year_headers)):
            year_col = year_idx + 1
            # Sum all build cost rows for this year
            build_year_refs = [f"{chr(65+year_col)}{r+1}" for r in build_pv_rows]
            if build_year_refs:  # Only if there are costs in this year
                year_total_formula = "+".join(build_year_refs)
                ws.write_formula(row, year_col, safe_formula(f"={year_total_formula}"), formats['currency'])
            else:
                ws.write_number(row, year_col, 0, formats['currency'])
        
        ws.write_string(row, notes_col, 'Annual build costs before risk adjustment', formats['text'])
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
        
        # COMPARISON SECTION with enhanced analytics
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
        
        # Cost Impact percentage
        ws.write_string(row, 0, 'Cost Impact (%)', formats['text_bold'])
        impact_formula = f"={chr(65+npv_col)}{self.npv_diff_row+1}/{buy_total_ref}"
        ws.write_formula(row, npv_col, safe_formula(impact_formula), formats['percent'])
        ws.write_string(row, notes_col, 'Percentage cost difference (negative = savings)', formats['text'])
        row += 1
        
        # Break-even analysis
        ws.write_string(row, 0, 'Break-even Build Cost', formats['text_bold'])
        ws.write_formula(row, npv_col, safe_formula(f"={buy_total_ref}"), formats['currency_bold'])
        ws.write_string(row, notes_col, 'Build cost at which both options are equal', formats['text'])
        row += 1
        
        # Recommendation with enhanced logic
        ws.write_string(row, 0, 'Recommendation', formats['text_bold'])
        recommendation_formula = f'=IF({chr(65+npv_col)}{self.npv_diff_row+1}<0,"Build","Buy")'
        ws.write_formula(row, npv_col, safe_formula(recommendation_formula), formats['text_bold'])
        ws.write_string(row, notes_col, 'Based on NPV analysis considering all risk factors', formats['text'])
        row += 1
        
        # Decision confidence indicator
        ws.write_string(row, 0, 'Decision Confidence', formats['text_bold'])
        confidence_formula = f'=IF(ABS({chr(65+npv_col)}{self.npv_diff_row+1})>{buy_total_ref}*0.1,"High",IF(ABS({chr(65+npv_col)}{self.npv_diff_row+1})>{buy_total_ref}*0.05,"Medium","Low"))'
        ws.write_formula(row, npv_col, safe_formula(confidence_formula), formats['text_bold'])
        ws.write_string(row, notes_col, 'High = >10% difference, Medium = 5-10%, Low = <5%', formats['text'])
        
        # Enhanced column formatting
        ws.set_column('A:A', 25)  # Component names
        ws.set_column('B:B', 12)  # Year 0
        for col in range(2, total_col):  # Year columns
            ws.set_column(col, col, 12)
        ws.set_column(npv_col, npv_col, 15)  # NPV column
        ws.set_column(notes_col, notes_col, 40)  # Notes column
    
    def _create_sensitivity_analysis_sheet(self, workbook, formats, scenario_data):
        """Create comprehensive sensitivity analysis sheet with interactive controls and proper formatting."""
        ws = workbook.add_worksheet(self.SENSITIVITY_SHEET)
        
        # Create special formats for interactive elements
        interactive_format = workbook.add_format({
            'bg_color': '#FFE6CC',  # Orange background
            'border': 1,
            'align': 'center',
            'bold': True,
            'locked': False,  # Allow editing
            'num_format': '0'
        })
        
        interactive_currency_format = workbook.add_format({
            'bg_color': '#FFE6CC',  # Orange background
            'border': 1,
            'align': 'right',
            'bold': True,
            'locked': False,  # Allow editing
            'num_format': '$#,##0'
        })
        
        impact_format = workbook.add_format({
            'bg_color': '#E6F3FF',  # Light blue background
            'border': 1,
            'align': 'center',
            'bold': True,
            'num_format': '0.0'
        })
        
        # Sheet title and description
        ws.merge_range('A1:F1', '📊 Sensitivity Analysis - Interactive Decision Tool', formats['header'])
        ws.write_string(2, 0, 'Adjust parameters below to see real-time impact on Build vs Buy decision', formats['text'])
        
        # Extract base parameters from scenario data
        base_params = {
            'build_timeline': safe_float(scenario_data.get('build_timeline', 12)),
            'fte_cost': safe_float(scenario_data.get('fte_cost', 150000)),
            'fte_count': safe_float(scenario_data.get('fte_count', 2)),
            'prob_success': safe_float(scenario_data.get('prob_success', 80)),
            'wacc': safe_float(scenario_data.get('wacc', 8)),
            'tech_risk': safe_float(scenario_data.get('tech_risk', 0)),
            'vendor_risk': safe_float(scenario_data.get('vendor_risk', 0)),
            'market_risk': safe_float(scenario_data.get('market_risk', 0)),
            'misc_costs': safe_float(scenario_data.get('misc_costs', 0))
        }
        
        # ===========================================
        # SECTION 1: INTERACTIVE PARAMETER CONTROLS
        # ===========================================
        row = 4
        ws.merge_range(f'A{row}:E{row}', '🎛️ INTERACTIVE CONTROLS', formats['subheader'])
        row += 1
        
        # Headers for the controls section
        ws.write_string(row, 0, 'Parameter', formats['text_bold'])
        ws.write_string(row, 1, 'Current Value', formats['text_bold'])
        ws.write_string(row, 2, 'Low Range', formats['text_bold'])
        ws.write_string(row, 3, 'High Range', formats['text_bold'])
        ws.write_string(row, 4, 'Impact Score', formats['text_bold'])
        row += 1
        
        # Store control cell references for both values and ranges
        control_cells = {}
        range_cells = {}
        
        # Define sensitivity range configurations for flexibility
        # These ranges can be easily modified to change how sensitive the analysis is
        # or can be made user-configurable through the UI in future versions
        SENSITIVITY_RANGES = {
            'timeline': {'low_pct': 0.7, 'high_pct': 1.5},      # -30% to +50%
            'fte_cost': {'low_pct': 0.8, 'high_pct': 1.3},      # -20% to +30%
            'team_size': {'low_pct': 0.75, 'high_pct': 1.5},    # -25% to +50%
            'success_prob': {'low_delta': -20, 'high_delta': 15}, # -20% to +15%
            'risk_factor': {'low_delta': -10, 'high_delta': 20}   # -10% to +20%
        }
        
        # Build Timeline Control
        ws.write_string(row, 0, 'Build Timeline (months)', formats['text'])
        timeline_base = safe_float(base_params.get('build_timeline', 12))
        timeline_low = max(1, timeline_base * SENSITIVITY_RANGES['timeline']['low_pct'])
        timeline_high = timeline_base * SENSITIVITY_RANGES['timeline']['high_pct']
        ws.write_number(row, 1, timeline_base, interactive_format)
        ws.write_number(row, 2, timeline_low, interactive_format)
        ws.write_number(row, 3, timeline_high, interactive_format)
        impact_score = ((timeline_high - timeline_low) / timeline_base) * 100
        ws.write_number(row, 4, impact_score, impact_format)
        control_cells['timeline'] = f'B{row+1}'
        range_cells['timeline_low'] = f'C{row+1}'
        range_cells['timeline_high'] = f'D{row+1}'
        row += 1
        
        # FTE Cost Control
        ws.write_string(row, 0, 'FTE Cost (annual)', formats['text'])
        fte_base = safe_float(base_params.get('fte_cost', 150000))
        fte_low = fte_base * SENSITIVITY_RANGES['fte_cost']['low_pct']
        fte_high = fte_base * SENSITIVITY_RANGES['fte_cost']['high_pct']
        ws.write_number(row, 1, fte_base, interactive_currency_format)
        ws.write_number(row, 2, fte_low, interactive_currency_format)
        ws.write_number(row, 3, fte_high, interactive_currency_format)
        impact_score = ((fte_high - fte_low) / fte_base) * 100
        ws.write_number(row, 4, impact_score, impact_format)
        control_cells['fte_cost'] = f'B{row+1}'
        range_cells['fte_cost_low'] = f'C{row+1}'
        range_cells['fte_cost_high'] = f'D{row+1}'
        row += 1
        
        # Team Size Control
        ws.write_string(row, 0, 'Team Size (FTEs)', formats['text'])
        team_base = safe_float(base_params.get('fte_count', 2))
        team_low = max(1, team_base * SENSITIVITY_RANGES['team_size']['low_pct'])
        team_high = team_base * SENSITIVITY_RANGES['team_size']['high_pct']
        ws.write_number(row, 1, team_base, interactive_format)
        ws.write_number(row, 2, team_low, interactive_format)
        ws.write_number(row, 3, team_high, interactive_format)
        impact_score = ((team_high - team_low) / team_base) * 100
        ws.write_number(row, 4, impact_score, impact_format)
        control_cells['team_size'] = f'B{row+1}'
        range_cells['team_size_low'] = f'C{row+1}'
        range_cells['team_size_high'] = f'D{row+1}'
        row += 1
        
        # Success Probability Control
        ws.write_string(row, 0, 'Success Probability (%)', formats['text'])
        success_base = safe_float(base_params.get('prob_success', 80))
        success_low = max(10, success_base + SENSITIVITY_RANGES['success_prob']['low_delta'])
        success_high = min(95, success_base + SENSITIVITY_RANGES['success_prob']['high_delta'])
        ws.write_number(row, 1, success_base, interactive_format)
        ws.write_number(row, 2, success_low, interactive_format)
        ws.write_number(row, 3, success_high, interactive_format)
        impact_score = ((success_high - success_low) / success_base) * 100
        ws.write_number(row, 4, impact_score, impact_format)
        control_cells['success_prob'] = f'B{row+1}'
        range_cells['success_prob_low'] = f'C{row+1}'
        range_cells['success_prob_high'] = f'D{row+1}'
        row += 1
        
        # Risk Factor Control
        risk_base = (safe_float(base_params.get('tech_risk', 0)) + 
                    safe_float(base_params.get('vendor_risk', 0)) + 
                    safe_float(base_params.get('market_risk', 0)))
        risk_low = max(0, risk_base + SENSITIVITY_RANGES['risk_factor']['low_delta'])
        risk_high = risk_base + SENSITIVITY_RANGES['risk_factor']['high_delta']
        ws.write_string(row, 0, 'Combined Risk (%)', formats['text'])
        ws.write_number(row, 1, risk_base, interactive_format)
        ws.write_number(row, 2, risk_low, interactive_format)
        ws.write_number(row, 3, risk_high, interactive_format)
        impact_score = ((risk_high - risk_low) / max(risk_base, 1)) * 100 if risk_base > 0 else 100
        ws.write_number(row, 4, impact_score, impact_format)
        control_cells['risk_factor'] = f'B{row+1}'
        range_cells['risk_factor_low'] = f'C{row+1}'
        range_cells['risk_factor_high'] = f'D{row+1}'
        row += 1
        
        # Miscellaneous Costs Control
        ws.write_string(row, 0, 'Misc Costs ($)', formats['text'])
        ws.write_number(row, 1, base_params['misc_costs'], interactive_currency_format)
        ws.write_number(row, 2, 0, interactive_currency_format)  # Low range (no misc costs)
        ws.write_number(row, 3, base_params['misc_costs'] * 2.0, interactive_currency_format)  # High range
        misc_impact = (base_params['misc_costs'] * 2.0) if base_params['misc_costs'] > 0 else 0
        ws.write_number(row, 4, misc_impact, impact_format)
        control_cells['misc_costs'] = f'B{row+1}'
        range_cells['misc_costs_low'] = f'C{row+1}'
        range_cells['misc_costs_high'] = f'D{row+1}'
        row += 2
        
        # ===========================================
        # SECTION 2: REAL-TIME CALCULATION ENGINE
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '⚡ REAL-TIME RESULTS', formats['subheader'])
        row += 1  # Reduce spacing
        
        # Dynamic build cost calculation
        ws.write_string(row, 0, 'Dynamic Build Cost (PV)', formats['text_bold'])
        timeline_cell = control_cells['timeline']
        fte_cost_cell = control_cells['fte_cost']
        team_size_cell = control_cells['team_size']
        success_cell = control_cells['success_prob']
        
        # Simplified labor cost calculation
        labor_formula = f"=({timeline_cell}/12)*{fte_cost_cell}*{team_size_cell}/({success_cell}/100)"
        ws.write_formula(row, 1, safe_formula(labor_formula), formats['sensitivity_result'])
        ws.write_string(row, 2, 'Labor cost adjusted for success probability', formats['text'])
        build_cost_row = row + 1  # Store for later reference
        row += 1
        
        # Buy cost reference
        buy_cost = safe_float(scenario_data.get('product_price', 0)) + safe_float(scenario_data.get('subscription_price', 0))
        ws.write_string(row, 0, 'Buy Cost (Reference)', formats['text_bold'])
        ws.write_number(row, 1, buy_cost, formats['currency'])
        ws.write_string(row, 2, 'Static reference value', formats['text'])
        buy_cost_row = row + 1  # Store for later reference
        row += 1
        
        # NPV difference calculation
        ws.write_string(row, 0, 'NPV Difference (Build - Buy)', formats['text_bold'])
        npv_diff_formula = f"=B{build_cost_row}-B{buy_cost_row}"
        ws.write_formula(row, 1, safe_formula(npv_diff_formula), formats['sensitivity_result'])
        ws.write_string(row, 2, 'Positive = Build costs more', formats['text'])
        diff_row = row + 1  # Store for later reference
        row += 1
        
        # Recommendation
        ws.write_string(row, 0, 'Recommendation', formats['text_bold'])
        recommendation_formula = f'=IF(B{diff_row}<0,"BUILD","BUY")'
        ws.write_formula(row, 1, safe_formula(recommendation_formula), formats['text_bold'])
        ws.write_string(row, 2, 'Based on cost difference', formats['text'])
        row += 2
        
        # ===========================================
        # SECTION 3: COST DRIVER ANALYSIS - STEP-BY-STEP BREAKDOWN
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '💰 Cost Driver Analysis', formats['subheader'])
        row += 1
        
        # Add explanation
        ws.write_string(row, 0, 'Step-by-step cost calculation showing how each component builds up:', formats['text'])
        row += 2
        
        # Current Scenario Calculation Breakdown
        ws.write_string(row, 0, 'Cost Component', formats['text_bold'])
        ws.write_string(row, 1, 'Current Value', formats['text_bold'])
        ws.write_string(row, 2, 'Calculation Method', formats['text_bold'])
        row += 1
        
        # 1. Core Labor Cost
        ws.write_string(row, 0, '1. Core Labor Cost', formats['text'])
        core_labor_formula = f"=({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}"
        ws.write_formula(row, 1, safe_formula(core_labor_formula), formats['currency'])
        ws.write_string(row, 2, 'Timeline × FTE Cost × Team Size ÷ 12', formats['text'])
        row += 1
        
        # 2. Success-Adjusted Cost  
        ws.write_string(row, 0, '2. Success-Adjusted Cost', formats['text'])
        success_adj_formula = f"={core_labor_formula.replace('=', '')}/({control_cells['success_prob']}/100)"
        ws.write_formula(row, 1, safe_formula(success_adj_formula), formats['currency'])
        ws.write_string(row, 2, 'Core Labor ÷ Success Probability', formats['text'])
        row += 1
        
        # 3. Add Miscellaneous Costs
        ws.write_string(row, 0, '3. Plus Miscellaneous Costs', formats['text'])
        with_misc_formula = f"={success_adj_formula.replace('=', '')}+{control_cells['misc_costs']}"
        ws.write_formula(row, 1, safe_formula(with_misc_formula), formats['currency'])
        ws.write_string(row, 2, 'Success-Adjusted + Misc Costs', formats['text'])
        row += 1
        
        # 4. Final Risk-Adjusted Total
        ws.write_string(row, 0, '4. Final Build Cost (with Risk)', formats['text_bold'])
        total_formula = f"=({with_misc_formula.replace('=', '')})*(1+{control_cells['risk_factor']}/100)"
        ws.write_formula(row, 1, safe_formula(total_formula), formats['currency_bold'])
        ws.write_string(row, 2, '(Adjusted + Misc) × (1 + Risk %)', formats['text_bold'])
        row += 2
        
        # ===========================================
        # SECTION 4: PARAMETER SENSITIVITY ANALYSIS  
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '📈 Parameter Sensitivity Analysis', formats['subheader'])
        row += 1
        
        # Explanation
        ws.write_string(row, 0, 'Each row tests ONE parameter while keeping all others constant:', formats['text'])
        row += 2
        
        # Headers
        ws.write_string(row, 0, 'Parameter Impact', formats['text_bold'])
        ws.write_string(row, 1, 'Optimistic Case', formats['text_bold'])
        ws.write_string(row, 2, 'Current Scenario', formats['text_bold'])
        ws.write_string(row, 3, 'Conservative Case', formats['text_bold'])
        ws.write_string(row, 4, 'Cost Swing', formats['text_bold'])
        row += 1
        
        # Timeline sensitivity - clean label without redundant value ranges
        ws.write_string(row, 0, 'Timeline', formats['text'])
        
        timeline_low_cost = f"=(({range_cells['timeline_low']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        timeline_high_cost = f"=(({range_cells['timeline_high']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        timeline_range_formula = f"={timeline_high_cost.replace('=', '')}-{timeline_low_cost.replace('=', '')}"
        
        ws.write_formula(row, 1, safe_formula(timeline_low_cost), formats['green_highlight'])
        ws.write_formula(row, 2, safe_formula(total_formula), formats['currency'])
        ws.write_formula(row, 3, safe_formula(timeline_high_cost), formats['red_highlight'])
        ws.write_formula(row, 4, safe_formula(timeline_range_formula), formats['currency_bold'])
        row += 1
        
        # FTE Cost sensitivity - clean label without redundant value ranges
        ws.write_string(row, 0, 'Labor Rate', formats['text'])
        
        fte_low_cost = f"=(({control_cells['timeline']}/12)*{range_cells['fte_cost_low']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        fte_high_cost = f"=(({control_cells['timeline']}/12)*{range_cells['fte_cost_high']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        fte_range_formula = f"={fte_high_cost.replace('=', '')}-{fte_low_cost.replace('=', '')}"
        
        ws.write_formula(row, 1, safe_formula(fte_low_cost), formats['green_highlight'])
        ws.write_formula(row, 2, safe_formula(total_formula), formats['currency'])
        ws.write_formula(row, 3, safe_formula(fte_high_cost), formats['red_highlight'])
        ws.write_formula(row, 4, safe_formula(fte_range_formula), formats['currency_bold'])
        row += 1
        
        # Team Size sensitivity - clean label without redundant value ranges
        ws.write_string(row, 0, 'Team Size', formats['text'])
        
        team_low_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{range_cells['team_size_low']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        team_high_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{range_cells['team_size_high']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        team_range_formula = f"={team_high_cost.replace('=', '')}-{team_low_cost.replace('=', '')}"
        
        ws.write_formula(row, 1, safe_formula(team_low_cost), formats['green_highlight'])
        ws.write_formula(row, 2, safe_formula(total_formula), formats['currency'])
        ws.write_formula(row, 3, safe_formula(team_high_cost), formats['red_highlight'])
        ws.write_formula(row, 4, safe_formula(team_range_formula), formats['currency_bold'])
        row += 1
        
        # Success Probability sensitivity - clean label without redundant value ranges
        ws.write_string(row, 0, 'Success Rate', formats['text'])
        
        success_low_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({range_cells['success_prob_low']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        success_high_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({range_cells['success_prob_high']}/100)+{control_cells['misc_costs']})*(1+{control_cells['risk_factor']}/100)"
        success_range_formula = f"={success_low_cost.replace('=', '')}-{success_high_cost.replace('=', '')}"
        
        ws.write_formula(row, 1, safe_formula(success_high_cost), formats['green_highlight'])
        ws.write_formula(row, 2, safe_formula(total_formula), formats['currency'])
        ws.write_formula(row, 3, safe_formula(success_low_cost), formats['red_highlight'])
        ws.write_formula(row, 4, safe_formula(success_range_formula), formats['currency_bold'])
        row += 1
        
        # Risk Factor sensitivity - clean label without redundant value ranges
        ws.write_string(row, 0, 'Risk Premium', formats['text'])
        
        risk_low_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{range_cells['risk_factor_low']}/100)"
        risk_high_cost = f"=(({control_cells['timeline']}/12)*{control_cells['fte_cost']}*{control_cells['team_size']}/({control_cells['success_prob']}/100)+{control_cells['misc_costs']})*(1+{range_cells['risk_factor_high']}/100)"
        risk_range_formula = f"={risk_high_cost.replace('=', '')}-{risk_low_cost.replace('=', '')}"
        
        ws.write_formula(row, 1, safe_formula(risk_low_cost), formats['green_highlight'])
        ws.write_formula(row, 2, safe_formula(total_formula), formats['currency'])
        ws.write_formula(row, 3, safe_formula(risk_high_cost), formats['red_highlight'])
        ws.write_formula(row, 4, safe_formula(risk_range_formula), formats['currency_bold'])
        row += 2
        
        # ===========================================
        # SECTION 5: INSTRUCTIONS AND INTERPRETATION
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '📋 How to Use This Analysis', formats['subheader'])
        row += 1
        
        instructions = [
            "• Orange cells are editable - adjust values to test different scenarios",
            "• Green = optimistic outcomes (lower costs), Red = conservative outcomes (higher costs)", 
            "• Cost Swing shows the dollar impact range for each parameter",
            "• Focus on parameters with the largest cost swings for the biggest decision impact",
            "• All calculations update automatically when you change input values"
        ]
        
        for instruction in instructions:
            ws.write_string(row, 0, instruction, formats['text'])
            row += 1
        
        row += 1
        ws.write_string(row, 0, 'Key Insights:', formats['text_bold'])
        row += 1
        insights = [
            "• Parameters with high cost swings deserve the most attention in planning",
            "• Success probability has inverse relationship: higher % = lower total cost",
            "• Risk factors multiply the base cost, so small % changes have big impacts"
        ]
        
        for insight in insights:
            ws.write_string(row, 0, insight, formats['text'])
            row += 1
        
        # ===========================================
        # COLUMN FORMATTING AND PROTECTION
        # ===========================================
        ws.set_column('A:A', 25)  # Parameter labels
        ws.set_column('B:B', 15)  # Current values
        ws.set_column('C:C', 12)  # Low range values
        ws.set_column('D:D', 12)  # High range values
        ws.set_column('E:E', 15)  # Impact scores/ranges
        
        # Protect the sheet but allow editing of interactive cells
        try:
            ws.protect('SensitivityAnalysis2024', {
                'format_cells': False,
                'format_columns': False,
                'format_rows': False,
                'insert_columns': False,
                'insert_rows': False,
                'insert_hyperlinks': False,
                'delete_columns': False,
                'delete_rows': False,
                'select_locked_cells': True,
                'sort': False,
                'autofilter': False,
                'pivot_tables': False,
                'select_unlocked_cells': True
            })
        except Exception:
            # If protection fails, continue without it
            pass

    def _create_breakeven_analysis_sheet(self, workbook, formats, scenario_data):
        """Create breakeven analysis sheet with interactive controls and styling similar to sensitivity analysis."""
        ws = workbook.add_worksheet(self.BREAKEVEN_SHEET)
        
        # Create special formats for interactive elements (consistent with sensitivity analysis)
        interactive_format = workbook.add_format({
            'bg_color': '#FFE6CC',  # Orange background (same as sensitivity)
            'border': 1,
            'align': 'center',
            'bold': True,
            'locked': False,  # Allow editing
            'num_format': '0'
        })
        
        interactive_currency_format = workbook.add_format({
            'bg_color': '#FFE6CC',  # Orange background
            'border': 1,
            'align': 'right',
            'bold': True,
            'locked': False,  # Allow editing
            'num_format': '$#,##0'
        })
        
        breakeven_result_format = workbook.add_format({
            'bg_color': '#E6F3FF',  # Light blue background (same as sensitivity)
            'border': 1,
            'align': 'right',
            'bold': True,
            'num_format': '$#,##0'
        })
        
        # Sheet title and description
        ws.merge_range('A1:F1', '⚖️ Breakeven Analysis - Find the Tipping Point', formats['header'])
        ws.write_string(2, 0, 'Determine the exact values where Build vs Buy decision changes', formats['text'])
        
        # Extract base parameters from scenario data
        base_params = {
            'build_timeline': safe_float(scenario_data.get('build_timeline', 12)),
            'fte_cost': safe_float(scenario_data.get('fte_cost', 150000)),
            'fte_count': safe_float(scenario_data.get('fte_count', 2)),
            'prob_success': safe_float(scenario_data.get('prob_success', 80)),
            'wacc': safe_float(scenario_data.get('wacc', 8)),
            'tech_risk': safe_float(scenario_data.get('tech_risk', 0)),
            'vendor_risk': safe_float(scenario_data.get('vendor_risk', 0)),
            'market_risk': safe_float(scenario_data.get('market_risk', 0)),
            'misc_costs': safe_float(scenario_data.get('misc_costs', 0)),
            'product_price': safe_float(scenario_data.get('product_price', 0)),
            'subscription_price': safe_float(scenario_data.get('subscription_price', 0))
        }
        
        buy_cost = base_params['product_price'] + base_params['subscription_price']
        
        # ===========================================
        # SECTION 1: CURRENT SCENARIO BASELINE
        # ===========================================
        row = 4
        ws.merge_range(f'A{row}:E{row}', '📊 CURRENT SCENARIO BASELINE', formats['subheader'])
        row += 1
        
        # Current build cost calculation
        ws.write_string(row, 0, 'Current Build Cost (PV)', formats['text_bold'])
        combined_risk = base_params['tech_risk'] + base_params['vendor_risk'] + base_params['market_risk']
        current_build_cost = ((base_params['build_timeline']/12) * base_params['fte_cost'] * 
                             base_params['fte_count'] / (base_params['prob_success']/100) + 
                             base_params['misc_costs']) * (1 + combined_risk/100)
        ws.write_number(row, 1, current_build_cost, formats['currency_bold'])
        current_build_cell = f'B{row+1}'
        row += 1
        
        # Current buy cost
        ws.write_string(row, 0, 'Current Buy Cost', formats['text_bold'])
        ws.write_number(row, 1, buy_cost, formats['currency_bold'])
        current_buy_cell = f'B{row+1}'
        row += 1
        
        # Current difference
        ws.write_string(row, 0, 'Current Difference (Build - Buy)', formats['text_bold'])
        current_diff_formula = f'={current_build_cell}-{current_buy_cell}'
        ws.write_formula(row, 1, safe_formula(current_diff_formula), formats['currency_bold'])
        current_diff_cell = f'B{row+1}'
        row += 1
        
        # Current recommendation
        ws.write_string(row, 0, 'Current Recommendation', formats['text_bold'])
        current_rec_formula = f'=IF({current_diff_cell}<0,"BUILD","BUY")'
        ws.write_formula(row, 1, safe_formula(current_rec_formula), formats['text_bold'])
        row += 2
        
        # ===========================================
        # SECTION 2: BREAKEVEN PARAMETER ANALYSIS
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '🎯 BREAKEVEN PARAMETER ANALYSIS', formats['subheader'])
        row += 1
        
        ws.write_string(row, 0, 'Find the exact parameter value where Build cost equals Buy cost', formats['text'])
        row += 2
        
        # Headers
        ws.write_string(row, 0, 'Parameter', formats['text_bold'])
        ws.write_string(row, 1, 'Current Value', formats['text_bold'])
        ws.write_string(row, 2, 'Breakeven Value', formats['text_bold'])
        ws.write_string(row, 3, 'Change Required', formats['text_bold'])
        ws.write_string(row, 4, 'Interpretation', formats['text_bold'])
        row += 1
        
        # Store breakeven calculation cells for easy reference
        breakeven_cells = {}
        
        # 1. Timeline Breakeven
        ws.write_string(row, 0, 'Build Timeline (months)', formats['text'])
        ws.write_number(row, 1, base_params['build_timeline'], interactive_format)
        
        # Calculate breakeven timeline: solve for timeline where build cost = buy cost
        # Formula: buy_cost = (timeline/12) * fte_cost * fte_count / (prob_success/100) * (1 + risk/100) + misc_costs
        timeline_breakeven = (buy_cost - base_params['misc_costs']) / (
            (base_params['fte_cost'] * base_params['fte_count'] / (base_params['prob_success']/100)) * 
            (1 + combined_risk/100) / 12
        )
        ws.write_number(row, 2, max(0, timeline_breakeven), breakeven_result_format)
        breakeven_cells['timeline'] = f'C{row+1}'
        
        timeline_change_formula = f'={breakeven_cells["timeline"]}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(timeline_change_formula), formats['currency'])
        
        timeline_interp_formula = f'=IF({breakeven_cells["timeline"]}>B{row+1},"Can afford "& ROUND(({breakeven_cells["timeline"]}-B{row+1}),1) &" more months","Need to reduce by "& ROUND((B{row+1}-{breakeven_cells["timeline"]}),1) &" months")'
        ws.write_formula(row, 4, safe_formula(timeline_interp_formula), formats['text'])
        row += 1
        
        # 2. FTE Cost Breakeven
        ws.write_string(row, 0, 'FTE Cost (annual)', formats['text'])
        ws.write_number(row, 1, base_params['fte_cost'], interactive_currency_format)
        
        # Calculate breakeven FTE cost
        fte_cost_breakeven = (buy_cost - base_params['misc_costs']) / (
            (base_params['build_timeline']/12) * base_params['fte_count'] / (base_params['prob_success']/100) * 
            (1 + combined_risk/100)
        )
        ws.write_number(row, 2, max(0, fte_cost_breakeven), breakeven_result_format)
        breakeven_cells['fte_cost'] = f'C{row+1}'
        
        fte_change_formula = f'={breakeven_cells["fte_cost"]}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(fte_change_formula), formats['currency'])
        
        fte_interp_formula = f'=IF({breakeven_cells["fte_cost"]}>B{row+1},"Can afford $"& ROUND(({breakeven_cells["fte_cost"]}-B{row+1}),0) &" more per FTE","Need to reduce by $"& ROUND((B{row+1}-{breakeven_cells["fte_cost"]}),0) &" per FTE")'
        ws.write_formula(row, 4, safe_formula(fte_interp_formula), formats['text'])
        row += 1
        
        # 3. Team Size Breakeven
        ws.write_string(row, 0, 'Team Size (FTEs)', formats['text'])
        ws.write_number(row, 1, base_params['fte_count'], interactive_format)
        
        # Calculate breakeven team size
        team_breakeven = (buy_cost - base_params['misc_costs']) / (
            (base_params['build_timeline']/12) * base_params['fte_cost'] / (base_params['prob_success']/100) * 
            (1 + combined_risk/100)
        )
        ws.write_number(row, 2, max(0, team_breakeven), breakeven_result_format)
        breakeven_cells['team_size'] = f'C{row+1}'
        
        team_change_formula = f'={breakeven_cells["team_size"]}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(team_change_formula), formats['number'])
        
        team_interp_formula = f'=IF({breakeven_cells["team_size"]}>B{row+1},"Can afford "& ROUND(({breakeven_cells["team_size"]}-B{row+1}),1) &" more FTEs","Need to reduce by "& ROUND((B{row+1}-{breakeven_cells["team_size"]}),1) &" FTEs")'
        ws.write_formula(row, 4, safe_formula(team_interp_formula), formats['text'])
        row += 1
        
        # 4. Success Probability Breakeven
        ws.write_string(row, 0, 'Success Probability (%)', formats['text'])
        ws.write_number(row, 1, base_params['prob_success'], interactive_format)
        
        # Calculate breakeven success probability
        # Rearrange: buy_cost = base_labor_cost / (prob_success/100) * (1 + risk) + misc
        base_labor_cost = (base_params['build_timeline']/12) * base_params['fte_cost'] * base_params['fte_count']
        success_breakeven = base_labor_cost * (1 + combined_risk/100) / (buy_cost - base_params['misc_costs']) * 100
        ws.write_number(row, 2, min(100, max(0, success_breakeven)), breakeven_result_format)
        breakeven_cells['success_prob'] = f'C{row+1}'
        
        success_change_formula = f'={breakeven_cells["success_prob"]}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(success_change_formula), formats['number'])
        
        success_interp_formula = f'=IF({breakeven_cells["success_prob"]}>B{row+1},"Need "& ROUND(({breakeven_cells["success_prob"]}-B{row+1}),1) &"% higher confidence","Can tolerate "& ROUND((B{row+1}-{breakeven_cells["success_prob"]}),1) &"% lower confidence")'
        ws.write_formula(row, 4, safe_formula(success_interp_formula), formats['text'])
        row += 2
        
        # ===========================================
        # SECTION 3: BUY COST SCENARIOS
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '💰 BUY COST SCENARIOS', formats['subheader'])
        row += 1
        
        ws.write_string(row, 0, 'Test different buy cost scenarios to see when the decision flips', formats['text'])
        row += 2
        
        # Headers
        ws.write_string(row, 0, 'Buy Cost Scenario', formats['text_bold'])
        ws.write_string(row, 1, 'Buy Cost ($)', formats['text_bold'])
        ws.write_string(row, 2, 'Build Cost ($)', formats['text_bold'])
        ws.write_string(row, 3, 'Difference ($)', formats['text_bold'])
        ws.write_string(row, 4, 'Recommendation', formats['text_bold'])
        row += 1
        
        # Build cost reference for all scenarios
        build_cost_ref = current_build_cost
        
        # Current scenario
        ws.write_string(row, 0, 'Current Buy Cost', formats['text'])
        ws.write_number(row, 1, buy_cost, interactive_currency_format)
        ws.write_number(row, 2, build_cost_ref, formats['currency'])
        current_scenario_diff = f'=C{row+1}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(current_scenario_diff), formats['currency'])
        current_scenario_rec = f'=IF(C{row+1}<B{row+1},"BUILD","BUY")'
        ws.write_formula(row, 4, safe_formula(current_scenario_rec), formats['text_bold'])
        row += 1
        
        # 25% lower buy cost
        low_buy_cost = buy_cost * 0.75
        ws.write_string(row, 0, '25% Lower Buy Cost', formats['text'])
        ws.write_number(row, 1, low_buy_cost, formats['currency'])
        ws.write_number(row, 2, build_cost_ref, formats['currency'])
        low_diff = f'=C{row+1}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(low_diff), formats['currency'])
        low_rec = f'=IF(C{row+1}<B{row+1},"BUILD","BUY")'
        ws.write_formula(row, 4, safe_formula(low_rec), formats['text_bold'])
        row += 1
        
        # 25% higher buy cost
        high_buy_cost = buy_cost * 1.25
        ws.write_string(row, 0, '25% Higher Buy Cost', formats['text'])
        ws.write_number(row, 1, high_buy_cost, formats['currency'])
        ws.write_number(row, 2, build_cost_ref, formats['currency'])
        high_diff = f'=C{row+1}-B{row+1}'
        ws.write_formula(row, 3, safe_formula(high_diff), formats['currency'])
        high_rec = f'=IF(C{row+1}<B{row+1},"BUILD","BUY")'
        ws.write_formula(row, 4, safe_formula(high_rec), formats['text_bold'])
        row += 1
        
        # Exact breakeven buy cost
        ws.write_string(row, 0, 'Exact Breakeven', formats['text_bold'])
        ws.write_number(row, 1, build_cost_ref, breakeven_result_format)
        ws.write_number(row, 2, build_cost_ref, formats['currency'])
        ws.write_number(row, 3, 0, formats['currency_bold'])
        ws.write_string(row, 4, 'INDIFFERENT', formats['text_bold'])
        row += 2
        
        # ===========================================
        # SECTION 4: SENSITIVITY TO COMBINED RISKS
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '⚠️ RISK TOLERANCE ANALYSIS', formats['subheader'])
        row += 1
        
        ws.write_string(row, 0, 'How much total risk can the build option absorb before buy becomes better?', formats['text'])
        row += 2
        
        # Calculate maximum allowable risk
        base_cost_no_risk = (base_params['build_timeline']/12) * base_params['fte_cost'] * base_params['fte_count'] / (base_params['prob_success']/100) + base_params['misc_costs']
        max_risk_multiplier = buy_cost / base_cost_no_risk
        max_allowable_risk = max(0, (max_risk_multiplier - 1) * 100)
        
        ws.write_string(row, 0, 'Base Cost (no risk)', formats['text_bold'])
        ws.write_number(row, 1, base_cost_no_risk, formats['currency'])
        row += 1
        
        ws.write_string(row, 0, 'Maximum Risk Tolerance', formats['text_bold'])
        ws.write_number(row, 1, max_allowable_risk, breakeven_result_format)
        ws.write_string(row, 2, '% (combined tech + vendor + market)', formats['text'])
        row += 1
        
        ws.write_string(row, 0, 'Current Risk Level', formats['text_bold'])
        ws.write_number(row, 1, combined_risk, formats['currency'])
        ws.write_string(row, 2, '% (current combined risk)', formats['text'])
        row += 1
        
        ws.write_string(row, 0, 'Risk Headroom', formats['text_bold'])
        risk_headroom = max_allowable_risk - combined_risk
        ws.write_number(row, 1, risk_headroom, breakeven_result_format)
        headroom_interpretation = f'=IF({risk_headroom}>0,"Can absorb "&ROUND({risk_headroom},1)&"% more risk","Over risk limit by "&ROUND(ABS({risk_headroom}),1)&"%")'
        ws.write_formula(row, 2, safe_formula(headroom_interpretation), formats['text'])
        row += 2
        
        # ===========================================
        # SECTION 5: INSTRUCTIONS AND KEY INSIGHTS
        # ===========================================
        ws.merge_range(f'A{row}:E{row}', '📋 KEY INSIGHTS & INTERPRETATION', formats['subheader'])
        row += 1
        
        insights = [
            "🎯 Breakeven Values: The exact parameter values where Build = Buy",
            "📊 Change Required: How much each parameter needs to shift to flip the decision",
            "💡 Risk Tolerance: Maximum combined risk the build option can absorb",
            "⚖️ Decision Sensitivity: Parameters closest to their breakeven values are most critical",
            "🔄 Use orange cells to test 'what-if' scenarios in real-time"
        ]
        
        for insight in insights:
            ws.write_string(row, 0, insight, formats['text'])
            row += 1
        
        row += 1
        ws.write_string(row, 0, 'Strategic Recommendations:', formats['text_bold'])
        row += 1
        
        recommendations = [
            "• Focus risk mitigation on parameters closest to breakeven values",
            "• If risk headroom is negative, consider buy option or reduce risk factors",
            "• Monitor market conditions for buy cost changes that could flip the decision",
            "• Use scenarios to stress-test your assumptions before final decision"
        ]
        
        for recommendation in recommendations:
            ws.write_string(row, 0, recommendation, formats['text'])
            row += 1
        
        # ===========================================
        # COLUMN FORMATTING AND PROTECTION
        # ===========================================
        ws.set_column('A:A', 25)  # Parameter labels
        ws.set_column('B:B', 15)  # Current values
        ws.set_column('C:C', 15)  # Breakeven values
        ws.set_column('D:D', 15)  # Change required
        ws.set_column('E:E', 35)  # Interpretation (wider for text)
        
        # Protect the sheet but allow editing of interactive cells
        try:
            ws.protect('BreakevenAnalysis2024', {
                'format_cells': False,
                'format_columns': False,
                'format_rows': False,
                'insert_columns': False,
                'insert_rows': False,
                'insert_hyperlinks': False,
                'delete_columns': False,
                'delete_rows': False,
                'select_locked_cells': True,
                'sort': False,
                'autofilter': False,
                'pivot_tables': False,
                'select_unlocked_cells': True
            })
        except Exception:
            # If protection fails, continue without it
            pass

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
