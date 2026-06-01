"""
Flight analysis results data model.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from alt_propulsion.models.enums import FlightOutcome, PropulsionType, TestPhase


@dataclass
class FlightAnalysis:
    """
    Complete flight dynamics analysis results.
    
    Contains all calculated metrics, warnings, and recommendations
    from a flight dynamics simulation.
    """
    
    # ========== CORE METRICS ==========
    outcome: FlightOutcome
    twr: float  # Thrust-to-Weight Ratio
    stability_score: float  # 0-1, overall stability
    hover_efficiency: float  # 0-1, hover efficiency
    max_altitude_m: float  # Maximum achievable altitude
    endurance_seconds: float  # Flight endurance
    
    # ========== ADVANCED METRICS ==========
    climb_rate_ms: float = 0.0  # Maximum climb rate
    descent_rate_ms: float = 0.0  # Maximum descent rate
    hover_power_kw: float = 0.0  # Power required to hover
    thermal_margin: float = 0.0  # 0-1, thermal headroom
    structural_margin: float = 0.0  # 0-1, structural headroom
    control_margin: float = 0.0  # 0-1, control authority headroom
    
    # ========== ATMOSPHERIC ==========
    air_density_kg_m3: float = 1.225  # At operating altitude
    density_altitude_m: float = 0.0  # Pressure altitude corrected for temp/humidity
    mach_number: float = 0.0  # At max speed
    Reynolds_number: float = 0.0  # Flow regime indicator
    
    # ========== HARDWARE ==========
    motor_temperature_c: float = 25.0  # Estimated operating temp
    battery_draw_a: float = 0.0  # Current draw
    battery_voltage_under_load: float = 0.0  # Voltage under load
    
    # ========== TEST PHASE ==========
    test_phase: TestPhase = TestPhase.BENCH
    variance_applied: bool = False
    
    # ========== WARNINGS & RECOMMENDATIONS ==========
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # ========== METADATA ==========
    seed: Optional[int] = None  # Random seed used
    propulsion_type: Optional[PropulsionType] = None
    mass_kg: Optional[float] = None
    thrust_newtons: Optional[float] = None
    
    # ========== ADVANCED ==========
    propulsion_details: Dict[str, Any] = field(default_factory=dict)
    monte_carlo_stats: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure warnings and recommendations are lists."""
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []
        if self.propulsion_details is None:
            self.propulsion_details = {}
    
    @property
    def is_success(self) -> bool:
        """Return True if flight outcome is successful."""
        return self.outcome.is_success
    
    @property
    def is_failure(self) -> bool:
        """Return True if flight outcome is a failure."""
        return self.outcome.is_failure
    
    @property
    def outcome_emoji(self) -> str:
        """Return emoji for outcome."""
        return self.outcome.emoji
    
    @property
    def endurance_formatted(self) -> str:
        """Format endurance as human-readable string."""
        import math
        
        if math.isinf(self.endurance_seconds):
            return "UNLIMITED"
        
        hours = int(self.endurance_seconds // 3600)
        minutes = int((self.endurance_seconds % 3600) // 60)
        seconds = self.endurance_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds:.1f}s"
        else:
            return f"{minutes}m {seconds:.1f}s"
    
    @property
    def max_altitude_formatted(self) -> str:
        """Format max altitude as human-readable string."""
        import math
        
        if math.isinf(self.max_altitude_m):
            return "UNLIMITED"
        elif self.max_altitude_m >= 1000:
            return f"{self.max_altitude_m:,.0f} m ({self.max_altitude_m/3.281:,.0f} ft)"
        else:
            return f"{self.max_altitude_m:.1f} m"
    
    @property
    def risk_level(self) -> str:
        """Return risk level assessment."""
        if self.outcome == FlightOutcome.CRASH:
            return "CRITICAL"
        elif self.outcome == FlightOutcome.UNSTABLE_HOVER:
            return "HIGH"
        elif self.stability_score < 0.5:
            return "MEDIUM"
        elif self.outcome.is_success:
            return "LOW"
        else:
            return "MEDIUM"
    
    @property
    def confidence_interval_90(self) -> Optional[Dict[str, tuple]]:
        """Return 90% confidence interval if Monte Carlo stats available."""
        if not self.monte_carlo_stats:
            return None
        
        stats = self.monte_carlo_stats
        return {
            "stability": (stats["stability"]["p5"], stats["stability"]["p95"]),
            "endurance": (stats["endurance"]["p5"], stats["endurance"]["p95"]),
        }
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        if warning not in self.warnings:
            self.warnings.append(warning)
    
    def add_recommendation(self, recommendation: str):
        """Add a recommendation message."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        import dataclasses
        import math
        
        result = dataclasses.asdict(self)
        
        # Handle inf values
        if math.isinf(result["max_altitude_m"]):
            result["max_altitude_m"] = "INFINITY"
        if math.isinf(result["endurance_seconds"]):
            result["endurance_seconds"] = "INFINITY"
        
        # Convert enums to strings
        result["outcome"] = self.outcome.name
        result["test_phase"] = self.test_phase.name
        if self.propulsion_type:
            result["propulsion_type"] = self.propulsion_type.name
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlightAnalysis":
        """Create from dictionary."""
        # Handle enum conversion
        if "outcome" in data and isinstance(data["outcome"], str):
            data["outcome"] = FlightOutcome[data["outcome"]]
        if "test_phase" in data and isinstance(data["test_phase"], str):
            data["test_phase"] = TestPhase[data["test_phase"]]
        if "propulsion_type" in data and isinstance(data["propulsion_type"], str):
            data["propulsion_type"] = PropulsionType[data["propulsion_type"]]
        
        # Handle infinity
        if data.get("max_altitude_m") == "INFINITY":
            import math
            data["max_altitude_m"] = float('inf')
        if data.get("endurance_seconds") == "INFINITY":
            import math
            data["endurance_seconds"] = float('inf')
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"FlightAnalysis(outcome={self.outcome_emoji} {self.outcome.name}, "
            f"twr={self.twr:.3f}, stability={self.stability_score:.1%}, "
            f"endurance={self.endurance_formatted})"
        )
    
    def __repr__(self) -> str:
        """Repr representation."""
        return self.__str__()
