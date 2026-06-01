"""
Atmospheric model with ISA + humidity + temperature corrections.
Based on International Standard Atmosphere (ISA) with real-world deviations.
"""

import math
import random
from typing import Optional, List


class AtmosphereModel:
    """
    Full atmospheric model including humidity, temperature, pressure, and advanced effects.
    
    Based on:
    - International Standard Atmosphere (ISA) [web:21][web:22][web:28]
    - Ideal Gas Law with water vapor correction [web:17][web:20]
    - Density altitude calculations [web:1][web:14][web:15]
    """
    
    # ========== CONSTANTS ==========
    R_DRY_AIR = 287.05  # J/(kg·K) - specific gas constant for dry air
    R_WATER_VAPOR = 461.5  # J/(kg·K) - specific gas constant for water vapor
    R_SEA_LEVEL = 1.225  # kg/m³ - standard air density at sea level
    P_SEA_LEVEL = 101325  # Pa - standard pressure at sea level
    T_SEA_LEVEL = 288.15  # K - standard temperature at sea level (15°C)
    LAPS_RATE = 0.0065  # K/m - temperature lapse rate in troposphere
    H_SCALE = 8500.0  # m - scale height for atmosphere
    G = 9.80665  # m/s² - standard gravity
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize atmosphere model.
        
        Args:
            seed: Random seed for reproducibility (optional)
        """
        self.seed = seed
        self.rng = random.Random(seed) if seed else random.Random()
    
    # ========== BASIC ATMOSPHERIC PROPERTIES ==========
    
    def temperature_isa(self, altitude: float) -> float:
        """
        Calculate ISA temperature at altitude (Kelvin).
        
        Args:
            altitude: Altitude in meters
        
        Returns:
            Temperature in Kelvin
        """
        if altitude < 11000:  # Troposphere
            return self.T_SEA_LEVEL - (self.LAPS_RATE * altitude)
        else:  # Stratosphere (constant)
            return 216.65  # K
    
    def temperature_isa_c(self, altitude: float) -> float:
        """ISA temperature at altitude (Celsius)."""
        return self.temperature_isa(altitude) - 273.15
    
    def pressure(self, altitude: float) -> float:
        """
        Calculate atmospheric pressure at altitude (Pascals).
        
        Args:
            altitude: Altitude in meters
        
        Returns:
            Pressure in Pascals
        """
        if altitude < 11000:  # Troposphere
            temp_ratio = 1 - (self.LAPS_RATE * altitude) / self.T_SEA_LEVEL
            exponent = self.G / (self.R_DRY_AIR * self.LAPS_RATE)
            return self.P_SEA_LEVEL * (temp_ratio ** exponent)
        else:  # Stratosphere
            pressure_11k = self.pressure(11000)
            return pressure_11k * math.exp(-(altitude - 11000) / 6384)
    
    def pressure_altitude(self, altitude: float) -> float:
        """
        Calculate pressure altitude (altitude in standard atmosphere).
        
        Args:
            altitude: Actual altitude in meters
        
        Returns:
            Pressure altitude in meters
        """
        # For most practical purposes, pressure altitude ≈ geometric altitude
        # In precision applications, this would account for barometric pressure variations
        return altitude
    
    def air_density_dry(self, altitude: float, temperature_k: float = None) -> float:
        """
        Calculate air density for dry air.
        
        ρ = P / (R × T)
        
        Args:
            altitude: Altitude in meters
            temperature_k: Temperature in Kelvin (optional, uses ISA if None)
        
        Returns:
            Air density in kg/m³ [web:17][web:20]
        """
        pressure = self.pressure(altitude)
        
        if temperature_k is None:
            temperature_k = self.temperature_isa(altitude)
        
        return pressure / (self.R_DRY_AIR * temperature_k)
    
    def saturation_vapor_pressure(self, temperature_k: float) -> float:
        """
        Calculate saturation vapor pressure using Magnus formula.
        
        Args:
            temperature_k: Temperature in Kelvin
        
        Returns:
            Saturation vapor pressure in Pascals
        """
        temperature_c = temperature_k - 273.15
        # Magnus formula: e_sat = 6.112 × exp((17.67 × T) / (T + 243.5)) hPa
        e_sat_hpa = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5))
        return e_sat_hpa * 100  # Convert hPa to Pa
    
    def vapor_pressure_from_dewpoint(self, dew_point_k: float) -> float:
        """
        Calculate vapor pressure from dew point temperature.
        
        Args:
            dew_point_k: Dew point temperature in Kelvin
        
        Returns:
            Vapor pressure in Pascals
        """
        return self.saturation_vapor_pressure(dew_point_k)
    
    def vapor_pressure_from_humidity(self, temperature_k: float, relative_humidity: float) -> float:
        """
        Calculate vapor pressure from relative humidity.
        
        Args:
            temperature_k: Temperature in Kelvin
            relative_humidity: Relative humidity (0-1)
        
        Returns:
            Vapor pressure in Pascals
        """
        e_sat = self.saturation_vapor_pressure(temperature_k)
        return relative_humidity * e_sat
    
    def air_density_humid(self, altitude: float, temperature_k: float,
                          dew_point_k: float = None,
                          relative_humidity: float = None) -> float:
        """
        Calculate air density including humidity (water vapor).
        
        ρ_humid = (p_d / (R_d × T)) + (p_v / (R_v × T))
        
        Humid air is LESS dense than dry air (H₂O molecule is lighter than N₂/O₂) [web:17]
        
        Args:
            altitude: Altitude in meters
            temperature_k: Temperature in Kelvin
            dew_point_k: Dew point temperature in Kelvin (optional)
            relative_humidity: Relative humidity 0-1 (alternative to dew_point)
        
        Returns:
            Air density in kg/m³ [web:1][web:17][web:20]
        """
        pressure = self.pressure(altitude)
        
        # Calculate vapor pressure
        if dew_point_k:
            vapor_pressure = self.vapor_pressure_from_dewpoint(dew_point_k)
        elif relative_humidity:
            vapor_pressure = self.vapor_pressure_from_humidity(temperature_k, relative_humidity)
        else:
            vapor_pressure = 0  # Dry air
        
        # Partial pressure of dry air
        dry_air_pressure = pressure - vapor_pressure
        
        # Humid air density (Ideal Gas Law with both components)
        density = (dry_air_pressure / (self.R_DRY_AIR * temperature_k) +
                   vapor_pressure / (self.R_WATER_VAPOR * temperature_k))
        
        return density
    
    def air_density(self, altitude: float, temperature_c: float = None,
                    dew_point_c: float = None, relative_humidity: float = None,
                    use_humidity: bool = True) -> float:
        """
        Calculate air density with optional humidity correction.
        
        Convenience method that handles unit conversions.
        
        Args:
            altitude: Altitude in meters
            temperature_c: Temperature in Celsius (optional, uses ISA if None)
            dew_point_c: Dew point in Celsius (optional)
            relative_humidity: Relative humidity 0-1 (alternative to dew_point)
            use_humidity: If True, include humidity correction
        
        Returns:
            Air density in kg/m³
        """
        # Convert to Kelvin
        if temperature_c is None:
            temperature_k = self.temperature_isa(altitude)
        else:
            temperature_k = temperature_c + 273.15
        
        dew_point_k = dew_point_c + 273.15 if dew_point_c else None
        
        if use_humidity and (dew_point_k or relative_humidity):
            return self.air_density_humid(altitude, temperature_k, dew_point_k, relative_humidity)
        else:
            return self.air_density_dry(altitude, temperature_k)
    
    # ========== DENSITY ALTITUDE ==========
    
    def density_altitude(self, pressure_altitude: float, oat_c: float,
                         dew_point_c: float = None) -> float:
        """
        Calculate density altitude (pressure altitude corrected for temp + humidity).
        
        Density Altitude determines actual aircraft performance.
        
        Rule of thumb:
        - 120 ft per °C from ISA temperature [web:1]
        - Humidity correction: (dew_point × 2) × 10 ft [web:18]
        
        Args:
            pressure_altitude: Pressure altitude in meters
            oat_c: Outside air temperature in Celsius
            dew_point_c: Dew point in Celsius (optional)
        
        Returns:
            Density altitude in meters [web:1][web:14][web:15][web:18]
        """
        # ISA temperature at pressure altitude
        isa_temp_c = self.temperature_isa_c(pressure_altitude)
        
        # Temperature correction (120 ft per °C from ISA)
        temp_correction = 120 * 0.3048 * (oat_c - isa_temp_c)  # Convert ft to m
        
        # Humidity correction
        humidity_correction = 0
        if dew_point_c:
            humidity_correction = (dew_point_c * 2) * 10 * 0.3048  # Convert ft to m
        
        density_alt = pressure_altitude + temp_correction + humidity_correction
        
        return density_alt
    
    # ========== WIND & TURBULENCE ==========
    
    def simulate_wind_gust(self, base_speed: float, intensity: float = 0.1) -> float:
        """
        Add random wind gust to base speed (seeded for reproducibility).
        
        Args:
            base_speed: Base wind speed in m/s
            intensity: Gust intensity (0-1, higher = more variance)
        
        Returns:
            Wind speed with gust in m/s
        """
        gust_offset = self.rng.gauss(0, intensity * base_speed)
        return base_speed + gust_offset
    
    def simulate_turbulence(self, base_speed: float, turbulence_level: float = 0.05,
                            num_samples: int = 100) -> List[float]:
        """
        Simulate turbulence over time (returns list of wind speeds).
        
        Uses seeded randomness for reproducibility.
        
        Args:
            base_speed: Base wind speed in m/s
            turbulence_level: Turbulence intensity (0-1)
            num_samples: Number of samples
        
        Returns:
            List of wind speeds in m/s
        """
        turbulence = []
        for _ in range(num_samples):
            offset = self.rng.gauss(0, turbulence_level * base_speed)
            turbulence.append(base_speed + offset)
        return turbulence
    
    # ========== ADVANCED ATMOSPHERIC ==========
    
    def speed_of_sound(self, temperature_k: float) -> float:
        """
        Calculate speed of sound at given temperature.
        
        a = √(γ × R × T)
        
        Args:
            temperature_k: Temperature in Kelvin
        
        Returns:
            Speed of sound in m/s
        """
        gamma = 1.4  # Ratio of specific heats for air
        return math.sqrt(gamma * self.R_DRY_AIR * temperature_k)
    
    def mach_number(self, velocity_ms: float, temperature_k: float) -> float:
        """
        Calculate Mach number.
        
        Args:
            velocity_ms: Velocity in m/s
            temperature_k: Temperature in Kelvin
        
        Returns:
            Mach number (dimensionless)
        """
        speed_of_sound = self.speed_of_sound(temperature_k)
        return velocity_ms / speed_of_sound if speed_of_sound > 0 else 0
    
    def kinematic_viscosity(self, temperature_k: float) -> float:
        """
        Calculate kinematic viscosity of air (Sutherland's law).
        
        Args:
            temperature_k: Temperature in Kelvin
        
        Returns:
            Kinematic viscosity in m²/s
        """
        # Sutherland's law for dynamic viscosity
        mu_0 = 1.716e-5  # Reference viscosity at T_0
        T_0 = 273.15  # Reference temperature
        S = 110.4  # Sutherland constant
        
        mu = mu_0 * ((temperature_k / T_0) ** 1.5) * ((T_0 + S) / (temperature_k + S))
        
        # Kinematic viscosity = dynamic viscosity / density
        density = self.air_density_dry(0, temperature_k)
        
        return mu / density if density > 0 else 0
    
    def Reynolds_number(self, velocity_ms: float, length_m: float, 
                        temperature_k: float) -> float:
        """
        Calculate Reynolds number.
        
        Re = (ρ × V × L) / μ
        
        Args:
            velocity_ms: Velocity in m/s
            length_m: Characteristic length in meters
            temperature_k: Temperature in Kelvin
        
        Returns:
            Reynolds number (dimensionless)
        """
        density = self.air_density_dry(0, temperature_k)
        kinematic_viscosity = self.kinematic_viscosity(temperature_k)
        
        if kinematic_viscosity > 0:
            return (velocity_ms * length_m) / kinematic_viscosity
        else:
            return 0
    
    # ========== Utility ==========
    
    def get_standard_conditions(self, altitude: float) -> dict:
        """
        Get all standard atmospheric conditions at altitude.
        
        Args:
            altitude: Altitude in meters
        
        Returns:
            Dictionary with all atmospheric properties
        """
        temp_k = self.temperature_isa(altitude)
        
        return {
            "altitude_m": altitude,
            "temperature_k": temp_k,
            "temperature_c": temp_k - 273.15,
            "pressure_pa": self.pressure(altitude),
            "pressure_atm": self.pressure(altitude) / 101325,
            "density_kg_m3": self.air_density_dry(altitude),
            "speed_of_sound_ms": self.speed_of_sound(temp_k),
            "kinematic_viscosity_m2_s": self.kinematic_viscosity(temp_k),
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"AtmosphereModel(seed={self.seed})"
    
    def __repr__(self) -> str:
        """Repr representation."""
        return self.__str__()
