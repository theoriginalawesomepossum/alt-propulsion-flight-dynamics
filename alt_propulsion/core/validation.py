"""
Input validation and physical bounds checking.
"""

from typing import Dict, Tuple, List, Any
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.enums import PropulsionType


class ConfigValidator:
    """
    Validates CraftConfig parameters against physical bounds.
    
    Ensures all inputs are within scientifically reasonable ranges
    before running physics calculations.
    """
    
    # ========== PHYSICAL BOUNDS ==========
    PHYSICAL_BOUNDS: Dict[str, Tuple[float, float]] = {
        # Physical parameters
        "mass_kg": (0.1, 1_000_000.0),  # 100g to 1000 tons
        "thrust_newtons": (0.1, 10_000_000.0),  # 0.1N to 10 MN
        "num_thrusters": (1, 100),  # 1 to 100 thrusters
        "thrust_symmetry": (0.0, 1.0),  # 0-1
        
        # Geometry
        "center_of_mass_height_m": (0.0, 100.0),  # 0 to 100m
        "center_of_thrust_height_m": (0.0, 100.0),  # 0 to 100m
        "center_of_mass_lateral_m": (-50.0, 50.0),  # -50 to 50m
        "center_of_thrust_lateral_m": (-50.0, 50.0),  # -50 to 50m
        "base_area_m2": (0.01, 10000.0),  # 100cm² to 10,000m²
        "drag_coefficient": (0.0, 5.0),  # 0 to 5
        "lift_coefficient_max": (0.0, 5.0),  # 0 to 5
        
        # Power
        "max_power_kw": (0.0, 100_000.0),  # 0 to 100 MW
        "battery_capacity_kwh": (0.0, 10_000.0),  # 0 to 10 MWh
        "battery_voltage": (1.0, 1500.0),  # 1V to 1500V
        "max_discharge_rate_c": (0.1, 50.0),  # 0.1C to 50C
        
        # Environmental
        "altitude_m": (0.0, 100_000.0),  # 0 to 100 km
        "temperature_c": (-100.0, 100.0),  # -100°C to 100°C
        "relative_humidity": (0.0, 1.0),  # 0-1
        "wind_speed_ms": (0.0, 200.0),  # 0 to 200 m/s (hurricane+)
        "wind_direction_deg": (0.0, 360.0),  # 0-360°
        "wind_gust_intensity": (0.0, 1.0),  # 0-1
        "turbulence_level": (0.0, 1.0),  # 0-1
        
        # Control
        "pid_stability_rating": (0.0, 1.0),  # 0-1
        "pilot_skill": (0.0, 1.0),  # 0-1
        "control_latency_ms": (0.1, 1000.0),  # 0.1ms to 1000ms
        
        # Hardware
        "hull_temperature_c": (-50.0, 150.0),  # -50°C to 150°C
        "motor_temperature_c": (-50.0, 300.0),  # -50°C to 300°C
        "battery_temperature_c": (-20.0, 80.0),  # -20°C to 80°C
        "battery_state_of_health": (0.5, 1.0),  # 50% to 100%
        "thruster_variation": (0.0, 0.2),  # 0-20%
        "weight_distribution_error": (0.0, 0.1),  # 0-10%
        "propeller_efficiency_degradation": (0.5, 1.0),  # 50-100%
        
        # Advanced
        "geomagnetic_interference": (0.0, 1.0),  # 0-1
        "solar_radiation_intensity": (0.5, 2.0),  # 0.5-2× standard
        "precipitation": (0.0, 1.0),  # 0-1
    }
    
    def validate_range(self, value: float, field_name: str) -> bool:
        """
        Check if value is within physical bounds.
        
        Args:
            value: Value to check
            field_name: Field name for error message
        
        Returns:
            True if within bounds
        """
        if field_name not in self.PHYSICAL_BOUNDS:
            return True  # No bounds defined
        
        min_val, max_val = self.PHYSICAL_BOUNDS[field_name]
        return min_val <= value <= max_val
    
    def get_bounds(self, field_name: str) -> str:
        """Get human-readable bounds string."""
        if field_name not in self.PHYSICAL_BOUNDS:
            return "no bounds defined"
        
        min_val, max_val = self.PHYSICAL_BOUNDS[field_name]
        return f"{min_val} to {max_val}"
    
    def validate_craft_config(self, config: CraftConfig) -> List[str]:
        """
        Validate entire CraftConfig.
        
        Args:
            config: CraftConfig to validate
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check all bounded fields
        for field_name, (min_val, max_val) in self.PHYSICAL_BOUNDS.items():
            if hasattr(config, field_name):
                value = getattr(config, field_name)
                if not self.validate_range(value, field_name):
                    errors.append(
                        f"{field_name} = {value} is outside valid range "
                        f"({min_val} to {max_val})"
                    )
        
        # Cross-field validations
        
        # TWR sanity check
        weight = config.mass_kg * 9.80665
        twr = config.thrust_newtons / weight if weight > 0 else float('inf')
        if twr > 50:
            errors.append(f"TWR = {twr:.1f} is unrealistically high (>50)")
        elif twr < 0.01:
            errors.append(f"TWR = {twr:.3f} is unrealistically low (<0.01)")
        
        # Power sanity check
        if config.max_power_kw > 0 and config.battery_capacity_kwh > 0:
            theoretical_endurance_h = config.battery_capacity_kwh / config.max_power_kw
            if theoretical_endurance_h < 0.001:  # < 3.6 seconds
                errors.append(
                    f"Battery capacity too small for power: "
                    f"{config.battery_capacity_kwh}kWh / {config.max_power_kw}kW = "
                    f"{theoretical_endurance_h*3600:.1f}s"
                )
        
        # Aerodynamics sanity check
        if config.drag_coefficient > 3.0:
            errors.append(f"Drag coefficient = {config.drag_coefficient} is very high (>3.0)")
        
        # Control sanity check
        if config.pid_stability_rating < 0.3 and config.pilot_skill < 0.3:
            errors.append(
                "Both PID stability and pilot skill are very low (<0.3). "
                "Craft will likely be uncontrollable."
            )
        
        # Speculative propulsion warning
        if config.propulsion_type.is_speculative:
            warnings = [
                f"{config.propulsion_type.name} is speculative/experimental. "
                "Results may not reflect real-world physics."
            ]
            # Add warnings to errors list for visibility
            errors.extend(warnings)
        
        return errors
    
    def validate_propulsion_type(self, propulsion_type: str) -> bool:
        """
        Check if propulsion type is valid.
        
        Args:
            propulsion_type: Propulsion type string
        
        Returns:
            True if valid
        """
        try:
            PropulsionType(propulsion_type)
            return True
        except ValueError:
            return False
    
    def get_all_bounds(self) -> Dict[str, str]:
        """Get all physical bounds as human-readable strings."""
        return {
            field: self.get_bounds(field)
            for field in self.PHYSICAL_BOUNDS
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"ConfigValidator(bounds={len(self.PHYSICAL_BOUNDS)} fields)"
    
    def __repr__(self) -> str:
        """Repr representation."""
        return self.__str__()
