
# Alt-Propulsion Flight Dynamics Framework v3.0

[![CI](https://github.com/theoriginalawesomepossum/alt-propulsion-flight-dynamics/actions/workflows/ci.yml/badge.svg)](https://github.com/theoriginalawesomepossum/alt-propulsion-flight-dynamics/actions/workflows/ci.yml)

Advanced framework for simulating and analyzing alternative propulsion systems in flight dynamics.

**Engineering-grade flight dynamics simulator for alternative propulsion craft**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/yourusername/alt-propulsion/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/alt-propulsion/actions)

---

## 🚀 Features

- **Physics-based analysis**: TWR, stability, endurance, climb rate, thermal/structural margins
- **18+ propulsion types**: VTOL, hovercraft, jetpack, ion, plasma, anti-gravity, hybrid
- **Hybrid propulsion**: Mix & match multiple propulsion systems
- **Real-world atmosphere**: ISA + humidity + temperature + density altitude [web:1][web:14][web:17]
- **Three-phase testing**: Bench, pre-flight aero, full flight with variance
- **Monte Carlo simulation**: Seeded randomness for reproducibility
- **Auto-detect CLI**: Interactive or batch mode automatically
- **JSON/CSV export**: Test logs for engineering reports
- **Type-safe**: Full Pydantic validation with physical bounds

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/alt-propulsion.git
cd alt-propulsion

# Install dependencies
pip install -r requirements.txt

# Install package (optional)
pip install -e .
