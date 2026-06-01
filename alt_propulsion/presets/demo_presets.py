"""
Demo preset configurations for testing.
"""

from typing import List, Tuple
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.enums import PropulsionType


def get_demo_presets() -> List[Tuple[str, CraftConfig]]:
    """Return list of demo preset configurations."""
    
    return [
        ("Quadcopter Drone", CraftConfig(
            mass_kg=1.5,
            thrust_newtons=20.0,
            num_thrusters=4,
            thrust_symmetry=0.95,
            center_of_mass_height_m=0.05,
            center_of_thrust_height_m=0.02,
            base_area_m2=0.05,
            max_power_kw=2.0,
            battery_capacity_kwh=0.5,
            propulsion_type=PropulsionType.VTOL_MULTICOPTER,
            pid_stability_rating=0.9,
            pilot_skill=0.8
        )),
        
        ("Heavy Lift VTOL", CraftConfig(
            mass_kg=5000.0,
            thrust_newtons=60000.0,
            num_thrusters=8,
            thrust_symmetry=0.9,
            center_of_mass_height_m=2.0,
            center_of_thrust_height_m=1.0,
            base_area_m2=50.0,
            max_power_kw=2000.0,
            battery_capacity_kwh=500.0,
            propulsion_type=PropulsionType.VTOL,
            pid_stability_rating=0.85,
            pilot_skill=0.75
        )),
        
        ("Jetpack (Underpowered)", CraftConfig(
            mass_kg=150.0,
            thrust_newtons=1200.0,
            num_thrusters=2,
            thrust_symmetry=0.8,
            center_of_mass_height_m=0.8,
            center_of_thrust_height_m=1.2,
            base_area_m2=0.5,
            max_power_kw=100.0,
            battery_capacity_kwh=5.0,
            propulsion_type=PropulsionType.JETPACK,
            pid_stability_rating=0.5,
            pilot_skill=0.6
        )),
        
        ("Hovercraft", CraftConfig(
            mass_kg=5000.0,
            thrust_newtons=8000.0,
            num_thrusters=1,
            thrust_symmetry=1.0,
            center_of_mass_height_m=0.3,
            center_of_thrust_height_m=0.1,
            base_area_m2=30.0,
            max_power_kw=300.0,
            battery_capacity_kwh=100.0,
            propulsion_type=PropulsionType.HOVERCRAFT,
            test_phase=TestPhase.PRE_FLIGHT_AERO
        )),
        
        ("Ion Thruster (Space)", CraftConfig(
            mass_kg=1000.0,
            thrust_newtons=0.5,
            num_thrusters=1,
            thrust_symmetry=1.0,
            center_of_mass_height_m=0.5,
            center_of_thrust_height_m=0.5,
            base_area_m2=5.0,
            max_power_kw=50.0,
            battery_capacity_kwh=1000.0,
            propulsion_type=PropulsionType.ION_THRUSTER,
            altitude_m=400000,
            pid_stability_rating=0.95
        )),
        
        ("Anti-Gravity Craft", CraftConfig(
            mass_kg=2000.0,
            thrust_newtons=20000.0,
            num_thrusters=1,
            thrust_symmetry=1.0,
            center_of_mass_height_m=1.0,
            center_of_thrust_height_m=1.0,
            base_area_m2=20.0,
            max_power_kw=0.0,
            battery_capacity_kwh=0.0,
            propulsion_type=PropulsionType.ANTI_GRAVITY,
            pid_stability_rating=1.0,
            pilot_skill=1.0
        )),
        
        ("Winged VTOL (eVTOL)", CraftConfig(
            mass_kg=2500.0,
            thrust_newtons=30000.0,
            num_thrusters=6,
            thrust_symmetry=0.92,
            center_of_mass_height_m=1.5,
            center_of_thrust_height_m=0.8,
            base_area_m2=25.0,
            lift_coefficient_max=1.8,
            max_power_kw=1500.0,
            battery_capacity_kwh=400.0,
            propulsion_type=PropulsionType.WINGED_VTOL,
            pid_stability_rating=0.88,
            pilot_skill=0.8
        )),
        
        ("Ducted Fan VTOL", CraftConfig(
            mass_kg=500.0,
            thrust_newtons=6000.0,
            num_thrusters=4,
            thrust_symmetry=0.95,
            center_of_mass_height_m=0.6,
            center_of_thrust_height_m=0.4,
            base_area_m2=5.0,
            max_power_kw=500.0,
            battery_capacity_kwh=50.0,
            propulsion_type=PropulsionType.DUCTED_FAN,
            pid_stability_rating=0.85
        ))
    ]
