"""
Alt-Propulsion Flight Dynamics Framework v3.0.0
===============================================
Engineering-grade flight dynamics simulator for alternative propulsion craft.

Supported Propulsion Types:
- VTOL (Tilt-Rotor, Thrust Vectoring, Multicopter)
- Hovercraft (Air Cushion, Ground Effect)
- Jetpack (Rocket, Jet)
- Ducted Fan (Shrouded Fan, Pulse Jet)
- Ion Thruster (Hall Thruster, Electrospray)
- Plasma Thruster (MPD, VASIMR - Experimental)
- Anti-Gravity (Speculative Placeholder)
- Hybrid (Mix & Match Multiple Propulsion Types)

Features:
- Physics-based thrust-to-weight ratio (TWR) calculation
- Stability analysis with COM/COT alignment
- Atmospheric modeling (ISA + humidity + temperature)
- Power/endurance calculation with battery degradation
- Monte Carlo simulation with seeded randomness
- Three-phase testing (Bench, Pre-Flight Aero, Full Flight)
- Interactive/non-automatic CLI with auto-detection
- JSON/CSV/PDF export for test logs

Author: Alt-Propulsion Engineering Team
License: MIT
"""

__version__ = "3.0.0"
__author__ = "Alt-Propulsion Engineering Team"
__email__ = "alt-propulsion@example.com"
__license__ = "MIT"

from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.flight_analysis import FlightAnalysis, FlightOutcome
from alt_propulsion.models.enums import PropulsionType, TestPhase
from alt_propulsion.core.physics import PhysicsEngine
from alt_propulsion.core.atmosphere import AtmosphereModel
from alt_propulsion.core.validation import ConfigValidator
from alt_propulsion.propulsion.base import PropulsionModule
from alt_propulsion.propulsion.hybrid import HybridPropulsion
from alt_propulsion.core.modes import ModeDetector

__all__ = [
    "CraftConfig",
    "FlightAnalysis",
    "FlightOutcome",
    "PropulsionType",
    "TestPhase",
    "PhysicsEngine",
    "AtmosphereModel",
    "ConfigValidator",
    "PropulsionModule",
    "HybridPropulsion",
    "ModeDetector",
]
