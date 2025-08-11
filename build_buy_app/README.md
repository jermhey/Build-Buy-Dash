# Build vs Buy Decision Dashboard

> A comprehensive financial analysis platform for strategic build vs buy decisions using Monte Carlo simulation and advanced analytics.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/dash-2.0+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

The Build vs Buy Decision Dashboard is a sophisticated web application designed to help organizations make data-driven decisions between building custom solutions in-house versus purchasing existing products. The platform combines Monte Carlo simulation, advanced financial modeling, and professional Excel reporting to provide comprehensive analysis across multiple scenarios.

### Key Features

- **Monte Carlo Simulation Engine**: Statistical modeling with 1000 simulations for uncertainty analysis
- **Dynamic Risk Modeling**: Configurable technical, vendor, and market risk factors
- **Present Value Calculations**: WACC-based discounting with proper timing considerations
- **Professional Excel Export**: Multi-sheet workbooks with formulas, sensitivity analysis, and reconciliation
- **Scenario Management**: Save, compare, and version control different analysis scenarios
- **Modern Web Interface**: Responsive design with real-time calculations and visualizations
- **Comprehensive Testing**: Full test suite ensuring reliability and accuracy

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jermhey/Build-Buy-Dash.git
   cd Build-Buy-Dash/build_buy_app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   Open your browser and navigate to: `http://127.0.0.1:8060`

## Project Structure

```
build_buy_app/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config/
│   └── parameters.py     # Configuration constants and defaults
├── core/
│   ├── excel_export.py   # Excel workbook generation engine
│   └── advanced_analytics.py  # Advanced statistical analysis
├── data/
│   ├── config_manager.py # Application configuration management
│   └── scenario_manager.py # Scenario persistence and comparison
├── src/
│   ├── simulation.py     # Monte Carlo simulation engine
│   └── utils.py          # Utility functions
├── ui/
│   └── modern_ui.py      # Dashboard UI components
├── tests/
│   └── test_simulation.py # Test suite
├── scenarios/            # Saved scenario files (created at runtime)
└── assets/
    └── style.css         # Custom CSS styling
```

## Usage Guide

### Basic Workflow

1. **Set Build Parameters**: Configure timeline, team size, costs, and success probability
2. **Configure Buy Options**: Set purchase prices and subscription costs
3. **Apply Risk Factors**: Add technical, vendor, and market risk percentages
4. **Run Analysis**: Click "Calculate" to generate Monte Carlo simulation results
5. **Export to Excel**: Download comprehensive analysis workbook
6. **Save Scenarios**: Store parameter sets for future comparison

### Key Input Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| Build Timeline | Development duration in months | 6-36 months |
| FTE Cost | Annual fully-loaded employee cost | $100K-$200K |
| Team Size | Number of full-time developers | 2-10 FTEs |
| Success Probability | Likelihood of successful delivery | 60%-95% |
| WACC | Weighted Average Cost of Capital | 5%-15% |
| Risk Factors | Additional cost risk percentages | 0%-50% each |

### Excel Export Features

The generated Excel workbook includes:

- **Input Parameters**: Editable parameter values with descriptions
- **Cost Timeline**: Year-by-year cost breakdown with PV calculations
- **Executive Summary**: High-level results and recommendations
- **Dashboard**: Visual charts and key metrics
- **Sensitivity Analysis**: Parameter impact assessment
- **Break-Even Analysis**: Decision threshold calculations
- **Reconciliation**: Simulation vs Excel formula comparison
- **Methodology**: Detailed calculation explanations

## Development Guide

### Architecture Overview

The application follows a modular architecture with clear separation of concerns:

- **Presentation Layer** (`ui/modern_ui.py`): Dash-based web interface
- **Application Layer** (`app.py`): Request handling and workflow orchestration
- **Business Logic** (`src/simulation.py`, `core/`): Core calculations and analysis
- **Data Layer** (`data/`): Persistence and configuration management

### Key Components

#### Simulation Engine (`src/simulation.py`)
- Monte Carlo methodology with configurable iterations
- Year-by-year PV discounting for accurate timing
- Risk factor application (additive model with stochastic variation)
- Probability of success adjustments

