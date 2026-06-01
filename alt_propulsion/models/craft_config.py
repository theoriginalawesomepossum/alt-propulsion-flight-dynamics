"""
Craft configuration data model with validation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from alt_propulsion.models.enums import PropulsionType, TestPhase


@dataclass
class CraftConfig:
    """
    Physical configuration of an alt-propulsion craft.
    
    All fields are validated on initialization via __post_init__.
    Use ConfigValidator for detailed validation errors.
    """
    
    # ========== PHYSICAL PARAMETERS ==========
    mass_kg: float = 1000.0
    thrust_newtons: float = 12000.0
    num_thrusters: int = 4
    thrust_symmetry: float = 1.0  # 1.0 = perfect, 0.0 = completely asymmetric
    
    # Center of Mass/Thrust geometry
    center_of_mass_height_m: float = 0.5
    center_of_thrust_height_m: float = 0.3
    center_of_mass_lateral_m: float = 0.0  # X-offset from geometric center
    center_of_thrust_lateral_m: float = 0.0  # X-offset from geometric center
    
    # Aerodynamic properties
    base_area_m2: float = 10.0
    drag_coefficient: float = 0.8
    lift_coefficient_max: float = 1.5  # For winged VTOL
    
    # ========== POWER SYSTEM ==========
    max_power_kw: float = 500.0
    battery_capacity_kwh: float = 50.0
    battery_voltage: float = 400.0
    max_discharge_rate_c: float = 5.0  # C-rate
    
    # Propulsion type
    propulsion_type: PropulsionType = PropulsionType.VTOL
    
    # Hybrid propulsion (optional)
    hybrid_modules: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [{"type": "VTOL", "weight": 0.7}, {"type": "ION_THRUSTER", "weight": 0.3}]
    
    # ========== ENVIRONMENTAL ==========
    altitude_m: float = 0.0
    temperature_c: float = 15.0  # Outside air temperature
    dew_point_c: Optional[float] = None  # For humidity calculation
    relative_humidity: Optional[float] = None  # Alternative to dew point
    
    # Wind conditions
    wind_speed_ms: float = 0.0
    wind_direction_deg: float = 0.0  # 0 = North, 90 = East
    wind_gust_intensity: float = 0.0  # 0-1, additional turbulence
    turbulence_level: float = 0.0  # 0-1, atmospheric turbulence
    
    # ========== CONTROL ==========
    pid_stability_rating: float = 0.8  # 0-1, autopilot quality
    pilot_skill: float = 0.7  # 0-1, human factor
    control_latency_ms: float = 10.0  # Control system latency
    
    # ========== HARDWARE STATE (Real-World Variance) ==========
    hull_temperature_c: float = 20.0
    motor_temperature_c: float = 25.0
    battery_temperature_c: float = 25.0
    battery_state_of_health: float = 1.0  # 1.0 = new, 0.8 = 80%
    
    # Manufacturing tolerances
    thruster_variation: float = 0.02  # ±2% thrust variation
    weight_distribution_error: float = 0.01  # ±1% COM offset
    propeller_efficiency_degradation: float = 1.0  # 1.0 = new
    
    # ========== ADVANCED ==========
    geomagnetic_interference: float = 0.0  # 0-1, affects compass/PID
    solar_radiation_intensity: float = 1.0  # For ion/plasma propulsion
    precipitation: float = 0.0  # 0-1, rain/snow affecting drag
    
    # Test phase (for simulation)
    test_phase: TestPhase = TestPhase.BENCH
    
    # Random seed for reproducibility
    seed: Optional[int] = None
    
    def __post_init__(self):
        """Validate all fields after initialization."""
        from alt_propulsion.core.validation import ConfigValidator
        
        validator = ConfigValidator()
        errors = validator.validate_craft_config(self)
        
        if errors:
            error_msg = "
".join(errors)
            raise ValueError(f"Invalid CraftConfig:
{error_msg}")
    
    @property
    def twr(self) -> float:
        """Calculate Thrust-to-Weight Ratio."""
        from alt_propulsion.core.physics import PhysicsEngine
        return PhysicsEngine.calculate_twr_static(self)
    
    @property
    def density_altitude(self) -> float:
        """Calculate density altitude."""
        from alt_propulsion.core.atmosphere import AtmosphereModel
        atm = AtmosphereModel()
        pressure_alt = atm.pressure_altitude(self.altitude_m)
        return atm.density_altitude(pressure_alt, self.temperature_c, self.dew_point_c)
    
    def with_variance(self, multiplier: float = 1.0) -> "CraftConfig":
        """
        Create a copy with random variance applied (seeded for reproducibility).
        
        Args:
            multiplier: Variance multiplier (0.1 = bench, 0.5 = pre-flight, 1.0 = full flight)
        
        Returns:
            New CraftConfig with applied variance
        """
        import copy
        import random
        
        result = copy.deepcopy(self)
        
        # Use seed for reproducibility
        rng = random.Random(self.seed if self.seed else 42)
        
        # Apply thruster variation
        thruster_var = self.thruster_variation * multiplier
        result.thrust_newtons *= (1.0 + rng.gauss(0, thruster_var))
        
        # Apply COM offset error
        com_error = self.weight_distribution_error * multiplier
        result.center_of_mass_lateral_m += rng.gauss(0, com_error)
        
        # Apply thrust symmetry degradation
        symmetry_var = 0.05 * multiplier
        result.thrust_symmetry = max(0.0, min(1.0, 
            self.thrust_symmetry + rng.gauss(0, symmetry_var)))
        
        # Apply propeller degradation
        result.propeller_efficiency_degradation = max(0.5, 
            self.propeller_efficiency_degradation * (1.0 + rng.gauss(0, 0.02 * multiplier)))
        
        # Apply battery SOH variance
        soh_var = 0.05 * multiplier
        result.battery_state_of_health = max(0.5, min(1.0,
            self.battery_state_of_health * (1.0 + rng.gauss(0, soh_var))))
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        import dataclasses
        return dataclasses.asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CraftConfig":
        """Create from dictionary."""
        # Handle enum conversion
        if "propulsion_type" in data and isinstance(data["propulsion_type"], str):
            data["propulsion_type"] = PropulsionType(data["propulsion_type"])
        if "test_phase" in data and isinstance(data["test_phase"], str):
            data["test_phase"] = TestPhase[data["test_phase"]]
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"CraftConfig(mass={self.mass_kg}kg, thrust={self.thrust_newtons}N, "
            f"twr={self.twr:.3f}, type={self.propulsion_type.name})"
        )
    
    def __repr__(self) -> str:
        """Repr representation."""
        return self.__str__()
