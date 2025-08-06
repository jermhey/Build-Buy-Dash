# Build vs Buy Decision Platform - Handoff Documentation

## Project Overview
Professional web application for strategic build vs buy decision analysis using Monte Carlo simulation, built with Python/Dash.

## 🏗️ Architecture & Key Files

### **Core Application**
- `app.py` - Main Dash application with UI and callbacks (1,291 lines)
- `src/simulation.py` - Monte Carlo simulation engine
- `src/utils.py` - Utility functions and validation

### **User Interface**
- `ui/modern_ui.py` - Modern Bootstrap-based UI components
- All callbacks are handled directly in `app.py` for simplicity

### **Business Logic**
- `core/excel_export.py` - Comprehensive Excel report generation (1,027 lines)
- `core/advanced_analytics.py` - Advanced charts and analytics
- `data/config_manager.py` - Configuration and parameter management
- `data/scenario_manager.py` - Scenario save/load functionality

### **Configuration**
- `config/parameters.py` - Default parameters and settings
- `requirements.txt` - Python dependencies

### **Testing & Validation**
- `tests/test_simulation.py` - Main test suite ✅
- `tests/wacc_validation.py` - Financial calculation validation
- `tests/excel_simulation_comparison.py` - Excel vs simulation consistency
- `tests/comprehensive_validation.py` - Full system validation
- Additional specialized test files for edge cases

## 🚀 Quick Start
```bash
cd build_buy_app
pip install -r requirements.txt
python app.py
```
Access at: http://127.0.0.1:8060

## 🧪 Testing
```bash
python tests/test_simulation.py
```

## 🔧 Key Features Implemented
- ✅ Monte Carlo simulation with uncertainty modeling
- ✅ Dynamic Excel export with formulas (maintains user flexibility)
- ✅ Professional UI with modern Bootstrap styling  
- ✅ Scenario management and comparison
- ✅ Risk factor modeling (technical, vendor, market)
- ✅ WACC-based present value calculations
- ✅ R&D tax credit support
- ✅ Multiple buy options (one-time, subscription)
- ✅ Comprehensive validation and testing

## 🗂️ Recent Improvements
1. **Excel Export Enhancement** - Fixed value consistency issues while maintaining dynamic formulas
2. **Repository Cleanup** - Removed duplicate nested folder structure
3. **File Cleanup** - Removed unused/duplicate files for cleaner handoff

## 📋 Files Removed for Clarity
- `core/excel_export_clean.py` (empty file)
- `core/utils_enhanced.py` (duplicate functionality)
- `ui/callbacks.py` (unused, callbacks in app.py)
- Empty scenario directories

## 🎯 Production Ready
- All tests passing ✅
- Clean, maintainable code structure
- Comprehensive documentation
- Git repository properly organized
- Ready for team handoff and further development

## 📞 Technical Notes
- Python 3.8+ required
- Main dependencies: Dash, Plotly, XlsxWriter, NumPy, Pandas
- No database required (file-based scenario storage)
- Responsive web interface works on desktop/tablet

---
*Last updated: August 6, 2025*
*Repository: https://github.com/jermhey/Build-Buy-Dash*
