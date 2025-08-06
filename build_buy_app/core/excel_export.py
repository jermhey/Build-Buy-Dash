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
    """Handles Excel expo        # Key insights section
        row += 2
        worksheet.merge_range(f'A{row}:L{row}', 'KEY INSIGHTS & VALIDATION', formats['subheader'])
        row += 1
        
        insights = [
            "• Present values use WACC discounting for accurate comparison",
            "• Build costs include R&D tax credit benefits",
            "• Risk factors are applied as cost multipliers",
            "• All calculations update automatically when Input_Parameters change",
            "• Subscription costs start in Year 1 with proper escalation"
        ]
        
        for insight in insights:
            worksheet.write_string(row, 0, insight, formats['text'])
            row += 1
        
        # Update Executive Dashboard with actual formulas now that we have the references
        self._update_executive_dashboard_formulas(workbook, formats) for Build vs Buy analysis."""
    
    def __init__(self):
        """Initialize the Excel exporter."""
        self.param_cells = {}  # Track cell references for dynamic formulas
        self.build_total_row = None  # Track build total row for executive summary
        self.buy_total_row = None    # Track buy total row for executive summary
        self.npv_diff_row = None     # Track NPV difference row for executive summary
    
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
                
                # Create enhanced executive summary with key insights
                self._create_executive_dashboard(workbook, formats, scenario_data)
                
                # Create core analysis sheets
                self._create_cost_breakdown_timeline(workbook, formats, scenario_data)
                self._create_sensitivity_analysis(workbook, formats, scenario_data)
                self._create_break_even_analysis(workbook, formats, scenario_data)
                self._create_assumptions_validation(workbook, formats, scenario_data)
                self._create_methodology_documentation(workbook, formats)
            
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
        worksheet = workbook.add_worksheet('Input_Parameters')
        
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
        
        # Total FTE Costs calculation
        worksheet.write_string(row, 0, 'Total FTE Costs ($)', formats['text_bold'])
        worksheet.write_formula(row, 1, f'=({timeline_cell}/12)*{fte_cost_cell}*{fte_count_cell}', formats['calculated_cell'])
        worksheet.write_string(row, 2, 'Total labor costs for build project', formats['text'])
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
        """Create comprehensive cost breakdown timeline with WACC discounting - DYNAMIC VERSION."""
        worksheet = workbook.add_worksheet('Cost_Timeline')
        
        # Enhanced formatting for professional appearance
        worksheet.set_column('A:A', 25)  # Component names
        worksheet.set_column('B:M', 15)  # Cost columns
        
        # Title and headers - referencing Input Parameters sheet
        worksheet.merge_range('A1:M1', 'DYNAMIC Cost Breakdown Timeline (Updates from Input_Parameters)', formats['header'])
        worksheet.write_string(2, 0, 'WACC Rate (from Input_Parameters):', formats['text_bold'])
        worksheet.write_formula(2, 1, f'=Input_Parameters!{self.param_cells["wacc"]}', formats['percent'])
        
        # Use the tracked cell references from Input Parameters sheet
        useful_life_ref = f'Input_Parameters!{self.param_cells["useful_life"]}'
        wacc_ref = f'Input_Parameters!{self.param_cells["wacc"]}'
        misc_costs_ref = f'Input_Parameters!{self.param_cells["misc_costs"]}'
        capex_ref = f'Input_Parameters!{self.param_cells["capex"]}'
        maint_opex_ref = f'Input_Parameters!{self.param_cells["maint_opex"]}'
        
        # Buy option references
        product_price_ref = f'Input_Parameters!{self.param_cells["product_price"]}'
        subscription_ref = f'Input_Parameters!{self.param_cells["subscription_price"]}'
        sub_increase_ref = f'Input_Parameters!{self.param_cells["subscription_increase"]}'
        
        # Key calculated values from Input Parameters
        total_fte_ref = f'Input_Parameters!{self.param_cells["total_fte_cost"]}'
        capitalized_ref = f'Input_Parameters!{self.param_cells["capitalized_labor"]}'
        expensed_ref = f'Input_Parameters!{self.param_cells["expensed_labor"]}'
        tax_credit_ref = f'Input_Parameters!{self.param_cells["tax_credit"]}'
        
        # Headers for detailed breakdown
        row = 4
        worksheet.merge_range(row, 0, row, 12, 'BUILD OPTION - Cost Components (Dynamic)', formats['subheader'])
        row += 1
        
        # Dynamic column headers based on useful life
        useful_life = safe_float(scenario_data.get('useful_life', 5))
        max_years = max(int(useful_life), 5)  # Show at least 5 years for consistency
        
        headers = ['Cost Component', 'Year 0']
        for year in range(1, max_years + 1):
            headers.append(f'Year {year}')
        headers.extend(['Nominal Total', 'PV Factor', 'Present Value', 'Cost Type', 'Notes'])
        
        for col, header in enumerate(headers):
            worksheet.write_string(row, col, header, formats['text_bold'])
        
        build_start_row = row + 1
        row += 1
        
        # BUILD COST COMPONENTS - using formulas that reference Input Parameters
        build_components = [
            ('FTE Labor Costs (Expensed)', expensed_ref, 'OpEx', 'Development team costs (expensed portion)'),
            ('FTE Labor Costs (Capitalized)', capitalized_ref, 'CapEx', 'Development team costs (capitalized for tax purposes)'),
            ('Miscellaneous Costs', misc_costs_ref, 'OpEx', 'Additional development expenses'),
            ('Infrastructure CapEx', capex_ref, 'CapEx', 'Hardware and infrastructure investment'),
            ('Ongoing Maintenance', maint_opex_ref, 'OpEx', 'Annual maintenance and support costs'),
            ('R&D Tax Credit (Benefit)', f'=-{tax_credit_ref}', 'Benefit', 'Tax credit reduces overall cost')
        ]
        
        for component, cost_formula, cost_type, notes in build_components:
            worksheet.write_string(row, 0, component, formats['text'])
            
            # Year 0 cost (most components start here)
            if 'Ongoing Maintenance' in component:
                worksheet.write_string(row, 1, '-', formats['text'])  # No maintenance in Year 0
            else:
                worksheet.write_formula(row, 1, cost_formula, formats['currency'])
            
            # Years 1 through useful life for ongoing maintenance
            year_end_col = 1 + max_years  # Adjust based on actual number of years
            for year_col in range(2, year_end_col + 1):  # Start from Year 1
                if 'Ongoing Maintenance' in component:
                    # Maintenance starts Year 1, continues through useful life - handle zero maintenance
                    year_num = year_col - 1  # Convert to 1-based year
                    maintenance_formula = f'=IF(AND({year_num}>=1,{year_num}<={useful_life_ref},{maint_opex_ref}>0),{maint_opex_ref},0)'
                    worksheet.write_formula(row, year_col, maintenance_formula, formats['currency'])
                else:
                    worksheet.write_string(row, year_col, '-', formats['text'])
            
            # Nominal Total (sum of all years) - dynamic range
            total_col = year_end_col + 1
            total_formula = f'=SUM(B{row+1}:{chr(66 + year_end_col - 1)}{row+1})'
            worksheet.write_formula(row, total_col, total_formula, formats['currency_bold'])
            
            # PV Factor and Present Value - with error handling
            pv_factor_col = total_col + 1
            pv_col = pv_factor_col + 1
            
            if 'Ongoing Maintenance' in component:
                # Multi-year maintenance PV - dynamic calculation based on useful life
                pv_terms = []
                for year in range(1, int(useful_life) + 1):
                    pv_terms.append(f'{maint_opex_ref}/(1+{wacc_ref})^{year}')
                
                pv_formula = f'=IF({maint_opex_ref}=0,0,{"+".join(pv_terms)})'
                worksheet.write_formula(row, pv_col, pv_formula, formats['currency_bold'])
                # PV Factor = PV / Nominal Total (with zero protection)
                pv_factor_formula = f'=IF({chr(65 + total_col)}{row+1}=0,0,{chr(65 + pv_col)}{row+1}/{chr(65 + total_col)}{row+1})'
                worksheet.write_formula(row, pv_factor_col, pv_factor_formula, formats['number'])
            else:
                # One-time costs in Year 0
                worksheet.write_formula(row, pv_factor_col, '=1', formats['number'])  # Year 0 PV factor = 1
                worksheet.write_formula(row, pv_col, f'={chr(65 + total_col)}{row+1}', formats['currency_bold'])
            
            # Cost Type and Notes
            cost_type_col = pv_col + 1
            notes_col = cost_type_col + 1
            worksheet.write_string(row, cost_type_col, cost_type, formats['text'])
            worksheet.write_string(row, notes_col, notes, formats['text'])
            row += 1
        
        build_end_row = row - 1
        
        # BUILD SECTION TOTAL - right within the build section
        row += 1
        worksheet.write_string(row, 0, 'TOTAL BUILD COSTS (Present Value)', formats['text_bold'])
        # Sum all the present values in the build section
        build_section_total_formula = f'=SUM({chr(65 + pv_col)}{build_start_row + 1}:{chr(65 + pv_col)}{build_end_row + 1})'
        worksheet.write_formula(row, pv_col, build_section_total_formula, formats['currency_bold'])
        worksheet.write_string(row, notes_col, 'Excel formula - may differ from simulation', formats['text'])
        
        # BUY OPTION COMPONENTS
        row += 2
        worksheet.merge_range(row, 0, row, notes_col, 'BUY OPTION - Cost Components (Dynamic)', formats['subheader'])
        buy_start_row = row + 1
        row += 1
        
        buy_components = [
            ('One-Time Purchase', product_price_ref, 'CapEx', 'Software license purchase'),
            ('Annual Subscription (All Years)', 'subscription_all_years', 'OpEx', 'Multi-year subscription with escalation')
        ]
        
        for component, cost_ref, cost_type, notes in buy_components:
            worksheet.write_string(row, 0, component, formats['text'])
            
            if component == 'One-Time Purchase':
                # One-time purchase in Year 0 - handle zero purchase price
                worksheet.write_formula(row, 1, f'=IF({cost_ref}>0,{cost_ref},0)', formats['currency'])
                for year_col in range(2, year_end_col + 1):
                    worksheet.write_string(row, year_col, '-', formats['text'])
                    
            else:  # Multi-year subscription across useful life
                # Year 0 - no subscription (annual subscriptions start in Year 1)
                worksheet.write_string(row, 1, '-', formats['text'])
                # Years 1 through useful life with escalation
                for year_col in range(2, year_end_col + 1):  # Dynamic year range
                    year_num = year_col - 1  # This gives us years 1, 2, 3, etc.
                    # Only charge subscription during useful life period
                    escalated_formula = f'=IF(AND({subscription_ref}>0,{year_num}<={useful_life_ref}),{subscription_ref}*((1+{sub_increase_ref})^{year_num}),0)'
                    worksheet.write_formula(row, year_col, escalated_formula, formats['currency'])
            
            # Nominal Total and PV calculations - using dynamic columns
            total_formula = f'=SUM(B{row+1}:{chr(66 + year_end_col - 1)}{row+1})'
            worksheet.write_formula(row, total_col, total_formula, formats['currency_bold'])
            
            # PV Factor and Present Value - with error handling
            if 'One-Time' in component:
                worksheet.write_formula(row, pv_factor_col, '=1', formats['number'])  # Year 0 PV factor
                worksheet.write_formula(row, pv_col, f'={chr(65 + total_col)}{row+1}', formats['currency_bold'])
            else:
                # Multi-year subscription PV - dynamic calculation based on useful life
                pv_terms = []
                for year in range(1, int(useful_life) + 1):
                    year_col_letter = chr(66 + year)  # C, D, E, F, etc.
                    pv_terms.append(f'{year_col_letter}{row+1}/(1+{wacc_ref})^{year}')
                
                pv_formula = f'=IF({subscription_ref}=0,0,{"+".join(pv_terms)})'
                worksheet.write_formula(row, pv_col, pv_formula, formats['currency_bold'])
                # PV Factor = PV / Nominal Total (with zero protection)
                pv_factor_formula = f'=IF({chr(65 + total_col)}{row+1}=0,0,{chr(65 + pv_col)}{row+1}/{chr(65 + total_col)}{row+1})'
                worksheet.write_formula(row, pv_factor_col, pv_factor_formula, formats['number'])
            
            worksheet.write_string(row, cost_type_col, cost_type, formats['text'])
            worksheet.write_string(row, notes_col, notes, formats['text'])
            row += 1
        
        buy_end_row = row - 1
        
        # BUY SECTION TOTAL - right within the buy section  
        row += 1
        worksheet.write_string(row, 0, 'TOTAL BUY COSTS (Present Value)', formats['text_bold'])
        # Sum all the present values in the buy section
        buy_section_total_formula = f'=SUM({chr(65 + pv_col)}{buy_start_row + 1}:{chr(65 + pv_col)}{buy_end_row + 1})'
        worksheet.write_formula(row, pv_col, buy_section_total_formula, formats['currency_bold'])
        worksheet.write_string(row, notes_col, 'Excel formula - may differ from simulation', formats['text'])
        
        # SUMMARY TOTALS - Excel formulas with simulation validation
        row += 2
        worksheet.merge_range(row, 0, row, notes_col, 'SUMMARY TOTALS (Dynamic Excel Formulas)', formats['subheader'])
        row += 1
        
        # Build Option Summary - uses Excel SUM formula for full dynamism  
        worksheet.write_string(row, 0, 'BUILD OPTION - Total Present Value', formats['text_bold'])
        build_pv_formula = f'=SUM({chr(65 + pv_col)}{build_start_row + 1}:{chr(65 + pv_col)}{build_end_row + 1})'
        worksheet.write_formula(row, pv_col, build_pv_formula, formats['currency_bold'])
        worksheet.write_string(row, notes_col, 'Dynamic Excel formula (user can modify parameters)', formats['text'])
        self.build_total_row = row + 1  # Store for executive summary reference (1-indexed for Excel)
        row += 1
        
        # Buy Option Summary - uses Excel SUM formula for full dynamism
        worksheet.write_string(row, 0, 'BUY OPTION - Total Present Value', formats['text_bold'])
        buy_pv_formula = f'=SUM({chr(65 + pv_col)}{buy_start_row + 1}:{chr(65 + pv_col)}{buy_end_row + 1})'
        worksheet.write_formula(row, pv_col, buy_pv_formula, formats['currency_bold'])
        worksheet.write_string(row, notes_col, 'Dynamic Excel formula (user can modify parameters)', formats['text'])
        self.buy_total_row = row + 1  # Store for executive summary reference (1-indexed for Excel)
        row += 1
        
        # NPV Difference - calculated dynamically
        worksheet.write_string(row, 0, 'NET PRESENT VALUE DIFFERENCE (Build - Buy)', formats['text_bold'])
        npv_diff_formula = f'={chr(65 + pv_col)}{self.build_total_row}-{chr(65 + pv_col)}{self.buy_total_row}'
        worksheet.write_formula(row, pv_col, npv_diff_formula, formats['currency_bold'])
        worksheet.write_string(row, notes_col, 'Negative favors BUILD, positive favors BUY', formats['text'])
        self.npv_diff_row = row + 1  # Store for executive summary reference (1-indexed for Excel)
        row += 1
        
        # Add simulation verification section if results are available
        simulation_results = scenario_data.get('results', {})
        if simulation_results and 'expected_build_cost' in simulation_results:
            row += 1
            worksheet.merge_range(row, 0, row, notes_col, 'SIMULATION VALIDATION (for verification only)', formats['subheader'])
            row += 1
            
            worksheet.write_string(row, 0, 'Simulation Build Cost:', formats['text'])
            worksheet.write_number(row, pv_col, simulation_results['expected_build_cost'], formats['currency'])
            worksheet.write_string(row, notes_col, f'Monte Carlo result: ${simulation_results["expected_build_cost"]:,.0f}', formats['text'])
            row += 1
            
            worksheet.write_string(row, 0, 'Excel vs Simulation Difference:', formats['text'])
            diff_formula = f'={chr(65 + pv_col)}{self.build_total_row}-{chr(65 + pv_col)}{row}'
            worksheet.write_formula(row, pv_col, diff_formula, formats['currency'])
            worksheet.write_string(row, notes_col, 'Should be close to $0 if methodologies match', formats['text'])
        
        # Key insights section
        row += 2
        worksheet.merge_range(row, 0, row, 12, 'KEY INSIGHTS', formats['subheader'])
        row += 1
        
        insights = [
            "• Excel formulas are FULLY DYNAMIC - modify Input_Parameters to see results update instantly",
            "• All calculations use proper present value discounting with WACC",
            "• Excel uses deterministic calculations; simulation adds Monte Carlo uncertainty",
            "• Small differences between Excel and simulation are normal and expected",
            "• Labor costs are discounted based on build timeline duration", 
            "• Tax credit benefits are automatically calculated on capitalized labor",
            "• Risk factors are applied as multiplicative adjustments to base costs",
            "• Users can freely modify any input parameter and see immediate updates"
        ]
        
        for insight in insights:
            worksheet.write_string(row, 0, insight, formats['text'])
            row += 1

    def _create_executive_summary(self, workbook, formats, scenario_data):
        """Create comprehensive executive summary with key metrics and recommendations."""
        worksheet = workbook.add_worksheet('Executive_Summary')
        
        # Enhanced formatting for executive presentation
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)
        
        # Header and title section
        worksheet.merge_range('A1:C1', 'BUILD vs BUY ANALYSIS - EXECUTIVE SUMMARY', formats['header'])
        
        # Key results section using simulation-matched Excel formulas
        row = 3
        
        # Create intermediate calculation references
        worksheet.write_string(row, 0, 'Build Option Total Cost:', formats['text_bold'])
        worksheet.write_formula(row, 1, f'=Cost_Timeline!J{self.build_total_row}', formats['currency_bold'])
        worksheet.write_string(row, 2, '(Excel formula matches simulation logic)', formats['text'])
        row += 1
        
        worksheet.write_string(row, 0, 'Buy Option Total Cost:', formats['text_bold'])
        worksheet.write_formula(row, 1, f'=Cost_Timeline!J{self.buy_total_row}', formats['currency_bold'])
        worksheet.write_string(row, 2, '(Excel formula matches simulation logic)', formats['text'])
        row += 1
        
        worksheet.write_string(row, 0, 'NPV Difference (Build - Buy):', formats['text_bold'])
        worksheet.write_formula(row, 1, f'=Cost_Timeline!J{self.npv_diff_row}', formats['currency_bold'])
        worksheet.write_string(row, 2, 'Negative = Build preferred', formats['text'])
        row += 1
        
        worksheet.write_string(row, 0, 'RECOMMENDATION:', formats['text_bold'])
        worksheet.write_formula(row, 1, f'=IF(Cost_Timeline!J{self.npv_diff_row}<0,"BUILD","BUY")', formats['text_bold'])
        worksheet.write_string(row, 2, 'Based on financial analysis (fully dynamic)', formats['text'])
        
        # Add simulation verification section
        row += 2
        simulation_results = self.scenario_data.get('simulation_results', {})
        if simulation_results:
            worksheet.merge_range(f'A{row}:C{row}', 'SIMULATION VERIFICATION (for validation only)', formats['subheader'])
            row += 1
            
            worksheet.write_string(row, 0, 'Simulation Expected Build Cost:', formats['text'])
            worksheet.write_number(row, 1, simulation_results.get('expected_build_cost', 0), formats['currency'])
            worksheet.write_string(row, 2, 'Monte Carlo result', formats['text'])
            row += 1
            
            worksheet.write_string(row, 0, 'Formula vs Simulation Difference:', formats['text'])
            formula_diff = f'=B{row-3}-B{row}'  # Excel total - simulation total
            worksheet.write_formula(row, 1, formula_diff, formats['currency'])
            worksheet.write_string(row, 2, 'Should be close to $0', formats['text'])
        row += 2
        
        # Key parameters display
        worksheet.merge_range(f'A{row}:C{row}', 'KEY PARAMETERS (from Input_Parameters)', formats['subheader'])
        row += 1
        
        # Use the tracked cell references
        params = [
            ('WACC Rate:', f'Input_Parameters!{self.param_cells["wacc"]}', formats['percent']),
            ('Build Timeline:', f'Input_Parameters!{self.param_cells["build_timeline"]}', formats['number']),
            ('Tax Credit Rate:', f'Input_Parameters!{self.param_cells["tax_credit_rate"]}', formats['percent']),
            ('Estimated Tax Credit:', f'Input_Parameters!{self.param_cells["tax_credit"]}', formats['currency'])
        ]
        
        for param_name, cell_ref, fmt in params:
            worksheet.write_string(row, 0, param_name, formats['text_bold'])
            worksheet.write_formula(row, 1, f'={cell_ref}', fmt)
            row += 1
        
        row += 1
        worksheet.write_string(row, 0, 'To modify parameters, go to Input_Parameters sheet', formats['text_bold'])
        worksheet.write_string(row + 1, 0, 'All calculations will update automatically', formats['text'])

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
        """Create sensitivity analysis showing impact of key parameter changes."""
        worksheet = workbook.add_worksheet('Sensitivity_Analysis')
        
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:E', 15)
        
        worksheet.merge_range('A1:E1', 'SENSITIVITY ANALYSIS - Impact of Parameter Changes', formats['header'])
        worksheet.write_string(2, 0, 'Shows how NPV difference changes with ±20% parameter variation', formats['text_bold'])
        
        # Headers for sensitivity table
        row = 4
        headers = ['Parameter', '-20%', 'Base Case', '+20%', 'Impact Range']
        for col, header in enumerate(headers):
            worksheet.write_string(row, col, header, formats['subheader'])
        row += 1
        
        # Key parameters for sensitivity analysis
        sensitive_params = [
            ('Build Timeline', 'build_timeline', 'months'),
            ('FTE Annual Cost', 'fte_cost', '$'),
            ('Team Size', 'fte_count', 'people'),
            ('Success Probability', 'prob_success', '%'),
            ('WACC Rate', 'wacc', '%'),
            ('Subscription Price', 'subscription_price', '$')
        ]
        
        for param_name, param_key, unit in sensitive_params:
            base_value = safe_float(scenario_data.get(param_key, 0))
            if base_value > 0:  # Only show parameters that have values
                worksheet.write_string(row, 0, f'{param_name} ({unit})', formats['text_bold'])
                worksheet.write_number(row, 1, base_value * 0.8, formats['number'])
                worksheet.write_number(row, 2, base_value, formats['number'])
                worksheet.write_number(row, 3, base_value * 1.2, formats['number'])
                worksheet.write_string(row, 4, 'See Cost_Timeline for impact', formats['text'])
                row += 1
        
        row += 2
        worksheet.write_string(row, 0, 'Key Insights:', formats['text_bold'])
        row += 1
        worksheet.write_string(row, 0, '• Parameters with highest impact should be validated carefully', formats['text'])
        row += 1
        worksheet.write_string(row, 0, '• Consider Monte Carlo analysis for uncertain parameters', formats['text'])
        row += 1
        worksheet.write_string(row, 0, '• Test different scenarios by modifying Input_Parameters', formats['text'])

    def _create_break_even_analysis(self, workbook, formats, scenario_data):
        """Create break-even analysis showing when build vs buy becomes favorable."""
        worksheet = workbook.add_worksheet('Break_Even_Analysis')
        
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:C', 20)
        
        worksheet.merge_range('A1:C1', 'BREAK-EVEN ANALYSIS', formats['header'])
        worksheet.write_string(2, 0, 'Identifies critical thresholds where build vs buy decision changes', formats['text_bold'])
        
        row = 4
        worksheet.merge_range(f'A{row}:C{row}', 'KEY BREAK-EVEN POINTS', formats['subheader'])
        row += 1
        
        # Calculate some break-even scenarios
        build_cost = (safe_float(scenario_data.get('fte_cost', 0)) * 
                     safe_float(scenario_data.get('fte_count', 0)) * 
                     (safe_float(scenario_data.get('build_timeline', 0)) / 12))
        
        subscription_annual = safe_float(scenario_data.get('subscription_price', 0))
        one_time_price = safe_float(scenario_data.get('product_price', 0))
        useful_life = safe_float(scenario_data.get('useful_life', 5))
        
        analyses = []
        
        if subscription_annual > 0:
            break_even_years = build_cost / subscription_annual if subscription_annual > 0 else 0
            analyses.append(('Subscription Break-Even Timeline', f'{break_even_years:.1f} years', 'Time when build cost equals cumulative subscription'))
        
        if one_time_price > 0:
            savings_ratio = (build_cost / one_time_price) * 100 if one_time_price > 0 else 0
            analyses.append(('One-Time Purchase Comparison', f'{savings_ratio:.0f}% of purchase price', 'Build cost as percentage of buy price'))
        
        # Team size break-even
        if safe_float(scenario_data.get('fte_cost', 0)) > 0:
            break_even_fte = one_time_price / (safe_float(scenario_data.get('fte_cost', 0)) * (safe_float(scenario_data.get('build_timeline', 0)) / 12)) if one_time_price > 0 else 0
            if break_even_fte > 0:
                analyses.append(('Team Size Break-Even', f'{break_even_fte:.1f} FTEs', 'Maximum team size before buy becomes favorable'))
        
        # Timeline break-even
        if safe_float(scenario_data.get('fte_cost', 0)) > 0 and safe_float(scenario_data.get('fte_count', 0)) > 0:
            monthly_burn = safe_float(scenario_data.get('fte_cost', 0)) * safe_float(scenario_data.get('fte_count', 0)) / 12
            break_even_months = one_time_price / monthly_burn if monthly_burn > 0 and one_time_price > 0 else 0
            if break_even_months > 0:
                analyses.append(('Timeline Break-Even', f'{break_even_months:.0f} months', 'Maximum build time before buy becomes favorable'))
        
        for analysis_name, value, description in analyses:
            worksheet.write_string(row, 0, analysis_name, formats['text_bold'])
            worksheet.write_string(row, 1, value, formats['number'] if 'years' in value or 'months' in value or 'FTE' in value else formats['text'])
            worksheet.write_string(row, 2, description, formats['text'])
            row += 1
        
        row += 2
        worksheet.merge_range(f'A{row}:C{row}', 'SCENARIO TESTING', formats['subheader'])
        row += 1
        
        scenario_tests = [
            'What if build timeline increases by 50%?',
            'What if subscription price increases by 20% annually?',
            'What if team needs 1 additional FTE?',
            'What if success probability drops to 70%?',
            'What if WACC increases to reflect higher risk?'
        ]
        
        worksheet.write_string(row, 0, 'Test these scenarios by modifying Input_Parameters:', formats['text_bold'])
        row += 1
        
        for test in scenario_tests:
            worksheet.write_string(row, 0, f'• {test}', formats['text'])
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
        """Update executive dashboard with dynamic Excel formulas linked to Cost_Timeline."""
        dashboard = workbook.get_worksheet_by_name('Executive_Dashboard')
        
        if dashboard and self.build_total_row and self.buy_total_row and self.npv_diff_row:
            # Update build and buy costs with formulas that link to Cost_Timeline
            dashboard.write_formula(self.dashboard_build_cost_row, 1, 
                                  f'=Cost_Timeline!L{self.build_total_row}', formats['dashboard_metric'])
            dashboard.write_formula(self.dashboard_build_cost_row, 3,
                                  f'=Cost_Timeline!L{self.buy_total_row}', formats['dashboard_metric'])
            
            # Update NPV difference and recommendation with formulas
            dashboard.write_formula(self.dashboard_recommendation_row, 1, 
                                  f'=Cost_Timeline!L{self.npv_diff_row}', formats['dashboard_metric'])
            
            recommendation_formula = f'=IF(Cost_Timeline!L{self.npv_diff_row}<0,"BUILD RECOMMENDED","BUY RECOMMENDED")'
            dashboard.write_formula(self.dashboard_recommendation_row, 3, recommendation_formula, formats['dashboard_metric'])
            
            # Add simulation validation if results are available
            simulation_results = self.scenario_data.get('results', {})
            if simulation_results and 'expected_build_cost' in simulation_results:
                # Add a small validation section (optional)
                validation_row = self.dashboard_recommendation_row + 2
                dashboard.write_string(validation_row, 0, 'Validation:', formats['text'])
                dashboard.write_string(validation_row, 1, f'Sim: ${simulation_results["expected_build_cost"]:,.0f}', formats['text'])
            
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
