# API-Evolve

Self-optimizing API marketplace CLI tool.

## Overview
API-Evolve is a Python CLI tool that lets independent API creators register their APIs, record usage, automatically adjust prices based on feedback, and enforce simple zero-trust-style access control using locally stored tokens. All data lives in a single SQLite file.

## Tech Stack
- Python 3.11+
- Click (CLI framework)
- SQLite3 (stdlib)

## Features
1. **API Registration & Discovery** - Register APIs with name, description, and price. List all registered APIs.
2. **Usage Tracking & Pricing Adjustment** - Record usage and auto-adjust prices based on demand.
3. **Access Control & Token Management** - Generate and validate bearer tokens for API access.

## Setup
```bash
chmod +x init.sh
./init.sh
```

## Usage
```bash
# Register an API
python -m api_evolve.main register --name "weather" --desc "Provides weather data" --price 0.01

# List APIs
python -m api_evolve.main list

# Record usage
python -m api_evolve.main usage --api weather --units 150

# Check price
python -m api_evolve.main price --api weather

# Generate token
python -m api_evolve.main token --api weather --user alice

# Validate token
python -m api_evolve.main check --token <token>
```
