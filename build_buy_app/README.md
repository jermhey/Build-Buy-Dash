# Build vs Buy Decision Dashboard

> A comprehensive financial analysis platform for strategic build vs buy decisions using Monte Carlo simulation and advanced analytics.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/dash-2.18+-green.svg)](https://dash.plotly.com/)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()
[![Deploy](https://img.shields.io/badge/deploy-render%20|%20railway%20|%20heroku-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

The Build vs Buy Decision Dashboard is a **production-ready** web application designed to help organizations make data-driven decisions between building custom solutions in-house versus purchasing existing products. The platform combines Monte Carlo simulation, advanced financial modeling, and professional Excel reporting to provide comprehensive analysis across multiple scenarios.

🚀 **Ready for Production Deployment** - Configured for Render, Railway, and Heroku with zero-downtime deployment capabilities. ✨

### Key Features

- **Monte Carlo Simulation Engine**: Statistical modeling with 1000 simulations for uncertainty analysis
- **Dynamic Risk Modeling**: Configurable technical, vendor, and market risk factors
- **Present Value Calculations**: WACC-based discounting with proper timing considerations
- **Professional Excel Export**: Multi-sheet workbooks with formulas, sensitivity analysis, and reconciliation
- **Scenario Management**: Save, compare, and version control different analysis scenarios
- **Modern Web Interface**: Responsive design with real-time calculations and visualizations
- **Comprehensive Testing**: Full test suite ensuring reliability and accuracy
- **Production Ready**: Deployment-optimized with Gunicorn, environment detection, and cloud platform support
- **Enterprise Security**: CSP policies, input validation, security headers for compliance scanning
- **Flexible Sensitivity Analysis**: Configurable parameter ranges with clean, professional presentation

### 🔐 Enterprise Security Features

**Security Compliance Ready** - Passes enterprise security scanning tools:

- **✅ Dependabot Compatible**: Secure dependency management
- **✅ Veracode Ready**: Input validation, sanitization, secure exception handling
- **✅ GitHub Advanced Security**: CodeQL patterns addressed, no secrets in code

**Security Implementations:**
- **Content Security Policy (CSP)**: Prevents XSS attacks
- **Security Headers**: X-Frame-Options, X-XSS-Protection, Strict-Transport-Security
- **Input Validation**: Bounds checking, parameter sanitization, injection prevention
- **File I/O Security**: UTF-8 encoding, path validation, size limits
- **Exception Handling**: Specific error types, secure logging, graceful degradation

*See `SECURITY.md` for complete security implementation details.*

## Quick Start

### Local Development

#### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jermhey/Build-Buy-Dash.git
   cd Build-Buy-Dash
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd build_buy_app
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   Open your browser and navigate to: `http://127.0.0.1:8060`

## 📋 Complete Replication Guide

### For New Developers - Exact Steps to Deploy

**Prerequisites:**
- GitHub account
- Render.com account (free)
- Git installed locally

**Step 1: Fork or Clone Repository**
```bash
git clone https://github.com/jermhey/Build-Buy-Dash.git
cd Build-Buy-Dash
```

**Step 2: Test Locally (Optional)**
```bash
cd build_buy_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Step 3: Deploy to Production**
1. Push to your GitHub repository
2. Go to [render.com](https://render.com) → Sign up with GitHub
3. Click "New +" → "Web Service"
4. **Configure exactly as shown:**

| Setting | Value |
|---------|-------|
| Repository | `https://github.com/YOUR_USERNAME/Build-Buy-Dash` |
| Branch | `main` |
| **Root Directory** | `build_buy_app` ⚠️ **REQUIRED** |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30` |
| Plan | Free |
| Auto-Deploy | On Commit |

5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment
7. Your app is live! 🎉

**Step 4: Verify Deployment**
- ✅ Dashboard loads with modern UI
- ✅ Monte Carlo simulation runs
- ✅ Excel export downloads
- ✅ Security headers present (check browser dev tools)

### Production Environment Configuration

The application automatically detects production environment and configures:
- **Security Headers**: CSP, X-Frame-Options, XSS Protection
- **Performance**: Optimized for cloud deployment
- **Error Handling**: Production-safe error messages
- **Monitoring**: Built-in health checks and logging

### Production Deployment 🚀

This application is **production-ready** and can be deployed to any cloud platform in minutes:

#### Option 1: Render (Recommended - Free)

**Step-by-Step Render Deployment:**

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy Build vs Buy Dashboard"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com) and sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build & Deploy Settings**
   ```yaml
   Repository: https://github.com/YOUR_USERNAME/Build-Buy-Dash
   Branch: main
   Root Directory: build_buy_app
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30
   Auto-Deploy: On Commit
   ```

4. **Detailed Configuration Values:**
   - **Repository**: Your GitHub repository URL
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `build_buy_app` ⚠️ **CRITICAL** - This must be set!
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30`
   - **Environment**: Python 3.8+
   - **Plan**: Free (sufficient for most use cases)

5. **Click "Create Web Service"** - Your app will be live in 5-10 minutes!

**⚠️ Important Notes:**
- **Root Directory MUST be set to `build_buy_app`** - This is essential for proper deployment
- If deployment fails, manually verify the Start Command in Render dashboard
- The app includes enterprise security features (CSP, input validation, security headers)

#### Option 2: Railway
1. **Push to GitHub**  
2. **Connect to [railway.app](https://railway.app)**
3. **Deploy Configuration:**
   ```yaml
   Source: GitHub Repository
   Root Directory: build_buy_app
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:server --bind 0.0.0.0:$PORT
   ```

#### Option 3: Heroku
1. **Install Heroku CLI and deploy:**
   ```bash
   # Navigate to app directory
   cd build_buy_app
   
   # Initialize Heroku app
   heroku create your-app-name
   
   # Deploy
   git subtree push --prefix=build_buy_app heroku main
   ```

**All deployment files included:** `render.yaml`, `Procfile`, `start.sh`, `requirements.txt` - all optimized for production use.

## Deployment Troubleshooting 🔧

### Common Render Issues & Solutions

**Issue 1: Build Fails - "No module named 'dash'"**
- **Solution**: Ensure Root Directory is set to `build_buy_app`
- **Verify**: Build command should run from `build_buy_app/` directory

**Issue 2: App Crashes on Start**
- **Solution**: Check Start Command is exactly: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30`
- **Note**: Some platforms cache old commands - update manually in dashboard

**Issue 3: "Module not found" errors**
- **Solution**: Verify all Python files use relative imports
- **Check**: `requirements.txt` contains all necessary packages

**Issue 4: Security Headers Not Applied**
- **Status**: ✅ All security improvements are deployment-ready
- **Includes**: CSP policies, XSS protection, input validation
- **Enterprise Ready**: Passes Dependabot, Veracode, GitHub Advanced Security

### Render Configuration Checklist ✅

Before deploying, ensure these exact settings:

```yaml
✅ Repository: https://github.com/YOUR_USERNAME/Build-Buy-Dash
✅ Branch: main  
✅ Root Directory: build_buy_app
✅ Build Command: pip install -r requirements.txt
✅ Start Command: gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30
✅ Environment: Python
✅ Plan: Free
✅ Auto-Deploy: On Commit
```

### Verification Steps

After deployment, verify your app:
1. **App loads**: Dashboard interface appears
2. **Calculations work**: Monte Carlo simulation runs
3. **Excel export**: Download functionality works  
4. **Security headers**: Check browser dev tools for CSP headers
5. **Responsive design**: Works on mobile devices

## Project Structure

```
build_buy_app/                    # 🚨 ROOT DIRECTORY for deployment
├── app.py                        # Main application entry point (production-ready)
├── requirements.txt              # Python dependencies (includes Gunicorn)
├── README.md                     # This file
├── SECURITY.md                   # Enterprise security documentation
├── Procfile                      # Heroku deployment configuration
├── render.yaml                   # Render deployment configuration  
├── start.sh                      # Render startup script
├── config/
│   ├── parameters.py             # Configuration constants and defaults
│   └── security.py               # Security configuration and constants
├── core/
│   ├── advanced_analytics.py    # Advanced analytics and reporting
│   └── excel_export.py          # Excel export functionality (fixed formulas)
├── data/
│   ├── config_manager.py        # Application configuration management
│   └── scenario_manager.py      # Scenario persistence and comparison
├── src/
│   ├── simulation.py            # Core Monte Carlo simulation engine
│   └── utils.py                 # Utility functions with security validation
├── tests/
│   ├── test_simulation.py       # Core simulation tests
│   ├── comprehensive_validation.py # Full validation suite
│   └── [additional test files]   # Comprehensive test coverage
├── ui/
│   └── modern_ui.py             # Modern Bootstrap UI components
└── scenarios/                    # Saved scenario storage directory
```

### 🚨 Critical Deployment Notes

- **Root Directory**: MUST be set to `build_buy_app` in deployment platforms
- **Start Command**: `gunicorn app:server` (NOT `gunicorn app:app.server`)
- **All Files Included**: No additional configuration needed
- **Security Ready**: Enterprise-grade security implementations included
│   ├── excel_export.py   # Excel workbook generation with clean sensitivity analysis
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
│   └── test_simulation.py # Comprehensive test suite
├── scenarios/            # Saved scenario files (created at runtime)
├── assets/
│   └── style.css         # Custom CSS styling
└── deployment/           # Production deployment files
    ├── render.yaml       # Render platform configuration
    ├── Procfile          # Process configuration for Heroku/Railway
    ├── runtime.txt       # Python version specification
    └── DEPLOYMENT.md     # Detailed deployment guide
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
- **Sensitivity Analysis**: Clean parameter impact assessment with configurable ranges
- **Break-Even Analysis**: Decision threshold calculations
- **Reconciliation**: Simulation vs Excel formula comparison
- **Methodology**: Detailed calculation explanations

✨ **Enhanced Sensitivity Analysis**: Features clean parameter labels, flexible range configuration, and professional presentation without redundant information.

## Development Guide

### Architecture Overview

The application follows a modular architecture with clear separation of concerns:

- **Presentation Layer** (`ui/modern_ui.py`): Dash-based web interface
- **Application Layer** (`app.py`): Request handling and workflow orchestration  
- **Business Logic** (`src/simulation.py`, `core/`): Core calculations and analysis
- **Data Layer** (`data/`): Persistence and configuration management

### Production Features

#### Environment Detection
- Automatically detects production vs development environment
- Uses appropriate host/port configuration for deployment
- Enables/disables debug mode based on environment

#### Performance Optimization
- Gunicorn WSGI server for production
- Optimized asset loading and caching
- Efficient Excel generation with proper memory management

#### Error Handling
- Comprehensive input validation
- Graceful error recovery
- Production-safe error logging

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
- **Clean sensitivity analysis** with configurable parameter ranges
- Professional presentation without redundant information

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

### Testing

#### Running Tests

```bash
# Run all tests
cd build_buy_app
python tests/test_simulation.py

# Run specific test
python -m pytest tests/test_simulation.py::test_basic_simulation -v

# Test production readiness
python tests/test_simulation.py
# Expected output: "🎉 ALL TESTS PASSED! Your app is ready for production."
```

#### Test Coverage
- ✅ Simulation engine validation
- ✅ Parameter validation and edge cases  
- ✅ App integration and startup
- ✅ Scenario management features
- ✅ Excel export functionality
- ✅ Production configuration

## Deployment Status

🟢 **Production Ready**: All tests passing, deployment files configured, performance optimized

**Supported Platforms:**
- ✅ Render (Free tier available)
- ✅ Railway (Auto-deployment from GitHub)  
- ✅ Heroku (Professional hosting)
- ✅ Docker (Containerization ready)
- ✅ AWS/GCP/Azure (Cloud platform compatible)

**Features Verified:**
- ✅ Monte Carlo simulation accuracy
- ✅ Excel export with clean sensitivity analysis  
- ✅ Professional UI/UX
- ✅ Scenario management
- ✅ Production server configuration
- ✅ Environment-aware deployment

See `DEPLOYMENT.md` for detailed deployment instructions and platform-specific guides.

## Recent Enhancements

### Sensitivity Analysis Improvements ✨
- **Clean Parameter Labels**: Removed redundant value ranges from parameter names
- **Flexible Range Configuration**: Easy-to-modify `SENSITIVITY_RANGES` dictionary
- **Dynamic Value Calculation**: Ranges adapt automatically to user inputs
- **Professional Presentation**: Excel export now shows clean, meaningful parameter names

### Production Readiness 🚀
- **Environment Detection**: Automatic production vs development configuration
- **Gunicorn Integration**: Professional WSGI server for production deployment
- **Cloud Platform Support**: Pre-configured for Render, Railway, and Heroku
- **Zero-Configuration Deployment**: Just push to GitHub and deploy

### Quality Assurance ✅
- **Comprehensive Testing**: Full test suite covering all functionality
- **Error-Resistant Design**: Robust input validation and error handling
- **Performance Optimized**: Efficient Excel generation and asset loading
- **Documentation Complete**: Detailed deployment and usage guides

---

**Ready to Deploy?** This application is production-ready and can be deployed to the web in under 10 minutes. All configuration files are included, tests are passing, and the application has been optimized for cloud deployment.

🎯 **Recommendation**: Deploy to [Render](https://render.com) for free hosting with automatic deployments from GitHub.

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

