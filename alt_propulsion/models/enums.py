"""
Enumeration types for the Alt-Propulsion Framework.
"""

from enum import Enum, auto
from typing import List


class FlightOutcome(Enum):
    """Possible flight dynamics outcomes."""
    
    HOVER = auto()           # Stable hover (TWR ~ 1.0, stability > 0.5)
    FLY = auto()             # Sustained flight (TWR > 1.15, stable)
    CRASH = auto()           # Immediate crash (TWR < 1.0 or stability < 0.2)
    UNSTABLE_HOVER = auto()  # Hover but unstable (will drift/crash eventually)
    STALL = auto()           # Aerodynamic stall (for winged VTOL)
    INSUFFICIENT_POWER = auto()  # Power depleted before achieving lift
    GROUND_EFFECT = auto()   # Stable in ground effect only (hovercraft)
    SPACE_FLIGHT = auto()    # Escape atmosphere (ion/anti-gravity)
    
    @property
    def is_success(self) -> bool:
        """Return True if outcome represents successful flight."""
        return self in [self.HOVER, self.FLY, self.GROUND_EFFECT, self.SPACE_FLIGHT]
    
    @property
    def is_failure(self) -> bool:
        """Return True if outcome represents failure."""
        return self in [self.CRASH, self.STALL, self.UNSTABLE_HOVER, self.INSUFFICIENT_POWER]
    
    @property
    def emoji(self) -> str:
        """Return emoji representation."""
        mapping = {
            self.HOVER: "🛸",
            self.FLY: "✈️",
            self.CRASH: "💥",
            self.UNSTABLE_HOVER: "⚠️",
            self.STALL: "🔄",
            self.INSUFFICIENT_POWER: "🔋",
            self.GROUND_EFFECT: "🌊",
            self.SPACE_FLIGHT: "🚀",
        }
        return mapping.get(self, "❓")
    
    @classmethod
    def all_outcomes(cls) -> List["FlightOutcome"]:
        """Return list of all possible outcomes."""
        return list(cls)