#### Excel Export Engine (`core/excel_export.py`)
- Dynamic formula generation with proper cell referencing
- Multi-sheet workbook creation with professional formatting
- Cross-sheet formula linking for live updates
- Error-resistant formula construction

#### UI Framework (`ui/modern_ui.py`)
- Modern Bootstrap-based design
- Real-time parameter validation
- Interactive charts and visualizations
- Responsive layout for different screen sizes

### Adding New Features

#### Adding a New Parameter

1. **Update Configuration** (`config/parameters.py`)
   ```python
   CORE_PARAMETERS = {
       "new_parameter": default_value,
       # ... existing parameters
   }
   ```

2. **Update Simulation Logic** (`src/simulation.py`)
   ```python
   def _extract_core_parameters(self, params):
       return {
           'new_parameter': float(params.get('new_parameter', default)),
           # ... existing extractions
       }
   ```

3. **Update UI** (`ui/modern_ui.py`)
   ```python
   # Add input component in appropriate method
   dbc.Input(id='new_parameter', type='number', value=default)
   ```

4. **Update Excel Export** (`core/excel_export.py`)
   ```python
   # Add to input_params list in _create_input_parameters_sheet
   ('new_parameter', 'Parameter Label', 'format_type', 'Description'),
   ```

#### Adding a New Analysis Sheet

1. Create new method in `ExcelExporter` class
2. Add sheet creation call in `create_excel_export` method
3. Implement sheet-specific logic with proper cell referencing
4. Add to sheet navigation in dashboard

### Testing

#### Running Tests

```bash
# Run all tests
python tests/test_simulation.py

# Run specific test
python -m pytest tests/test_simulation.py::test_basic_simulation -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

#### Test Coverage Areas

- **Simulation Engine**: Parameter validation, calculation accuracy
- **Excel Export**: Formula generation, cell referencing
- **UI Components**: Input validation, state management
- **Integration**: End-to-end workflow testing

### Code Style and Standards

- **PEP 8**: Python style guide compliance
- **Type Hints**: Function signatures include type annotations
- **Docstrings**: All public methods documented with Google style
- **Error Handling**: Graceful failure with user-friendly messages
- **Logging**: Structured logging for debugging and monitoring

## Deployment

### Production Deployment

For production deployment, consider:

1. **Environment Variables**: Store sensitive configuration externally
2. **Reverse Proxy**: Use nginx or similar for SSL termination
3. **Process Management**: Use gunicorn or similar WSGI server
4. **Monitoring**: Implement health checks and error tracking
5. **Scaling**: Consider containerization with Docker

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8060

CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in the correct directory
cd build_buy_app
python app.py
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### Excel Export Errors
- Verify xlsxwriter is installed: `pip show xlsxwriter`
- Check disk space for temporary file creation
- Ensure proper file permissions in working directory

#### Performance Issues
- Reduce simulation iterations for faster testing (modify `n_simulations` parameter)
- Check available memory for large Monte Carlo runs
- Profile with `cProfile` if needed

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python app.py
```

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run test suite: `python tests/test_simulation.py`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Create Pull Request

### Guidelines

- Write tests for new functionality
- Update documentation for API changes
- Follow existing code style and patterns
- Include docstrings for public methods

## Documentation

- [Contributing Guidelines](CONTRIBUTING.md) - Development setup and coding standards
- [API Documentation](docs/API.md) - Detailed API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

### Additional Resources

- **Project Structure**: See [Project Structure](#project-structure) section above
- **Testing**: Run `python -m pytest tests/` for comprehensive test suite
- **Excel Export**: Generated workbooks include multiple analysis sheets with live formulas
- **Monte Carlo Simulation**: 1000 iterations with statistical distribution analysis
- **Risk Modeling**: Incorporates technical, vendor, and market risk factors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions:

1. **Issues**: Create a GitHub issue with detailed description
2. **Documentation**: Check this README and inline code documentation
3. **Testing**: Run the test suite to verify functionality

## Changelog

### Version 1.0.0
- Initial release with Monte Carlo simulation
- Excel export functionality
- Modern web interface
- Scenario management system

