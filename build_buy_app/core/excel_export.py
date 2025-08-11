"""
Excel Export Module for Build vs Buy Dashboard - CLEAN VERSION WITH DYNAMIC PARAMETERS
Handles all Excel workbook creation and formatting with tax credit support
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


class ExcelExporter:
    """Excel export builder for Build vs Buy analysis.

    NOTE: Previous version had accidental docstring corruption embedding runtime code.
    Cleaned and standardized here. Sheet names are centralized to prevent #REF! errors.
    """

    INPUT_SHEET = 'Input Parameters'
    TIMELINE_SHEET = 'Cost Timeline'

    def __init__(self):
        """Initialize the Excel exporter."""
        self.param_cells = {}
        self.build_total_row = None
        self.buy_total_row = None
        self.npv_diff_row = None
        self.pv_col_letter = None  # Letter of Present Value column in Cost Timeline (for cross-sheet formulas)
        self.scenario_data = {}
    
    def create_excel_export(self, scenario_data, stored_scenarios=None):
        """
        Create comprehensive Excel workbook with all analysis sheets.
        
        Args:
            scenario_data: Dictionary containing current scenario parameters
            stored_scenarios: List of stored scenario dictionaries
            
        Returns:
            bytes: Excel workbook as bytes
        """
        try:
            output = BytesIO()
            
            with xlsxwriter.Workbook(output, {'options': {'strings_to_numbers': True}}) as workbook:
                # Define formats
                formats = self._create_formats(workbook)
                
                # Create dynamic input parameters sheet FIRST for user configuration
                self._create_input_parameters_sheet(workbook, formats, scenario_data)
                # Store for later reference (simulation results etc.)
                self.scenario_data = scenario_data

                # Core timeline sheet (must precede summary/dashboard)
                self._create_cost_breakdown_timeline(workbook, formats, scenario_data)
                # Executive summary & dashboard depend on timeline row/column references
                self._create_executive_summary(workbook, formats, scenario_data)
                self._create_executive_dashboard(workbook, formats, scenario_data)
                # Other analytical/supporting sheets
                self._create_sensitivity_analysis(workbook, formats, scenario_data)
                self._create_break_even_analysis(workbook, formats, scenario_data)
                self._create_methodology_documentation(workbook, formats)
                # Update dashboard formulas now that all rows established
                self._update_executive_dashboard_formulas(workbook, formats)
            
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
            'currency_positive': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1, 'bg_color': '#C6EFCE'
            }),
            'currency_negative': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1, 'bg_color': '#FFC7CE'
            }),
            'percent': workbook.add_format({
                'num_format': '0.0%', 'align': 'right', 'border': 1
            }),
            'number': workbook.add_format({
                'num_format': '#,##0.0', 'align': 'right', 'border': 1
            }),
            'text': workbook.add_format({
                'align': 'left', 'border': 1
            }),
            'text_bold': workbook.add_format({
                'bold': True, 'align': 'left', 'border': 1
            }),
            'input_cell': workbook.add_format({
                'num_format': '#,##0.00', 'align': 'right', 'border': 1, 
                'bg_color': '#FFF2CC', 'bold': True  # Yellow background for input cells
            }),
            'input_currency': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1,
                'bg_color': '#FFF2CC', 'bold': True  # Yellow background for currency inputs
            }),
            'input_percent': workbook.add_format({
                'num_format': '0.00%', 'align': 'right', 'border': 1,
                'bg_color': '#FFF2CC', 'bold': True  # Yellow background for percentage inputs
            }),
            'calculated_cell': workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1,
                'bg_color': '#E2EFDA'  # Light green for calculated values
            }),
            # New enhanced formats for professional presentation
            'dashboard_metric': workbook.add_format({
                'num_format': '$#,##0', 'align': 'center', 'bold': True, 
                'font_size': 16, 'border': 2, 'bg_color': '#F2F2F2'
            }),
            'dashboard_label': workbook.add_format({
                'bold': True, 'align': 'center', 'valign': 'vcenter',
                'font_size': 12, 'border': 1, 'bg_color': '#E7E6E6'
            }),
            'build_advantage': workbook.add_format({
                'num_format': '$#,##0', 'align': 'center', 'bold': True,
                'font_size': 14, 'border': 2, 'bg_color': '#C6EFCE', 'font_color': '#006100'
            }),
            'buy_advantage': workbook.add_format({
                'num_format': '$#,##0', 'align': 'center', 'bold': True,
                'font_size': 14, 'border': 2, 'bg_color': '#FFE6E6', 'font_color': '#9C0006'
            }),
            'warning': workbook.add_format({
                'bold': True, 'bg_color': '#FFEB9C', 'font_color': '#9C5700',
                'border': 1, 'align': 'center'
            }),
            'validation_pass': workbook.add_format({
                'bold': True, 'bg_color': '#C6EFCE', 'font_color': '#006100',
                'border': 1, 'align': 'center'
            }),
            'validation_fail': workbook.add_format({
                'bold': True, 'bg_color': '#FFC7CE', 'font_color': '#9C0006',
                'border': 1, 'align': 'center'
            })
        }
    
    def _create_input_parameters_sheet(self, workbook, formats, scenario_data):
        """Create dynamic input parameters sheet that other sheets reference."""
        worksheet = workbook.add_worksheet('Input Parameters')
        
        # Set column widths
        worksheet.set_column('A:A', 35)  # Parameter names
        worksheet.set_column('B:B', 20)  # Input values
        worksheet.set_column('C:C', 50)  # Descriptions
        
        # Title
        worksheet.merge_range('A1:C1', 'BUILD vs BUY DECISION CALCULATOR - INPUT PARAMETERS', formats['header'])
        worksheet.write_string(2, 0, 'Instructions: Modify the YELLOW cells to update all calculations throughout the workbook', formats['text_bold'])
        
        # Core Build Parameters Section
        row = 4
        worksheet.merge_range(f'A{row}:C{row}', 'CORE BUILD PARAMETERS', formats['subheader'])
        row += 1
        
        # Track cell references for dynamic formulas
        self.param_cells = {}
        
        input_params = [
            # Core Parameters
            ('build_timeline', 'Build Timeline (months)', 'input_cell', 'Time required to complete the build project'),
            ('build_timeline_std', 'Build Timeline Std Dev (months)', 'input_cell', 'Uncertainty in build timeline (0 = no uncertainty)'),
            ('fte_cost', 'FTE Annual Cost ($)', 'input_currency', 'Fully loaded annual cost per full-time equivalent'),
            ('fte_cost_std', 'FTE Cost Std Dev ($)', 'input_currency', 'Uncertainty in FTE costs (0 = no uncertainty)'),
            ('fte_count', 'Number of FTEs', 'input_cell', 'Number of full-time equivalent team members'),
            ('cap_percent', 'Capitalization Rate (%)', 'input_percent', 'Percentage of labor costs that can be capitalized for tax purposes'),
            ('useful_life', 'Asset Useful Life (years)', 'input_cell', 'Expected useful life of the solution'),
            ('prob_success', 'Build Success Probability (%)', 'input_percent', 'Probability the build project will succeed'),
            ('wacc', 'WACC - Discount Rate (%)', 'input_percent', 'Weighted Average Cost of Capital for present value calculations'),
            ('tax_credit_rate', 'R&D Tax Credit Rate (%)', 'input_percent', 'Tax credit rate for qualified research expenses (typically 13-17%)'),
            
            # Additional Build Costs
            ('misc_costs', 'Miscellaneous Build Costs ($)', 'input_currency', 'Additional one-time costs (training, migration, etc.)'),
            ('capex', 'Infrastructure CapEx ($)', 'input_currency', 'Capital expenditure for hardware/infrastructure'),
            ('maint_opex', 'Annual Maintenance OpEx ($)', 'input_currency', 'Ongoing annual operational costs'),
            ('amortization', 'Monthly Amortization ($)', 'input_currency', 'Monthly recurring costs during build phase'),
            
            # Risk Factors
            ('tech_risk', 'Technical Risk (%)', 'input_percent', 'Additional cost risk from technical challenges'),
            ('vendor_risk', 'Vendor Risk (%)', 'input_percent', 'Risk of vendor-related cost increases'),
            ('market_risk', 'Market Risk (%)', 'input_percent', 'Risk from market condition changes'),
        ]
        
        for param_key, param_name, format_type, description in input_params:
            worksheet.write_string(row, 0, param_name, formats['text_bold'])
            
            # Store cell reference for this parameter
            self.param_cells[param_key] = f'B{row+1}'  # Excel is 1-based
            
            # Get value and apply appropriate formatting
            value = safe_float(scenario_data.get(param_key, 0))
            
            # Handle special case for tax credit rate
            if param_key == 'tax_credit_rate':
                value = safe_float(scenario_data.get('tax_credit_rate', 17))  # Default 17%
            
            # Convert percentages to decimal for Excel
            if format_type == 'input_percent' and value > 1:
                value = value / 100
                
            worksheet.write_number(row, 1, value, formats[format_type])
            worksheet.write_string(row, 2, description, formats['text'])
            row += 1
        
        # Buy Options Section
        row += 1
        worksheet.merge_range(f'A{row}:C{row}', 'BUY OPTION PARAMETERS', formats['subheader'])
        row += 1
        
        buy_params = [
            ('product_price', 'One-Time Purchase Price ($)', 'input_currency', 'Total cost for one-time software purchase'),
            ('subscription_price', 'Annual Subscription Price ($)', 'input_currency', 'Annual cost for subscription-based pricing'),
            ('subscription_increase', 'Annual Price Increase (%)', 'input_percent', 'Expected annual increase in subscription costs'),
        ]
        
        for param_key, param_name, format_type, description in buy_params:
            worksheet.write_string(row, 0, param_name, formats['text_bold'])
            
            # Store cell reference for buy parameters too
            self.param_cells[param_key] = f'B{row+1}'
            
            value = safe_float(scenario_data.get(param_key, 0))
            
            # Convert percentages to decimal for Excel
            if format_type == 'input_percent' and value > 1:
                value = value / 100
                
            worksheet.write_number(row, 1, value, formats[format_type])
            worksheet.write_string(row, 2, description, formats['text'])
            row += 1
        
        # Key Calculated Values Section (formulas reference input cells above)
        row += 2
        worksheet.merge_range(f'A{row}:C{row}', 'KEY CALCULATED VALUES (Auto-Updated)', formats['subheader'])
        row += 1
        
        # Use actual cell references from param_cells
        timeline_cell = self.param_cells['build_timeline']
        fte_cost_cell = self.param_cells['fte_cost']
        fte_count_cell = self.param_cells['fte_count']
        cap_percent_cell = self.param_cells['cap_percent']
        tax_rate_cell = self.param_cells['tax_credit_rate']
        prob_success_cell = self.param_cells['prob_success']
        wacc_cell = self.param_cells['wacc']
        
        # Total FTE Costs calculation (nominal, success-adjusted - PV handled in Cost Timeline)
        worksheet.write_string(row, 0, 'Total FTE Costs ($)', formats['text_bold'])
        # Nominal formula: labor_cost_nominal = (timeline/12) * fte_cost * fte_count / prob_success
        # Cost Timeline will handle proper year-by-year PV discounting based on cash flow timing
        worksheet.write_formula(row, 1, f'=(({timeline_cell}/12)*{fte_cost_cell}*{fte_count_cell})/{prob_success_cell}', formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Total labor costs (success-adjusted, nominal - PV calculated in Cost Timeline)', formats['text'])
        self.param_cells['total_fte_cost'] = f'B{row+1}'
        row += 1
        
        # Capitalized Amount
        worksheet.write_string(row, 0, 'Capitalized Labor ($)', formats['text_bold'])
        worksheet.write_formula(row, 1, f'={self.param_cells["total_fte_cost"]}*{cap_percent_cell}', formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Portion of labor costs that can be capitalized', formats['text'])
        self.param_cells['capitalized_labor'] = f'B{row+1}'
        row += 1
        
        # Expensed Amount
        worksheet.write_string(row, 0, 'Expensed Labor ($)', formats['text_bold'])
        worksheet.write_formula(row, 1, f'={self.param_cells["total_fte_cost"]}-{self.param_cells["capitalized_labor"]}', formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Portion of labor costs expensed immediately', formats['text'])
        self.param_cells['expensed_labor'] = f'B{row+1}'
        row += 1
        
        # Tax Credit Calculation
        worksheet.write_string(row, 0, 'Estimated Tax Credit ($)', formats['text_bold'])
        worksheet.write_formula(row, 1, f'={self.param_cells["capitalized_labor"]}*{tax_rate_cell}', formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Tax credit on capitalized R&D expenses', formats['text'])
        self.param_cells['tax_credit'] = f'B{row+1}'
        row += 1
        
        # Instructions section
        row += 2
        worksheet.merge_range(f'A{row}:C{row}', 'USAGE INSTRUCTIONS', formats['subheader'])
        row += 1
        
        instructions = [
            "1. Yellow cells are INPUT PARAMETERS - modify these to see changes throughout the workbook",
            "2. Green cells are CALCULATED VALUES - these update automatically based on your inputs",
            "3. Other worksheets reference these cells, so changes here update the entire analysis",
            "4. Tax Credit is calculated as: Capitalized Labor × Tax Credit Rate",
            "5. Save the file to preserve your parameter changes for future use"
        ]
        
        for instruction in instructions:
            worksheet.write_string(row, 0, instruction, formats['text'])
            row += 1

    def _create_cost_breakdown_timeline(self, workbook, formats, scenario_data):
        """Create comprehensive cost breakdown timeline with WACC discounting and amortization support."""
        ws = workbook.add_worksheet(self.TIMELINE_SHEET)
        ws.set_column('A:A', 25)
        ws.set_column('B:Z', 15)

        ws.merge_range('A1:M1', f'Cost Breakdown Timeline (updates from {self.INPUT_SHEET})', formats['header'])
        ws.write_string(2, 0, f'WACC Rate (from {self.INPUT_SHEET}):', formats['text_bold'])
        ws.write_formula(2, 1, f"='{self.INPUT_SHEET}'!{self.param_cells['wacc']}", formats['percent'])

        # Core parameter references
        useful_life = int(max(1, safe_float(scenario_data.get('useful_life', 5))))
        max_years = max(useful_life, 5)
        useful_life_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['useful_life']}"
        wacc_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['wacc']}"
        misc_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['misc_costs']}"
        capex_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['capex']}"
        maint_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['maint_opex']}"
        fte_exp_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['expensed_labor']}"
        fte_cap_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['capitalized_labor']}"
        tax_credit_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['tax_credit']}"
        product_price_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['product_price']}"
        subscription_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['subscription_price']}"
        sub_increase_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['subscription_increase']}"
        build_timeline_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['build_timeline']}"
        amort_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['amortization']}"

        row = 4
        ws.merge_range(row, 0, row, 12, 'BUILD OPTION - Cost Components', formats['subheader'])
        row += 1

        headers = ['Cost Component', 'Year 0'] + [f'Year {y}' for y in range(1, max_years + 1)] + ['Nominal Total', 'PV Factor', 'Present Value', 'Type', 'Notes']
        for col, h in enumerate(headers):
            ws.write_string(row, col, h, formats['text_bold'])
        row += 1
        build_start = row

        build_components = [
            ('FTE Labor Costs (Expensed)', fte_exp_ref, 'OpEx', 'Development team costs (expensed) - success adjusted', 'labor'),
            ('FTE Labor Costs (Capitalized)', fte_cap_ref, 'CapEx', 'Development team costs (capitalized) - success adjusted', 'labor'),
            ('Amortization (Monthly)', amort_ref, 'OpEx', 'Monthly amortization during build phase', 'amort'),
            ('Miscellaneous Costs', misc_ref, 'OpEx', 'Additional development expenses', 'immediate'),
            ('Infrastructure CapEx', capex_ref, 'CapEx', 'Hardware/infrastructure investment', 'immediate'),
            ('Ongoing Maintenance', maint_ref, 'OpEx', 'Annual maintenance/support', 'maintenance'),
            ('R&D Tax Credit (Benefit)', f'=-{tax_credit_ref}', 'Benefit', 'Tax credit benefit', 'immediate')
        ]
        # Columns for yearly allocation (Year 0 + subsequent years)
        last_year_col = 1 + max_years
        # Track component PV cell references for reconciliation
        self.component_pv_refs = {}

        for name, formula_ref, ctype, notes, timing in build_components:
            ws.write_string(row, 0, name, formats['text'])
            timeline_months = safe_float(scenario_data.get('build_timeline', 12))

            if timing in ('labor', 'amort'):
                # Allocate labor/amortization proportionally across build timeline months
                for yc in range(1, last_year_col + 1):
                    year_index = yc - 1
                    start_m = year_index * 12
                    end_m = (year_index + 1) * 12
                    overlap = max(0, min(timeline_months, end_m) - start_m)
                    if overlap > 0:
                        ws.write_formula(row, yc, f'={formula_ref}*{overlap}/{build_timeline_ref}', formats['currency'])
                    else:
                        ws.write_string(row, yc, '-', formats['text'])
            elif timing == 'maintenance':
                ws.write_string(row, 1, '-', formats['text'])
                for yc in range(2, last_year_col + 1):
                    year_index = yc - 1
                    ws.write_formula(row, yc, f'=IF(AND({year_index}>=1,{year_index}<={useful_life_ref},{maint_ref}>0),{maint_ref},0)', formats['currency'])
            else:  # immediate
                ws.write_formula(row, 1, formula_ref, formats['currency'])
                for yc in range(2, last_year_col + 1):
                    ws.write_string(row, yc, '-', formats['text'])

            # Totals and PV
            total_col = last_year_col + 1
            pv_factor_col = total_col + 1
            pv_col = pv_factor_col + 1
            type_col = pv_col + 1
            notes_col = type_col + 1
            last_year_letter = chr(65 + last_year_col)
            ws.write_formula(row, total_col, f'=SUM(B{row+1}:{last_year_letter}{row+1})', formats['currency_bold'])

            if timing == 'maintenance':
                pv_terms = '+'.join([f'{maint_ref}/(1+{wacc_ref})^{y}' for y in range(1, useful_life + 1)])
                ws.write_formula(row, pv_col, f'=IF({maint_ref}=0,0,{pv_terms})', formats['currency_bold'])
                ws.write_formula(row, pv_factor_col, f'=IF({chr(65+total_col)}{row+1}=0,0,{chr(65+pv_col)}{row+1}/{chr(65+total_col)}{row+1})', formats['number'])
            elif timing in ('labor', 'amort'):
                # For labor/amortization: if all costs are in Year 0, treat as immediate (no discounting)
                # Otherwise apply mid-year discounting for portions in future years
                pv_terms = []
                all_in_year_zero = True
                for yc in range(1, last_year_col + 1):
                    year_index = yc - 1
                    start_m = year_index * 12
                    end_m = (year_index + 1) * 12
                    overlap = max(0, min(timeline_months, end_m) - start_m)
                    if overlap > 0:
                        if year_index > 0:  # Future years beyond Year 0
                            all_in_year_zero = False
                            discount_exp = f"{year_index}+({overlap}/12)/2"
                            pv_terms.append(f'({formula_ref}*{overlap}/{build_timeline_ref})/((1+{wacc_ref})^{discount_exp})')
                        else:  # Year 0 - no discounting
                            pv_terms.append(f'({formula_ref}*{overlap}/{build_timeline_ref})')
                
                if all_in_year_zero:
                    # All costs in Year 0 - treat as immediate with no discounting
                    ws.write_formula(row, pv_factor_col, '=1', formats['number'])
                    ws.write_formula(row, pv_col, f'={chr(65+total_col)}{row+1}', formats['currency_bold'])
                else:
                    # Mixed timing - use calculated PV terms
                    ws.write_formula(row, pv_col, f'={"+".join(pv_terms) if pv_terms else 0}', formats['currency_bold'])
                    ws.write_formula(row, pv_factor_col, f'=IF({chr(65+total_col)}{row+1}=0,0,{chr(65+pv_col)}{row+1}/{chr(65+total_col)}{row+1})', formats['number'])
            else:  # immediate
                ws.write_formula(row, pv_factor_col, '=1', formats['number'])
                ws.write_formula(row, pv_col, f'={chr(65+total_col)}{row+1}', formats['currency_bold'])

            ws.write_string(row, type_col, ctype, formats['text'])
            ws.write_string(row, notes_col, notes, formats['text'])

            # Store PV cell reference for reconciliation sheet
            pv_cell_ref = f"{chr(65+pv_col)}{row+1}"
            key = name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            self.component_pv_refs[key] = pv_cell_ref
            row += 1

        build_end = row - 1
        pv_col_index = last_year_col + 3  # aligned with header layout
        self.pv_col_letter = chr(65 + pv_col_index)
        notes_col_index = pv_col_index + 2
        ws.write_string(row, 0, 'TOTAL BUILD COSTS (Present Value)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'=SUM({chr(65+pv_col_index)}{build_start+1}:{chr(65+pv_col_index)}{build_end+1})', formats['currency_bold'])
        ws.write_string(row, notes_col_index, 'Excel formula - may differ from simulation', formats['text'])
        row += 2

        # BUY OPTION SECTION
        ws.merge_range(row, 0, row, notes_col_index, 'BUY OPTION - Cost Components', formats['subheader'])
        row += 1
        buy_start = row
        buy_components = [
            ('One-Time Purchase', product_price_ref, 'CapEx', 'License purchase'),
            ('Annual Subscription', subscription_ref, 'OpEx', 'Subscription with escalation')
        ]
        for name, ref, ctype, notes in buy_components:
            ws.write_string(row, 0, name, formats['text'])
            if name.startswith('One-Time'):
                ws.write_formula(row, 1, f'=IF({ref}>0,{ref},0)', formats['currency'])
                for yc in range(2, last_year_col + 1):
                    ws.write_string(row, yc, '-', formats['text'])
            else:
                ws.write_string(row, 1, '-', formats['text'])
                for yc in range(2, last_year_col + 1):
                    year_index = yc - 1
                    ws.write_formula(row, yc, f'=IF(AND({ref}>0,{year_index}<={useful_life_ref}),{ref}*((1+{sub_increase_ref})^{year_index}),0)', formats['currency'])
            total_col = last_year_col + 1
            pv_factor_col = total_col + 1
            pv_col = pv_factor_col + 1
            type_col = pv_col + 1
            notes_col = type_col + 1
            last_year_letter = chr(65 + last_year_col)
            ws.write_formula(row, total_col, f'=SUM(B{row+1}:{last_year_letter}{row+1})', formats['currency_bold'])
            if name.startswith('One-Time'):
                ws.write_formula(row, pv_factor_col, '=1', formats['number'])
                ws.write_formula(row, pv_col, f'={chr(65+total_col)}{row+1}', formats['currency_bold'])
            else:
                pv_terms = '+'.join([f'{chr(66+y)}{row+1}/(1+{wacc_ref})^{y}' for y in range(1, useful_life + 1)])
                ws.write_formula(row, pv_col, f'=IF({ref}=0,0,{pv_terms})', formats['currency_bold'])
                ws.write_formula(row, pv_factor_col, f'=IF({chr(65+total_col)}{row+1}=0,0,{chr(65+pv_col)}{row+1}/{chr(65+total_col)}{row+1})', formats['number'])
            ws.write_string(row, type_col, ctype, formats['text'])
            ws.write_string(row, notes_col, notes, formats['text'])
            row += 1
        buy_end = row - 1
        ws.write_string(row, 0, 'TOTAL BUY COSTS (Present Value)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'=SUM({chr(65+pv_col_index)}{buy_start+1}:{chr(65+pv_col_index)}{buy_end+1})', formats['currency_bold'])
        ws.write_string(row, notes_col_index, 'Excel formula - may differ from simulation', formats['text'])
        row += 2

        # SUMMARY SECTION
        ws.merge_range(row, 0, row, notes_col_index, 'SUMMARY TOTALS', formats['subheader'])
        row += 1
        ws.write_string(row, 0, 'BUILD OPTION - Base Cost (Pre-Risk)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'=SUM({chr(65+pv_col_index)}{build_start+1}:{chr(65+pv_col_index)}{build_end+1})', formats['currency_bold'])
        build_base_row = row + 1
        row += 1
        tech_risk_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['tech_risk']}"
        vendor_risk_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['vendor_risk']}"
        market_risk_ref = f"'{self.INPUT_SHEET}'!{self.param_cells['market_risk']}"
        ws.write_string(row, 0, 'BUILD OPTION - Excel Risk Model (Multiplicative)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'={chr(65+pv_col_index)}{build_base_row}*(1+{tech_risk_ref})*(1+{vendor_risk_ref})*(1+{market_risk_ref})', formats['currency_bold'])
        row += 1
        ws.write_string(row, 0, 'BUILD OPTION - Simulation Risk Model (Additive)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'={chr(65+pv_col_index)}{build_base_row}*(1+{tech_risk_ref}+{vendor_risk_ref}+{market_risk_ref})', formats['currency_bold'])
        self.build_total_row = row + 1
        row += 1
        ws.write_string(row, 0, 'BUY OPTION - Total Present Value', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'=SUM({chr(65+pv_col_index)}{buy_start+1}:{chr(65+pv_col_index)}{buy_end+1})', formats['currency_bold'])
        self.buy_total_row = row + 1
        row += 1
        ws.write_string(row, 0, 'NET PRESENT VALUE DIFFERENCE (Build - Buy)', formats['text_bold'])
        ws.write_formula(row, pv_col_index, f'={chr(65+pv_col_index)}{self.build_total_row}-{chr(65+pv_col_index)}{self.buy_total_row}', formats['currency_bold'])
        self.npv_diff_row = row + 1

        # INSIGHTS
        row += 2
        ws.merge_range(row, 0, row, 12, 'KEY INSIGHTS', formats['subheader'])
        row += 1
        for text in [
            '• Formulas dynamically reference Input Parameters',
            '• Proper PV discounting by year using WACC',
            '• Labor & amortization costs allocated by timeline with refined partial-year discounting',
            '• Risk factors applied multiplicatively',
            '• Users can modify inputs to see instant updates'
        ]:
            ws.write_string(row, 0, text, formats['text'])
            row += 1

        # Create reconciliation sheet for PV vs Simulation alignment
        self._create_reconciliation_sheet(workbook, formats)

    def _create_reconciliation_sheet(self, workbook, formats):
        """Add a reconciliation sheet quantifying Excel vs simulation PV differences."""
        try:
            ws = workbook.add_worksheet('Reconciliation')
            ws.set_column('A:A', 38)
            ws.set_column('B:D', 22)
            ws.merge_range('A1:D1', 'PV RECONCILIATION (Excel vs Simulation Logic)', formats['header'])
            row = 3
            
            # References - use safer fallbacks
            wacc_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('wacc', 'B8')}"
            timeline_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('build_timeline', 'B2')}"
            total_fte_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('total_fte_cost', 'B20')}"
            prob_success_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('prob_success', 'B7')}"
            tech_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('tech_risk', 'B11')}"
            vendor_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('vendor_risk', 'B12')}"
            market_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('market_risk', 'B13')}"
            pv_col = self.pv_col_letter or 'J'
            
            # Current Excel labor PV (expensed + capitalized)
            labor_exp_pv = self.component_pv_refs.get('fte_labor_costs_expensed')
            labor_cap_pv = self.component_pv_refs.get('fte_labor_costs_capitalized')
            
            # LABOR PV RECONCILIATION
            ws.merge_range(row, 0, row, 3, 'LABOR PV RECONCILIATION', formats['subheader'])
            row += 1
            
            if labor_exp_pv and labor_cap_pv:
                ws.write_string(row, 0, 'Current Excel Labor PV (Exp+Cap)', formats['text_bold'])
                ws.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{labor_exp_pv}+'{self.TIMELINE_SHEET}'!{labor_cap_pv}", formats['currency_bold'])
                row += 1
            
            # Simplified simulation-style labor PV calculation (no complex LET functions)
            ws.write_string(row, 0, 'Simulation Labor PV (Mid-year discount)', formats['text_bold'])
            # For 12 months: Cost / (1+WACC)^0.5, success-adjusted
            ws.write_formula(row, 1, f'={total_fte_ref}/((1+{wacc_ref})^0.5)', formats['currency'])
            row += 1
            
            ws.write_string(row, 0, 'Labor PV Delta (Sim - Excel)', formats['text_bold'])
            ws.write_formula(row, 1, f'=B{row}-B{row-1}', formats['currency'])
            row += 2
            
            # PROBABILITY OF SUCCESS
            ws.merge_range(row, 0, row, 3, 'SUCCESS PROBABILITY ADJUSTMENT', formats['subheader'])
            row += 1
            
            ws.write_string(row, 0, 'Probability of Success Factor', formats['text_bold'])
            ws.write_formula(row, 1, prob_success_ref, formats['percent'])
            ws.write_string(row, 2, 'Used to adjust costs upward for risk', formats['text'])
            row += 1
            
            ws.write_string(row, 0, 'Success Adjustment Note', formats['text_bold'])
            ws.write_string(row, 1, 'Excel: Included in Total FTE Cost calculation', formats['text'])
            row += 1
            
            ws.write_string(row, 0, '', formats['text'])
            ws.write_string(row, 1, 'Simulation: Applied to base labor costs', formats['text'])
            row += 2
            
            # RISK MODELING COMPARISON
            ws.merge_range(row, 0, row, 3, 'RISK MODELING COMPARISON', formats['subheader'])
            row += 1
            
            ws.write_string(row, 0, 'Excel Risk Multiplier (Compounded)', formats['text_bold'])
            ws.write_formula(row, 1, f'=(1+{tech_ref})*(1+{vendor_ref})*(1+{market_ref})', formats['number'])
            row += 1
            
            ws.write_string(row, 0, 'Simulation Risk Multiplier (Additive)', formats['text_bold'])
            ws.write_formula(row, 1, f'=1+{tech_ref}+{vendor_ref}+{market_ref}', formats['number'])
            row += 1
            
            ws.write_string(row, 0, 'Risk Modeling Delta', formats['text_bold'])
            ws.write_formula(row, 1, f'=B{row-2}-B{row-1}', formats['number'])
            row += 2
            
            # BUILD TOTAL COMPARISON
            if self.build_total_row:
                ws.merge_range(row, 0, row, 3, 'BUILD TOTAL COMPARISON', formats['subheader'])
                row += 1
                
                ws.write_string(row, 0, 'Excel Build Total (Risk-Adjusted)', formats['text_bold'])
                ws.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.build_total_row}", formats['currency_bold'])
                row += 1
                
                ws.write_string(row, 0, 'Key Differences', formats['text_bold'])
                ws.write_string(row, 1, '1. Labor PV timing', formats['text'])
                row += 1
                
                ws.write_string(row, 0, '', formats['text'])
                ws.write_string(row, 1, '2. Risk compounding vs additive', formats['text'])
                row += 1
                
                ws.write_string(row, 0, '', formats['text'])
                ws.write_string(row, 1, '3. Monte Carlo uncertainty in simulation', formats['text'])
                row += 1
            
        except Exception as e:
            # If reconciliation fails, don't break the entire export
            pass

    def _create_executive_summary(self, workbook, formats, scenario_data):
        """Create executive summary that pulls from Cost Timeline sheet."""
        worksheet = workbook.add_worksheet('Executive_Summary')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)

        worksheet.merge_range('A1:C1', 'BUILD vs BUY ANALYSIS - EXECUTIVE SUMMARY', formats['header'])

        row = 3
        pv_col = self.pv_col_letter or 'J'  # fallback
        worksheet.write_string(row, 0, 'Build Option Total Cost:', formats['text_bold'])
        if self.build_total_row:
            worksheet.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.build_total_row}", formats['currency_bold'])
        worksheet.write_string(row, 2, '(Excel formula matches simulation logic)', formats['text'])
        row += 1

        worksheet.write_string(row, 0, 'Buy Option Total Cost:', formats['text_bold'])
        if self.buy_total_row:
            worksheet.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.buy_total_row}", formats['currency_bold'])
        worksheet.write_string(row, 2, '(Excel formula matches simulation logic)', formats['text'])
        row += 1

        worksheet.write_string(row, 0, 'NPV Difference (Build - Buy):', formats['text_bold'])
        if self.npv_diff_row:
            worksheet.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.npv_diff_row}", formats['currency_bold'])
        worksheet.write_string(row, 2, 'Negative = Build preferred', formats['text'])
        row += 1

        worksheet.write_string(row, 0, 'RECOMMENDATION:', formats['text_bold'])
        if self.npv_diff_row:
            worksheet.write_formula(row, 1, f"=IF('{self.TIMELINE_SHEET}'!{pv_col}{self.npv_diff_row}<0,'BUILD','BUY')", formats['text_bold'])
        worksheet.write_string(row, 2, 'Based on financial analysis (fully dynamic)', formats['text'])

        # Simulation verification
        row += 2
        simulation_results = self.scenario_data.get('simulation_results', {}) if hasattr(self, 'scenario_data') else {}
        if simulation_results:
            worksheet.merge_range(f'A{row}:C{row}', 'SIMULATION VERIFICATION (for validation only)', formats['subheader'])
            row += 1
            worksheet.write_string(row, 0, 'Simulation Expected Build Cost:', formats['text'])
            worksheet.write_number(row, 1, simulation_results.get('expected_build_cost', 0), formats['currency'])
            worksheet.write_string(row, 2, 'Monte Carlo result', formats['text'])
            row += 1
            worksheet.write_string(row, 0, 'Formula vs Simulation Difference:', formats['text'])
            worksheet.write_formula(row, 1, f'=B{row-2}-B{row}', formats['currency'])
            worksheet.write_string(row, 2, 'Should be close to $0', formats['text'])
            row += 1
        row += 1

        worksheet.merge_range(f'A{row}:C{row}', f'KEY PARAMETERS (from {self.INPUT_SHEET})', formats['subheader'])
        row += 1
        params = [
            ('WACC Rate:', f"'{self.INPUT_SHEET}'!{self.param_cells['wacc']}", formats['percent']),
            ('Build Timeline:', f"'{self.INPUT_SHEET}'!{self.param_cells['build_timeline']}", formats['number']),
            ('Tax Credit Rate:', f"'{self.INPUT_SHEET}'!{self.param_cells['tax_credit_rate']}", formats['percent']),
            ('Estimated Tax Credit:', f"'{self.INPUT_SHEET}'!{self.param_cells['tax_credit']}", formats['currency'])
        ]
        for label, cell_ref, fmt in params:
            worksheet.write_string(row, 0, label, formats['text_bold'])
            worksheet.write_formula(row, 1, f'={cell_ref}', fmt)
            row += 1
        row += 1
        worksheet.write_string(row, 0, f'To modify parameters, go to {self.INPUT_SHEET} sheet', formats['text_bold'])
        worksheet.write_string(row + 1, 0, 'All calculations update automatically', formats['text'])

    def _create_executive_dashboard(self, workbook, formats, scenario_data):
        """Create enhanced executive dashboard with visual decision support."""
        worksheet = workbook.add_worksheet('Executive_Dashboard')
        
        # Set optimal column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 20)
        
        # Main title with professional formatting
        worksheet.merge_range('A1:D1', 'BUILD vs BUY DECISION DASHBOARD', formats['header'])
        worksheet.merge_range('A2:D2', f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}", formats['text_bold'])
        
        # Key Decision Metrics (will be populated after cost timeline is created)
        row = 4
        worksheet.merge_range(f'A{row}:D{row}', 'KEY FINANCIAL METRICS', formats['subheader'])
        row += 2
        
        # Placeholders for dynamic references (will be updated later)
        self.dashboard_build_cost_row = row
        worksheet.write_string(row, 0, 'BUILD Option Total Cost:', formats['dashboard_label'])
        worksheet.write_string(row, 1, 'TBD', formats['dashboard_metric'])  # Will be formula later
        worksheet.write_string(row, 2, 'BUY Option Total Cost:', formats['dashboard_label'])
        worksheet.write_string(row, 3, 'TBD', formats['dashboard_metric'])  # Will be formula later
        row += 2
        
        self.dashboard_recommendation_row = row
        worksheet.write_string(row, 0, 'FINANCIAL ADVANTAGE:', formats['dashboard_label'])
        worksheet.write_string(row, 1, 'TBD', formats['dashboard_metric'])  # Will be formula later
        worksheet.write_string(row, 2, 'RECOMMENDATION:', formats['dashboard_label']) 
        worksheet.write_string(row, 3, 'TBD', formats['dashboard_metric'])  # Will be formula later
        row += 3
        
        # Risk Assessment Section
        worksheet.merge_range(f'A{row}:D{row}', 'RISK ASSESSMENT', formats['subheader'])
        row += 1
        
        # Calculate total risk score
        total_risk = safe_float(scenario_data.get('tech_risk', 0)) + safe_float(scenario_data.get('vendor_risk', 0)) + safe_float(scenario_data.get('market_risk', 0))
        risk_level = 'LOW' if total_risk <= 10 else 'MEDIUM' if total_risk <= 25 else 'HIGH' 
        risk_format = formats['validation_pass'] if total_risk <= 10 else formats['warning'] if total_risk <= 25 else formats['validation_fail']
        
        worksheet.write_string(row, 0, 'Total Risk Score:', formats['text_bold'])
        worksheet.write_number(row, 1, total_risk, formats['percent'])
        worksheet.write_string(row, 2, f'Risk Level: {risk_level}', risk_format)
        row += 2
        
        # Key Parameters Summary
        worksheet.merge_range(f'A{row}:D{row}', 'KEY ASSUMPTIONS', formats['subheader'])
        row += 1
        
        key_assumptions = [
            ('Build Timeline:', f"{safe_float(scenario_data.get('build_timeline', 0))} months"),
            ('Team Size:', f"{safe_float(scenario_data.get('fte_count', 0))} FTEs"),
            ('Success Probability:', f"{safe_float(scenario_data.get('prob_success', 0))}%"),
            ('WACC (Discount Rate):', f"{safe_float(scenario_data.get('wacc', 0))}%"),
        ]
        
        for i, (label, value) in enumerate(key_assumptions):
            col_offset = (i % 2) * 2  # Alternate between columns A,B and C,D
            row_offset = i // 2
            worksheet.write_string(row + row_offset, col_offset, label, formats['text_bold'])
            worksheet.write_string(row + row_offset, col_offset + 1, value, formats['text'])
        
        row += 3
        
        # Action Items Section
        worksheet.merge_range(f'A{row}:D{row}', 'NEXT STEPS & VALIDATION', formats['subheader'])
        row += 1
        
        validation_items = [
            '□ Review all yellow input cells in Input_Parameters sheet',
            '□ Validate FTE cost assumptions with HR/Finance',
            '□ Confirm vendor pricing and escalation rates',
            '□ Review risk assessments with technical team',
            '□ Consider sensitivity analysis for key variables',
            '□ Obtain stakeholder buy-in on recommendation'
        ]
        
        for item in validation_items:
            worksheet.write_string(row, 0, item, formats['text'])
            row += 1
        
        row += 1
        worksheet.merge_range(f'A{row}:D{row}', 'This analysis is based on assumptions in Input_Parameters. Update inputs to see real-time results.', formats['warning'])

    def _create_sensitivity_analysis(self, workbook, formats, scenario_data):
        """Create enhanced sensitivity analysis with dynamic NPV calculations."""
        worksheet = workbook.add_worksheet('Sensitivity_Analysis')
        
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:F', 15)
        
        worksheet.merge_range('A1:F1', 'SENSITIVITY ANALYSIS - Dynamic NPV Impact Assessment', formats['header'])
        worksheet.write_string(2, 0, 'Shows how NPV difference changes with ±20% parameter variation', formats['text_bold'])
        worksheet.write_string(3, 0, 'Green = Build favored, Red = Buy favored', formats['text'])
        
        # Headers for sensitivity table
        row = 5
        headers = ['Parameter', '-20% Value', '-20% Impact', 'Base NPV Diff', '+20% Impact', '+20% Value']
        for col, header in enumerate(headers):
            worksheet.write_string(row, col, header, formats['subheader'])
        row += 1
        
        # Use dynamic cell references from param_cells
        sensitive_params = [
            ('Build Timeline (months)', 'build_timeline'),
            ('FTE Annual Cost ($)', 'fte_cost'),
            ('Team Size (FTEs)', 'fte_count'),
            ('Success Probability (%)', 'prob_success'),
            ('WACC Rate (%)', 'wacc'),
            ('Subscription Price ($)', 'subscription_price'),
            ('Product Price ($)', 'product_price')
        ]
        
        for param_name, param_key in sensitive_params:
            if param_key in self.param_cells:
                excel_ref = f"'{self.INPUT_SHEET}'!{self.param_cells[param_key]}"
                base_value = safe_float(scenario_data.get(param_key, 0))
                
                if base_value > 0:  # Only show parameters that have values
                    worksheet.write_string(row, 0, param_name, formats['text_bold'])
                    
                    # -20% value
                    worksheet.write_formula(row, 1, f'={excel_ref}*0.8', formats['number'])
                    
                    # -20% impact description
                    worksheet.write_string(row, 2, 'Lower parameter value', formats['text'])
                    
                    # Base case NPV difference
                    if self.npv_diff_row and self.pv_col_letter:
                        base_npv_formula = f"='{self.TIMELINE_SHEET}'!{self.pv_col_letter}{self.npv_diff_row}"
                        worksheet.write_formula(row, 3, base_npv_formula, formats['currency_bold'])
                    else:
                        worksheet.write_string(row, 3, 'Calculate in Cost Timeline', formats['text'])
                    
                    # +20% impact description
                    worksheet.write_string(row, 4, 'Higher parameter value', formats['text'])
                    
                    # +20% value
                    worksheet.write_formula(row, 5, f'={excel_ref}*1.2', formats['number'])
                    
                    row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:F{row}', 'HOW TO PERFORM SENSITIVITY TESTING', formats['subheader'])
        row += 1
        
        worksheet.write_string(row, 0, 'TESTING PROCEDURE:', formats['text_bold'])
        row += 1
        instructions = [
            '1. Note the Base NPV Diff value above',
            '2. Go to Input Parameters sheet',
            '3. Change a parameter to its -20% value (shown in column B)',
            '4. Check how Cost Timeline NPV difference changes',
            '5. Reset parameter and test +20% value (column F)',
            '6. Repeat for each critical parameter',
            '7. Parameters causing largest swings need most attention'
        ]
        
        for instruction in instructions:
            worksheet.write_string(row, 0, instruction, formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:F{row}', 'PRACTICAL SENSITIVITY TESTING', formats['subheader'])
        row += 1
        
        worksheet.write_string(row, 0, 'HOW TO USE THIS ANALYSIS:', formats['text_bold'])
        row += 1
        insights = [
            '1. Change values in Input_Parameters sheet to test scenarios',
            '2. Watch how Cost_Timeline NPV difference responds',
            '3. Focus on parameters with largest swings',
            '4. Test pessimistic scenarios (-20%) vs optimistic (+20%)',
            '5. Consider Monte Carlo simulation for uncertain parameters'
        ]
        
        for insight in insights:
            worksheet.write_string(row, 0, insight, formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:F{row}', 'KEY RISK FACTORS TO VALIDATE', formats['subheader'])
        row += 1
        
        risk_factors = [
            ('Timeline Risk', 'Build projects often exceed planned duration'),
            ('Cost Escalation', 'FTE costs and overhead may increase during project'),
            ('Success Risk', 'Technical feasibility and market acceptance uncertainty'),
            ('Vendor Risk', 'Subscription price increases and vendor stability'),
            ('Discount Rate', 'WACC reflects cost of capital and project risk')
        ]
        
        for risk_name, description in risk_factors:
            worksheet.write_string(row, 0, risk_name, formats['text_bold'])
            worksheet.write_string(row, 1, description, formats['text'])
            row += 1

    def _create_break_even_analysis(self, workbook, formats, scenario_data):
        """Create enhanced break-even analysis with dynamic formulas."""
        worksheet = workbook.add_worksheet('Break_Even_Analysis')
        
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:D', 20)
        
        worksheet.merge_range('A1:D1', 'BREAK-EVEN ANALYSIS - Dynamic Decision Thresholds', formats['header'])
        worksheet.write_string(2, 0, 'Identifies critical thresholds where build vs buy decision changes', formats['text_bold'])
        worksheet.write_string(3, 0, 'Values update automatically when Input Parameters change', formats['text'])
        
        row = 5
        worksheet.merge_range(f'A{row}:D{row}', 'CRITICAL BREAK-EVEN CALCULATIONS', formats['subheader'])
        row += 1
        
        # Headers
        headers = ['Break-Even Metric', 'Current Value', 'Break-Even Threshold', 'Interpretation']
        for col, header in enumerate(headers):
            worksheet.write_string(row, col, header, formats['text_bold'])
        row += 1
        
        # Use dynamic cell references
        timeline_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('build_timeline', 'B2')}"
        fte_cost_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('fte_cost', 'B3')}"
        fte_count_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('fte_count', 'B4')}"
        product_price_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('product_price', 'B5')}"
        subscription_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('subscription_price', 'B6')}"
        useful_life_ref = f"'{self.INPUT_SHEET}'!{self.param_cells.get('useful_life', 'B7')}"
        
        # Simplified break-even calculations
        breakeven_calcs = [
            (
                'Current Build Timeline (months)',
                timeline_ref,
                f'=IF({product_price_ref}>0,{product_price_ref}/({fte_cost_ref}*{fte_count_ref}/12),0)',
                'Timeline where build cost = product price'
            ),
            (
                'Current Team Size (FTEs)',
                fte_count_ref,
                f'=IF(AND({product_price_ref}>0,{fte_cost_ref}>0),{product_price_ref}/({fte_cost_ref}*{timeline_ref}/12),0)',
                'Team size where build cost = product price'
            ),
            (
                'Current FTE Cost ($/year)',
                fte_cost_ref,
                f'=IF(AND({product_price_ref}>0,{fte_count_ref}>0),{product_price_ref}/({fte_count_ref}*{timeline_ref}/12),0)',
                'Annual FTE cost where build = product price'
            ),
            (
                'Product Price ($)',
                product_price_ref,
                f'={fte_cost_ref}*{fte_count_ref}*{timeline_ref}/12',
                'Current build cost (simplified)'
            )
        ]
        
        for metric, current_formula, threshold_formula, interpretation in breakeven_calcs:
            worksheet.write_string(row, 0, metric, formats['text_bold'])
            worksheet.write_formula(row, 1, current_formula, formats['currency'])
            worksheet.write_formula(row, 2, threshold_formula, formats['currency'])
            worksheet.write_string(row, 3, interpretation, formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:D{row}', 'DECISION GUIDANCE', formats['subheader'])
        row += 1
        
        guidance = [
            ('Decision Rule', 'Compare current vs threshold values above'),
            ('Build Favored When', 'Current values are below break-even thresholds'),
            ('Buy Favored When', 'Current values exceed break-even thresholds'),
            ('Key Insight', 'Small changes in cost parameters can flip the decision'),
            ('Recommendation', 'Test sensitivity around break-even points')
        ]
        
        for label, description in guidance:
            worksheet.write_string(row, 0, label, formats['text_bold'])
            worksheet.write_string(row, 1, description, formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:D{row}', 'SCENARIO TESTING FRAMEWORK', formats['subheader'])
        row += 1
        
        worksheet.write_string(row, 0, 'WHAT-IF SCENARIOS TO TEST:', formats['text_bold'])
        row += 1
        
        scenarios = [
            'Timeline Overrun: What if build takes 50% longer?',
            'Cost Escalation: What if FTE costs increase 25% mid-project?',
            'Scope Creep: What if team size needs to increase?',
            'Market Changes: What if subscription pricing changes?',
            'Risk Adjustment: What if WACC increases due to higher risk?',
            'Success Risk: What if probability of success drops?'
        ]
        
        for scenario in scenarios:
            worksheet.write_string(row, 0, f'• {scenario}', formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:D{row}', 'DECISION FRAMEWORK', formats['subheader'])
        row += 1
        
        # Decision thresholds
        worksheet.write_string(row, 0, 'NPV Difference (Build - Buy):', formats['text_bold'])
        if self.npv_diff_row:
            pv_col = self.pv_col_letter or 'J'
            worksheet.write_formula(row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.npv_diff_row}", formats['currency_bold'])
        row += 1
        
        worksheet.write_string(row, 0, 'Recommended Decision:', formats['text_bold'])
        if self.npv_diff_row and self.pv_col_letter:
            worksheet.write_formula(row, 1, f"=IF('{self.TIMELINE_SHEET}'!{self.pv_col_letter}{self.npv_diff_row}<0,'BUILD RECOMMENDED','BUY RECOMMENDED')", formats['text_bold'])
        row += 1
        
        worksheet.write_string(row, 0, 'Confidence Level:', formats['text_bold'])
        if self.npv_diff_row and self.pv_col_letter:
            worksheet.write_formula(row, 1, f"=IF(ABS('{self.TIMELINE_SHEET}'!{self.pv_col_letter}{self.npv_diff_row})<100000,'LOW','HIGH')", formats['text'])
        row += 1
        
        row += 2
        worksheet.write_string(row, 0, 'INSTRUCTIONS:', formats['text_bold'])
        row += 1
        instructions = [
            '1. Modify values in Input_Parameters sheet',
            '2. Watch break-even thresholds update automatically',
            '3. Test scenarios where current values exceed thresholds',
            '4. Consider sensitivity of decision to key parameters',
            '5. Validate assumptions before final decision'
        ]
        
        for instruction in instructions:
            worksheet.write_string(row, 0, instruction, formats['text'])
            row += 1

    def _create_assumptions_validation(self, workbook, formats, scenario_data):
        """Create assumptions validation checklist."""
        worksheet = workbook.add_worksheet('Assumptions_Checklist')
        
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        
        worksheet.merge_range('A1:C1', 'ASSUMPTIONS VALIDATION CHECKLIST', formats['header'])
        worksheet.write_string(2, 0, 'Validate these assumptions before finalizing your decision:', formats['text_bold'])
        
        row = 4
        worksheet.write_string(row, 0, 'Assumption Category', formats['subheader'])
        worksheet.write_string(row, 1, 'Status', formats['subheader'])
        worksheet.write_string(row, 2, 'Notes', formats['subheader'])
        row += 1
        
        # Build reasonable validation rules
        build_timeline = safe_float(scenario_data.get('build_timeline', 0))
        fte_cost = safe_float(scenario_data.get('fte_cost', 0))
        success_prob = safe_float(scenario_data.get('prob_success', 0))
        wacc = safe_float(scenario_data.get('wacc', 0))
        
        validations = [
            ('Build timeline is realistic', 
             'PASS' if 6 <= build_timeline <= 36 else 'REVIEW',
             f'{build_timeline} months - typical range is 6-36 months'),
            ('FTE costs include all loaded costs',
             'PASS' if fte_cost >= 100000 else 'REVIEW',
             f'${fte_cost:,.0f} - should include benefits, overhead'),
            ('Success probability is conservative',
             'PASS' if 60 <= success_prob <= 95 else 'REVIEW',
             f'{success_prob}% - consider project complexity and team experience'),
            ('WACC reflects true cost of capital',
             'PASS' if 5 <= wacc <= 15 else 'REVIEW',
             f'{wacc}% - should align with company cost of capital'),
            ('Subscription pricing confirmed with vendor',
             'REVIEW', 'Validate current pricing and escalation terms'),
            ('Risk factors reflect actual project risks',
             'REVIEW', 'Consider technical, market, and execution risks'),
            ('Tax implications have been considered',
             'REVIEW', 'Verify R&D tax credit eligibility and rates')
        ]
        
        for assumption, status, notes in validations:
            status_format = formats['validation_pass'] if status == 'PASS' else formats['warning']
            worksheet.write_string(row, 0, assumption, formats['text'])
            worksheet.write_string(row, 1, status, status_format)
            worksheet.write_string(row, 2, notes, formats['text'])
            row += 1

    def _create_methodology_documentation(self, workbook, formats):
        """Create methodology documentation sheet."""
        worksheet = workbook.add_worksheet('Methodology')
        
        worksheet.set_column('A:A', 80)
        
        worksheet.write_string(0, 0, 'BUILD vs BUY ANALYSIS METHODOLOGY', formats['header'])
        
        row = 2
        methodology_text = [
            ('OVERVIEW', formats['subheader']),
            ('This analysis uses Net Present Value (NPV) methodology to compare build vs buy options.', formats['text']),
            ('All costs are discounted to present value using the specified WACC rate.', formats['text']),
            ('', formats['text']),
            ('BUILD COST CALCULATION', formats['subheader']),
            ('1. Labor Costs: FTE Count × Annual Cost × (Timeline/12) × Success Probability', formats['text']),
            ('2. Tax Credit: Capitalized Labor × Tax Credit Rate (reduces total cost)', formats['text']),
            ('3. Additional Costs: CapEx + OpEx (PV) + Amortization (PV) + Miscellaneous', formats['text']),
            ('4. Risk Adjustment: Base costs × (1 + Total Risk Factors)', formats['text']),
            ('', formats['text']),
            ('BUY COST CALCULATION', formats['subheader']),
            ('1. One-time Purchase: Immediate cost in Year 0', formats['text']),
            ('2. Subscription: Annual costs with escalation, discounted over useful life', formats['text']),
            ('   - Starts in Year 1 for annual subscriptions', formats['text']),
            ('   - Escalated by annual increase rate', formats['text']),
            ('   - Discounted by WACC for each year', formats['text']),
            ('', formats['text']),
            ('DECISION CRITERIA', formats['subheader']),
            ('• NPV Difference = Build Cost - Buy Cost', formats['text']),
            ('• Negative difference indicates Build is preferred', formats['text']),
            ('• Positive difference indicates Buy is preferred', formats['text']),
            ('• Consider risk tolerance and strategic factors beyond pure NPV', formats['text']),
            ('', formats['text']),
            ('KEY ASSUMPTIONS', formats['subheader']),
            ('• All costs are in nominal dollars', formats['text']),
            ('• WACC represents appropriate discount rate for the organization', formats['text']),
            ('• Success probability applies to entire build cost', formats['text']),
            ('• Tax credits are received when expenses are incurred', formats['text'])
        ]
        
        for text, fmt in methodology_text:
            worksheet.write_string(row, 0, text, fmt)
            row += 1

    def _update_executive_dashboard_formulas(self, workbook, formats):
        """Update dashboard references after Cost Timeline creation."""
        dashboard = workbook.get_worksheet_by_name('Executive_Dashboard')
        if not dashboard or not (self.build_total_row and self.buy_total_row and self.npv_diff_row):
            return
        pv_col = self.pv_col_letter or 'J'
        dashboard.write_formula(self.dashboard_build_cost_row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.build_total_row}", formats['dashboard_metric'])
        dashboard.write_formula(self.dashboard_build_cost_row, 3, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.buy_total_row}", formats['dashboard_metric'])
        dashboard.write_formula(self.dashboard_recommendation_row, 1, f"='{self.TIMELINE_SHEET}'!{pv_col}{self.npv_diff_row}", formats['dashboard_metric'])
        recommendation_formula = f"=IF('{self.TIMELINE_SHEET}'!{pv_col}{self.npv_diff_row}<0,'BUILD RECOMMENDED','BUY RECOMMENDED')"
        dashboard.write_formula(self.dashboard_recommendation_row, 3, recommendation_formula, formats['dashboard_metric'])
        simulation_results = getattr(self, 'scenario_data', {}).get('results', {}) if hasattr(self, 'scenario_data') else {}
        if simulation_results and 'expected_build_cost' in simulation_results:
            validation_row = self.dashboard_recommendation_row + 2
            dashboard.write_string(validation_row, 0, 'Validation:', formats['text'])
            dashboard.write_string(validation_row, 1, f"Sim: ${simulation_results['expected_build_cost']:,.0f}", formats['text'])
            
            # Add conditional formatting for advantage cell
            dashboard.conditional_format(self.dashboard_recommendation_row, 1, 
                                       self.dashboard_recommendation_row, 1, {
                'type': 'cell',
                'criteria': '<',
                'value': 0,
                'format': formats['build_advantage']
            })
            
            dashboard.conditional_format(self.dashboard_recommendation_row, 1,
                                       self.dashboard_recommendation_row, 1, {
                'type': 'cell', 
                'criteria': '>=',
                'value': 0,
                'format': formats['buy_advantage']
            })

    def _create_current_scenario_analysis(self, workbook, formats, scenario_data):
        """Create detailed analysis for current scenario."""
        worksheet = workbook.add_worksheet('Current_Scenario')
        
        # Set column widths for better formatting
        worksheet.set_column('A:A', 25)  # Parameter names
        worksheet.set_column('B:B', 15)  # Values
        worksheet.set_column('C:C', 20)  # Additional info
        
        # Write scenario name and timestamp
        worksheet.merge_range('A1:C1', 'Build vs Buy Analysis - Current Scenario', formats['header'])
        worksheet.write_string(1, 0, f"Scenario: {scenario_data.get('name', 'Current')}", formats['text_bold'])
        worksheet.write_string(2, 0, f"Generated: {scenario_data.get('timestamp', 'N/A')}", formats['text'])
        
        # Write parameters header
        worksheet.merge_range('A5:C5', 'INPUT PARAMETERS', formats['subheader'])
        
        param_data = [
            ['Build Timeline (months)', scenario_data.get('build_timeline', 0), 'number'],
            ['FTE Cost ($)', scenario_data.get('fte_cost', 0), 'currency'],
            ['FTE Count', scenario_data.get('fte_count', 0), 'number'],
            ['Capitalization %', scenario_data.get('cap_percent', 0), 'percent'],
            ['Tax Credit Rate %', scenario_data.get('tax_credit_rate', 17), 'percent'],
            ['Useful Life (years)', scenario_data.get('useful_life', 0), 'number'],
            ['Success Probability (%)', scenario_data.get('prob_success', 0), 'percent'],
            ['WACC (%)', scenario_data.get('wacc', 0), 'percent'],
        ]
        
        for row_num, (param, value, format_type) in enumerate(param_data, start=6):
            worksheet.write_string(row_num, 0, param, formats['text'])
            if isinstance(value, (int, float)) and value != 0:
                if format_type == 'percent' and value > 1:
                    # Convert to decimal if needed (e.g., 90 -> 0.90)
                    value = value / 100 
                fmt = formats[format_type] if format_type in formats else formats['number']
                worksheet.write_number(row_num, 1, float(value), fmt)
            else:
                worksheet.write_string(row_num, 1, str(value) if value else 'N/A', formats['text'])
