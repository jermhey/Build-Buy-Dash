# Build vs Buy Decision Dashboard

A modern web app for data-driven build vs buy analysis using Monte Carlo simulation.

## Features
- Monte Carlo simulation engine
- Dynamic risk and cost modeling
- Scenario saving and comparison
- Professional Excel export
- Modern UI (Dash)
- Fully tested and production-ready

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
   App runs at http://127.0.0.1:8060

## Developer Guide
- Parameters: `config/parameters.py`
- Simulation: `src/simulation.py`
- UI: `app.py`, `ui/modern_ui.py`
- Utilities: `src/utils.py`
- Tests: `tests/`

## Testing
```bash
python tests/test_simulation.py
```

## Troubleshooting
- Import errors: Run from `build_buy_app` directory
- Missing packages: `pip install -r requirements.txt`
- Python 3.8+ required

