"""
Tests for physics engine.
"""

import pytest
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.enums import PropulsionType, FlightOutcome
from alt_propulsion.core.physics import PhysicsEngine


class TestPhysicsEngine:
    """Tests for PhysicsEngine."""
    
    def test_calculate_twr_basic(self):
        """Test basic TWR calculation."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=12000.0)
        engine = PhysicsEngine()
        
        twr = engine.calculate_twr(config)
        expected = 12000.0 / (1000.0 * 9.80665)
        
        assert abs(twr - expected) < 0.001
    
    def test_twr_less_than_1_crash(self):
        """Test that TWR < 1.0 results in CRASH."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=8000.0)  # TWR = 0.816
        engine = PhysicsEngine()
        
        analysis = engine.analyze(config)
        assert analysis.outcome == FlightOutcome.CRASH
    
    def test_twr_greater_than_1_flight(self):
        """Test that TWR > 1.15 results in FLY."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=15000.0)  # TWR = 1.53
        engine = PhysicsEngine()
        
        analysis = engine.analyze(config)
        assert analysis.outcome == FlightOutcome.FLY
    
    def test_twr_near_1_hover(self):
        """Test that TWR ~ 1.0 results in HOVER."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=10500.0)  # TWR = 1.07
        engine = PhysicsEngine()
        
        analysis = engine.analyze(config)
        assert analysis.outcome == FlightOutcome.HOVER
    
    def test_stability_score_range(self):
        """Test that stability score is always 0-1."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=12000.0)
        engine = PhysicsEngine()
        
        stability = engine.calculate_stability(config)
        assert 0.0 <= stability <= 1.0
    
    def test_hover_efficiency_range(self):
        """Test that hover efficiency is always 0-1."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=12000.0)
        engine = PhysicsEngine()
        
        efficiency = engine.calculate_hover_efficiency(config)
        assert 0.0 <= efficiency <= 1.0
    
    def test_endurance_positive(self):
        """Test that endurance is positive for valid craft."""
        config = CraftConfig(
            mass_kg=1000.0,
            thrust_newtons=12000.0,
            max_power_kw=500.0,
            battery_capacity_kwh=50.0
        )
        engine = PhysicsEngine()
        
        endurance = engine.calculate_endurance(config)
        assert endurance > 0
    
    def test_anti_gravity_infinite_endurance(self):
        """Test that anti-gravity has infinite endurance."""
        config = CraftConfig(
            mass_kg=2000.0,
            thrust_newtons=20000.0,
            propulsion_type=PropulsionType.ANTI_GRAVITY,
            max_power_kw=0.0,
            battery_capacity_kwh=0.0
        )
        engine = PhysicsEngine()
        
        endurance = engine.calculate_endurance(config)
        assert endurance == float('inf')
    
    def test_anti_gravity_infinite_altitude(self):
        """Test that anti-gravity has unlimited altitude."""
        config = CraftConfig(
            mass_kg=2000.0,
            thrust_newtons=20000.0,
            propulsion_type=PropulsionType.ANTI_GRAVITY
        )
        engine = PhysicsEngine()
        
        max_alt = engine.calculate_max_altitude(config)
        assert max_alt == float('inf')
    
    def test_warnings_generated(self):
        """Test that warnings are generated for low TWR."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=7000.0)  # TWR = 0.714
        engine = PhysicsEngine()
        
        analysis = engine.analyze(config)
        assert len(analysis.warnings) > 0
        assert "CRITICAL" in analysis.warnings[0] or "WARNING" in analysis.warnings[0]
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated for low TWR."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=8000.0)  # TWR < 1
        engine = PhysicsEngine()
        
        analysis = engine.analyze(config)
        assert len(analysis.recommendations) > 0
    
    def test_seeded_reproducibility(self):
        """Test that same seed gives same results."""
        config = CraftConfig(mass_kg=1000.0, thrust_newtons=12000.0)
        
        engine1 = PhysicsEngine(seed=42)
        engine2 = PhysicsEngine(seed=42)
        
        analysis1 = engine1.analyze(config)
        analysis2 = engine2.analyze(config)
        
        assert analysis1.twr == analysis2.twr
        assert analysis1.stability_score == analysis2.stability_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
