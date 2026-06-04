"""
Core physics engine for flight dynamics calculations.
Pure, deterministic functions with seeded randomness support.
"""

import math
import random
from typing import Optional, Dict, Any
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.flight_analysis import FlightAnalysis
from alt_propulsion.models.enums import FlightOutcome, PropulsionType, TestPhase
from alt_propulsion.core.atmosphere import AtmosphereModel


class PhysicsEngine:
    """
    Pure physics engine for flight dynamics calculations.
    
    All methods are deterministic (same input → same output).
    Supports seeded randomness for Monte Carlo simulations.
    """
    
    # ========== CONSTANTS ==========
    G = 9.80665  # m/s² - standard gravity
    RHO_SEA_LEVEL = 1.225  # kg/m³ - air density at sea level
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize physics engine.
        
        Args:
            seed: Random seed for reproducibility (optional)
        """
        self.seed = seed
        self.rng = random.Random(seed) if seed else random.Random()
        self.atmosphere = AtmosphereModel(seed)
    
    # ========== STATIC METHODS (For direct use without instantiation) ==========
    
    @staticmethod
    def calculate_twr_static(config: CraftConfig) -> float:
        """
        Calculate Thrust-to-Weight Ratio (static method).
        
        TWR = Thrust / Weight = Thrust / (mass × g)
        
        Args:
            config: Craft configuration
        
        Returns:
            Thrust-to-Weight Ratio (dimensionless)
        """
        weight = config.mass_kg * PhysicsEngine.G
        return config.thrust_newtons / weight if weight > 0 else float('inf')
    
    @staticmethod
    def calculate_weight_static(mass_kg: float) -> float:
        """Calculate weight in Newtons."""
        return mass_kg * PhysicsEngine.G
    
    # ========== THRUST-TO-WEIGHT RATIO ==========
    
    def calculate_twr(self, config: CraftConfig) -> float:
        """
        Calculate Thrust-to-Weight Ratio with variance applied.
        
        Args:
            config: Craft configuration
        
        Returns:
            TWR (dimensionless)
        """
        return self.calculate_twr_static(config)
    
    # ========== STABILITY CALCULATION ==========
    
    def calculate_stability(self, config: CraftConfig) -> float:
        """
        Calculate overall stability score (0-1).
        
        Components:
        - COM/COT alignment (30%)
        - Thrust symmetry (25%)
        - Control system (PID × pilot) (25%)
        - Propulsion type modifier (20%)
        - Wind penalty (subtracted)
        
        Args:
            config: Craft configuration
        
        Returns:
            Stability score (0-1, higher = more stable)
        """
        # COM/COT alignment
        com_cot_offset = math.sqrt(
            (config.center_of_mass_height_m - config.center_of_thrust_height_m) ** 2 +
            (config.center_of_mass_lateral_m - config.center_of_thrust_lateral_m) ** 2
        )
        alignment_score = max(0.0, min(1.0, 1.0 - com_cot_offset / 2.0))
        
        # Symmetry factor
        symmetry_score = config.thrust_symmetry
        
        # Control system compensation
        control_score = config.pid_stability_rating * config.pilot_skill
        
        # Wind disturbance penalty
        wind_penalty = min(0.3, config.wind_speed_ms / 50.0)
        
        # Propulsion-specific stability modifier
        type_modifier = config.propulsion_type.stability_modifier
        
        # Weighted combination
        stability = (
            alignment_score * 0.30 +
            symmetry_score * 0.25 +
            control_score * 0.25 +
            type_modifier * 0.20
        ) - wind_penalty
        
        return max(0.0, min(1.0, stability))
    
    # ========== HOVER EFFICIENCY ==========
    
    def calculate_hover_efficiency(self, config: CraftConfig) -> float:
        """
        Calculate hover efficiency (0-1).
        
        Efficiency peaks at TWR = 1.0 (exactly enough thrust to hover).
        Higher TWR = less efficient (excess thrust).
        Lower TWR = cannot hover.
        
        Args:
            config: Craft configuration
        
        Returns:
            Hover efficiency (0-1)
        """
        twr = self.calculate_twr(config)
        
        if twr <= 0:
            return 0.0
        
        # Efficiency peaks at TWR = 1.0
        if twr >= 1.0:
            efficiency = 1.0 / twr  # Higher TWR = less efficient
        else:
            efficiency = twr  # Can't hover if TWR < 1
        
        # Propulsion type efficiency modifier
        efficiency_mod = config.propulsion_type.efficiency_modifier
        
        # Propeller degradation
        efficiency_mod *= config.propeller_efficiency_degradation
        
        return max(0.0, min(1.0, efficiency * efficiency_mod))
    
    # ========== ENDURANCE CALCULATION ==========
    
    def calculate_endurance(self, config: CraftConfig) -> float:
        """
        Calculate flight endurance in seconds.
        
        Args:
            config: Craft configuration
        
        Returns:
            Endurance in seconds (float('inf') for anti-gravity)
        """
        if config.max_power_kw <= 0 or config.battery_capacity_kwh <= 0:
            return 0.0
        
        twr = self.calculate_twr(config)
        if twr < 1.0:
            return 0.0  # Can't hover, no endurance
        
        # Anti-gravity: infinite endurance
        if config.propulsion_type == PropulsionType.ANTI_GRAVITY:
            return float('inf')
        
        # Air density at altitude
        rho = self.atmosphere.air_density(
            config.altitude_m,
            config.temperature_c,
            config.dew_point_c,
            config.relative_humidity
        )
        
        if rho <= 0:
            return 0.0
        
        # Induced velocity for hover (momentum theory)
        disk_area = config.base_area_m2
        if disk_area <= 0:
            return 0.0
        
        induced_vel = math.sqrt(
            (config.mass_kg * self.G) / (2 * rho * disk_area)
        )
        
        # Hover power (Watts)
        hover_efficiency = self.calculate_hover_efficiency(config)
        if hover_efficiency <= 0:
            return 0.0
        
        hover_power_w = (config.mass_kg * self.G * induced_vel) / hover_efficiency
        hover_power_kw = hover_power_w / 1000.0
        
        # Actual power (capped at max)
        actual_power = min(hover_power_kw, config.max_power_kw)
        
        if actual_power <= 0:
            return 0.0
        
        # Endurance formula: capacity / power × 3600 (seconds)
        endurance = (config.battery_capacity_kwh / actual_power) * 3600
        
        # Apply battery SOH
        endurance *= config.battery_state_of_health
        
        return endurance
    
    # ========== MAX ALTITUDE ==========
    
    def calculate_max_altitude(self, config: CraftConfig) -> float:
        """
        Calculate maximum achievable altitude.
        
        Args:
            config: Craft configuration
        
        Returns:
            Max altitude in meters (float('inf') for space-capable)
        """
        twr = self.calculate_twr(config)
        
        if twr <= 1.0:
            return config.altitude_m  # Can't climb
        
        # Ion thruster: works in vacuum (very highaltitude)
        if config.propulsion_type == PropulsionType.ION_THRUSTER:
            return 100000.0  # 100 km (edge of space)
        
        # Anti-gravity: unlimited
        if config.propulsion_type == PropulsionType.ANTI_GRAVITY:
            return float('inf')
        
        # Rocket/jetpack: thrust roughly constant
        if config.propulsion_type == PropulsionType.JETPACK:
            return 50000.0  # 50 km
        
        # Propeller-based: thrust ∝ air density
        # TWR_at_alt = TWR_sea × (rho_alt / rho_sea)
        # Set TWR = 1: rho_alt = rho_sea / TWR_sea
        rho_needed = self.RHO_SEA_LEVEL / twr
        
        if rho_needed <= 0:
            return float('inf')
        
        # Solve for altitude: rho = rho_sea × exp(-h / H)
        # h = -H × ln(rho / rho_sea)
        H = self.atmosphere.H_SCALE
        max_alt = -H * math.log(rho_needed / self.RHO_SEA_LEVEL)
        
        return max(0.0, max_alt)
    
    # ========== CLIMB RATE ==========
    
    def calculate_climb_rate(self, config: CraftConfig) -> float:
        """
        Calculate maximum climb rate (m/s).
        
        Args:
            config: Craft configuration
        
        Returns:
            Climb rate in m/s
        """
        twr = self.calculate_twr(config)
        
        if twr <= 1.0:
            return 0.0  # Can't climb
        
        # Excess thrust provides climb
        excess_twr = twr - 1.0
        
        # Rough approximation: climb_rate ≈ excess_twr × characteristic_velocity
        hover_efficiency = self.calculate_hover_efficiency(config)
        
        rho = self.atmosphere.air_density(config.altitude_m, config.temperature_c)
        
        disk_area = config.base_area_m2
        induced_vel = math.sqrt(
            (config.mass_kg * self.G) / (2 * rho * disk_area)
        ) if disk_area > 0 else 10.0
        
        # Characteristic velocity
        char_vel = induced_vel * 2.0
        
        climb_rate = excess_twr * char_vel * hover_efficiency
        
        return max(0.0, min(climb_rate, 50.0))  # Cap at 50 m/s
    
    # ========== THERMAL MARGIN ==========
    
    def calculate_thermal_margin(self, config: CraftConfig) -> float:
        """
        Calculate thermal margin (0-1, higher = more headroom).
        
        Args:
            config: Craft configuration
        
        Returns:
            Thermal margin (0-1)
        """
        # Estimate motor temperature under load
        twr = self.calculate_twr(config)
        power_factor = min(1.0, twr / 2.0) if twr > 0 else 0.0
        
        # Temperature rise proportional to power
        temp_rise = power_factor * 80.0  # Up to 80°C rise
        estimated_motor_temp = config.motor_temperature_c + temp_rise
        
        # Thermal limit
        thermal_limit = 150.0  # °C
        
        margin = max(0.0, min(1.0, 1.0 - (estimated_motor_temp / thermal_limit)))
        
        return margin
    
    # ========== STRUCTURAL MARGIN ==========
    
    def calculate_structural_margin(self, config: CraftConfig) -> float:
        """
        Calculate structural margin (0-1, higher = more headroom).
        
        Args:
            config: Craft configuration
        
        Returns:
            Structural margin (0-1)
        """
        twr = self.calculate_twr(config)
        
        # Higher TWR = more stress
        stress_factor = twr / 3.0  # Normalized to 3.0 TWR = 100% stress
        
        margin = max(0.0, min(1.0, 1.0 - stress_factor))
        
        return margin
    
    # ========== CONTROL MARGIN ==========
    
    def calculate_control_margin(self, config: CraftConfig) -> float:
        """
        Calculate control authority margin (0-1).
        
        Args:
            config: Craft configuration
        
        Returns:
            Control margin (0-1)
        """
        # Based on symmetry, PID, pilot skill
        symmetry = config.thrust_symmetry
        control = config.pid_stability_rating * config.pilot_skill
        
        # Wind penalty
        wind_penalty = min(0.3, config.wind_speed_ms / 50.0)
        
        margin = (symmetry + control) / 2.0 - wind_penalty
        
        return max(0.0, min(1.0, margin))
    
    # ========== OUTCOME DETERMINATION ==========
    
    def determine_outcome(self, twr: float, stability: float, 
                          endurance: float, config: CraftConfig) -> FlightOutcome:
        """
        Determine flight outcome based on physics.
        
        Args:
            twr: Thrust-to-Weight Ratio
            stability: Stability score (0-1)
            endurance: Endurance in seconds
            config: Craft configuration
        
        Returns:
            FlightOutcome enum
        """
        # Immediate crash conditions
        if twr < 1.0:
            return FlightOutcome.CRASH
        
        if stability < 0.2:
            return FlightOutcome.CRASH
        
        if endurance <= 0 and config.propulsion_type != PropulsionType.ANTI_GRAVITY:
            return FlightOutcome.INSUFFICIENT_POWER
        
        # Unstable hover
        if stability < 0.5:
            return FlightOutcome.UNSTABLE_HOVER
        
        # Stable conditions
        if 0.95 <= twr <= 1.15:
            return FlightOutcome.HOVER
        elif twr > 1.15:
            return FlightOutcome.FLY
        
        # Special cases
        if config.propulsion_type == PropulsionType.HOVERCRAFT:
            if twr >= 1.0 and stability >= 0.5:
                return FlightOutcome.GROUND_EFFECT
        
        if config.propulsion_type in [PropulsionType.ION_THRUSTER, PropulsionType.ANTI_GRAVITY]:
            if config.altitude_m > 100000:
                return FlightOutcome.SPACE_FLIGHT
        
        return FlightOutcome.CRASH
    
    # ========== FULL ANALYSIS ==========
    
    def analyze(self, config: CraftConfig) -> FlightAnalysis:
        """
        Perform complete flight dynamics analysis.
        
        Args:
            config: Craft configuration
        
        Returns:
            Complete FlightAnalysis result
        """
        # Calculate all metrics
        twr = self.calculate_twr(config)
        stability = self.calculate_stability(config)
        efficiency = self.calculate_hover_efficiency(config)
        endurance = self.calculate_endurance(config)
        max_alt = self.calculate_max_altitude(config)
        climb_rate = self.calculate_climb_rate(config)
        thermal_margin = self.calculate_thermal_margin(config)
        structural_margin = self.calculate_structural_margin(config)
        control_margin = self.calculate_control_margin(config)
        
        # Atmospheric properties
        air_density = self.atmosphere.air_density(
            config.altitude_m, config.temperature_c,
            config.dew_point_c, config.relative_humidity
        )
        pressure_alt = self.atmosphere.pressure_altitude(config.altitude_m)
        density_alt = self.atmosphere.density_altitude(
            pressure_alt, config.temperature_c, config.dew_point_c
        )
        
        # Determine outcome
        outcome = self.determine_outcome(twr, stability, endurance, config)
        
        # Generate warnings
        warnings = []
        if twr < 0.8:
            warnings.append("CRITICAL: Thrust-to-weight ratio dangerously low (TWR < 0.8)!")
        elif twr < 1.0:
            warnings.append("WARNING: Insufficient thrust for liftoff (TWR < 1.0).")
        elif twr > 3.0:
            warnings.append("NOTE: Very high TWR (>3.0) - control authority may be excessive.")
        
        if stability < 0.3:
            warnings.append("CRITICAL: Craft is highly unstable (stability < 0.3)!")
        elif stability < 0.5:
            warnings.append("WARNING: Low stability margin (stability < 0.5).")
        
        if endurance < 60 and outcome != FlightOutcome.CRASH:
            warnings.append(f"WARNING: Flight endurance only {endurance:.1f} seconds.")
        
        if config.wind_speed_ms > 15:
            warnings.append(f"WARNING: High wind ({config.wind_speed_ms} m/s) detected.")
        
        if thermal_margin < 0.3:
            warnings.append(f"WARNING: Low thermal margin ({thermal_margin:.1%}).")
        
        if structural_margin < 0.3:
            warnings.append(f"WARNING: Low structural margin ({structural_margin:.1%}).")
        
        # Speculative propulsion warning
        if config.propulsion_type.is_speculative:
            warnings.append(
                f"WARNING: {config.propulsion_type.name} is speculative/experimental. "
                "Results may not reflect real-world physics."
            )
        
        # Generate recommendations
        recommendations = []
        if twr < 1.0:
            recommendations.append("Increase thrust or reduce mass to achieve TWR > 1.0.")
        if stability < 0.5:
            recommendations.append("Lower center of mass or raise center of thrust.")
            recommendations.append("Improve thrust symmetry (>0.9 recommended).")
            recommendations.append("Increase PID stability rating or pilot skill.")
        if endurance < 300:
            recommendations.append("Increase battery capacity or reduce power consumption.")
        if thermal_margin < 0.5:
            recommendations.append("Improve cooling or reduce power output.")
        if config.propulsion_type == PropulsionType.JETPACK and config.mass_kg > 200:
            recommendations.append("Jetpack mass exceeds safe human-portable limits (>200 kg).")
        
        # Hover power
        if endurance > 0:
            hover_power = (config.battery_capacity_kwh / endurance) * 3600 * 1000  # Convert to Watts
            hover_power_kw = hover_power / 1000
        else:
            hover_power_kw = 0.0
        
        return FlightAnalysis(
            outcome=outcome,
            twr=twr,
            stability_score=stability,
            hover_efficiency=efficiency,
            max_altitude_m=max_alt,
            endurance_seconds=endurance,
            climb_rate_ms=climb_rate,
            descent_rate_ms=climb_rate * 0.7,  # Rough estimate
            hover_power_kw=hover_power_kw,
            thermal_margin=thermal_margin,
            structural_margin=structural_margin,
            control_margin=control_margin,
            air_density_kg_m3=air_density,
            density_altitude_m=density_alt,
            test_phase=config.test_phase,
            warnings=warnings,
            recommendations=recommendations,
            seed=self.seed,
            propulsion_type=config.propulsion_type,
            mass_kg=config.mass_kg,
            thrust_newtons=config.thrust_newtons
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"PhysicsEngine(seed={self.seed})"
    
    def __repr__(self) -> str:
        """Repr representation."""
        return self.__str__()