class PropulsionType(Enum):
    """Supported propulsion system types."""
    
    # VTOL Family
    VTOL = "VTOL (Tilt-Rotor/Thrust Vectoring)"
    VTOL_MULTICOPTER = "VTOL Multicopter"
    VTOL_TILT_ROTOR = "VTOL Tilt-Rotor"
    VTOL_TILT_WING = "VTOL Tilt-Wing"
    
    # Aerodynamic Lift
    HOVERCRAFT = "Hovercraft (Air Cushion)"
    GROUND_EFFECT = "Ground-Effect Craft (WIG)"
    WINGED_VTOL = "Winged VTOL (eVTOL)"
    
    # Jet/Rocket
    JETPACK = "Jetpack (Rocket/Jet)"
    TURBOJET = "Turbojet"
    TURBOFAN = "Turbofan"
    RAMJET = "Ramjet"
    SCRAMJET = "Scramjet"
    
    # Ducted Systems
    DUCTED_FAN = "Ducted Fan"
    SHROUDED_FAN = "Shrouded Fan"
    PULSE_JET = "Pulse Jet"
    
    # Electric/Ion
    ION_THRUSTER = "Ion Thruster"
    HALL_THRUSTER = "Hall Thruster"
    ELECTROSPRAY = "Electrospray Thruster"
    
    # Experimental
    PLASMA_THRUSTER = "Plasma Thruster (MPD/VASIMR)"
    MPD_THRUSTER = "MPD Thruster"
    VASIMR = "VASIMR"
    
    # Speculative
    ANTI_GRAVITY = "Anti-Gravity (Speculative)"
    
    # Hybrid
    HYBRID = "Hybrid (Multi-System)"
    
    @property
    def category(self) -> str:
        """Return propulsion category."""
        categories = {
            self.VTOL: "VTOL",
            self.VTOL_MULTICOPTER: "VTOL",
            self.VTOL_TILT_ROTOR: "VTOL",
            self.VTOL_TILT_WING: "VTOL",
            self.HOVERCRAFT: "Aerodynamic",
            self.GROUND_EFFECT: "Aerodynamic",
            self.WINGED_VTOL: "Aerodynamic",
            self.JETPACK: "Jet/Rocket",
            self.TURBOJET: "Jet/Rocket",
            self.TURBOFAN: "Jet/Rocket",
            self.RAMJET: "Jet/Rocket",
            self.SCRAMJET: "Jet/Rocket",
            self.DUCTED_FAN: "Ducted",
            self.SHROUDED_FAN: "Ducted",
            self.PULSE_JET: "Ducted",
            self.ION_THRUSTER: "Electric",
            self.HALL_THRUSTER: "Electric",
            self.ELECTROSPRAY: "Electric",
            self.PLASMA_THRUSTER: "Experimental",
            self.MPD_THRUSTER: "Experimental",
            self.VASIMR: "Experimental",
            self.ANTI_GRAVITY: "Speculative",
            self.HYBRID: "Hybrid",
        }
        return categories.get(self, "Unknown")
    
    @property
    def is_speculative(self) -> bool:
        """Return True if propulsion type is speculative/experimental."""
        return self in [self.ANTI_GRAVITY, self.PLASMA_THRUSTER, self.MPD_THRUSTER, self.VASIMR]
    
    @property
    def is_electric(self) -> bool:
        """Return True if propulsion is electric-based."""
        return self in [self.ION_THRUSTER, self.HALL_THRUSTER, self.ELECTROSPRAY, 
                        self.PLASMA_THRUSTER, self.MPD_THRUSTER, self.VASIMR]
    
    @property
    def is_airbreathing(self) -> bool:
        """Return True if propulsion requires atmospheric air."""
        airbreathing = [
            self.VTOL, self.VTOL_MULTICOPTER, self.VTOL_TILT_ROTOR, self.VTOL_TILT_WING,
            self.HOVERCRAFT, self.GROUND_EFFECT, self.WINGED_VTOL,
            self.TURBOJET, self.TURBOFAN, self.RAMJET, self.SCRAMJET,
            self.DUCTED_FAN, self.SHROUDED_FAN, self.PULSE_JET,
        ]
        return self in airbreathing
    
    @property
    def stability_modifier(self) -> float:
        """Return inherent stability modifier (0-1)."""
        modifiers = {
            self.VTOL: 0.9,
            self.VTOL_MULTICOPTER: 0.92,
            self.VTOL_TILT_ROTOR: 0.88,
            self.VTOL_TILT_WING: 0.87,
            self.HOVERCRAFT: 0.7,
            self.GROUND_EFFECT: 0.75,
            self.WINGED_VTOL: 0.85,
            self.JETPACK: 0.5,
            self.TURBOJET: 0.8,
            self.TURBOFAN: 0.82,
            self.RAMJET: 0.75,
            self.SCRAMJET: 0.7,
            self.DUCTED_FAN: 0.85,
            self.SHROUDED_FAN: 0.87,
            self.PULSE_JET: 0.65,
            self.ION_THRUSTER: 0.95,
            self.HALL_THRUSTER: 0.94,
            self.ELECTROSPRAY: 0.93,
            self.PLASMA_THRUSTER: 0.9,
            self.MPD_THRUSTER: 0.88,
            self.VASIMR: 0.91,
            self.ANTI_GRAVITY: 1.0,
            self.HYBRID: 0.8,
        }
        return modifiers.get(self, 0.8)
    
    @property
    def efficiency_modifier(self) -> float:
        """Return efficiency modifier for hover (0-1)."""
        modifiers = {
            self.VTOL: 0.75,
            self.VTOL_MULTICOPTER: 0.78,
            self.VTOL_TILT_ROTOR: 0.72,
            self.VTOL_TILT_WING: 0.7,
            self.HOVERCRAFT: 0.9,
            self.GROUND_EFFECT: 0.92,
            self.WINGED_VTOL: 0.8,
            self.JETPACK: 0.4,
            self.TURBOJET: 0.55,
            self.TURBOFAN: 0.65,
            self.RAMJET: 0.6,
            self.SCRAMJET: 0.58,
            self.DUCTED_FAN: 0.8,
            self.SHROUDED_FAN: 0.82,
            self.PULSE_JET: 0.5,
            self.ION_THRUSTER: 0.95,
            self.HALL_THRUSTER: 0.94,
            self.ELECTROSPRAY: 0.93,
            self.PLASMA_THRUSTER: 0.88,
            self.MPD_THRUSTER: 0.85,
            self.VASIMR: 0.9,
            self.ANTI_GRAVITY: 1.0,
            self.HYBRID: 0.75,
        }
        return modifiers.get(self, 0.7)
    
    @classmethod
    def all_types(cls) -> List["PropulsionType"]:
        """Return list of all propulsion types."""
        return list(cls)
    
    @classmethod
    def by_category(cls, category: str) -> List["PropulsionType"]:
        """Return all propulsion types in a category."""
        return [pt for pt in cls if pt.category == category]


class TestPhase(Enum):
    """Test phase for simulation."""
    
    BENCH = auto()            # Lab conditions, minimal variance
    PRE_FLIGHT_AERO = auto()  # Ground effect, low altitude
    FULL_FLIGHT = auto()      # Real-world conditions, full variance
    
    @property
    def variance_multiplier(self) -> float:
        """Return variance multiplier for this phase."""
        mults = {
            self.BENCH: 0.1,
            self.PRE_FLIGHT_AERO: 0.5,
            self.FULL_FLIGHT: 1.0,
        }
        return mults.get(self, 1.0)
    
    @property
    def description(self) -> str:
        """Return phase description."""
        descs = {
            self.BENCH: "Bench Testing (Lab Conditions)",
            self.PRE_FLIGHT_AERO: "Pre-Flight Aero (Ground Effect)",
            self.FULL_FLIGHT: "Full Flight (Real-World)",
        }
        return descs.get(self, "Unknown")
    
    @classmethod
    def all_phases(cls) -> List["TestPhase"]:
        """Return list of all test phases."""
        return list(cls)
