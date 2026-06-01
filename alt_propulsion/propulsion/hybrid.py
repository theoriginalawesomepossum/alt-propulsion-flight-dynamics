"""
Hybrid propulsion system (mix & match multiple types).
"""

from typing import List, Dict, Any
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.enums import PropulsionType
from alt_propulsion.propulsion.base import PropulsionModule


class HybridPropulsion:
    """
    Hybrid propulsion combining multiple propulsion types.
    
    Example: VTOL (70%) + Ion Thruster (30%)
    """
    
    def __init__(self, modules: List[Dict[str, Any]]):
        """
        Initialize hybrid propulsion.
        
        Args:
            modules: List of {"type": PropulsionType, "weight": float} dicts
                     Weights must sum to 1.0
        """
        self.modules = modules
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate weights sum to 1.0."""
        total = sum(m["weight"] for m in self.modules)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Hybrid weights must sum to 1.0, got {total}")
    
    def thrust_model(self, config: CraftConfig, env: Dict[str, Any]) -> float:
        """Weighted sum of thrust from all modules."""
        total_thrust = 0.0
        for module in self.modules:
            prop_type = module["type"]
            weight = module["weight"]
            
            # Use propulsion type's inherent thrust modifier
            thrust_mod = prop_type.efficiency_modifier
            total_thrust += config.thrust_newtons * thrust_mod * weight
        
        return total_thrust
    
    def efficiency_model(self, config: CraftConfig, env: Dict[str, Any]) -> float:
        """Weighted sum of efficiencies."""
        total_eff = 0.0
        for module in self.modules:
            prop_type = module["type"]
            weight = module["weight"]
            total_eff += prop_type.efficiency_modifier * weight
        
        return total_eff
    
    def stability_modifier(self, config: CraftConfig) -> float:
        """Weighted sum of stability modifiers."""
        total_stab = 0.0
        for module in self.modules:
            prop_type = module["type"]
            weight = module["weight"]
            total_stab += prop_type.stability_modifier * weight
        
        return total_stab
    
    def power_consumption(self, config: CraftConfig, throttle: float) -> float:
        """Weighted sum of power consumption."""
        total_power = 0.0
        for module in self.modules:
            prop_type = module["type"]
            weight = module["weight"]
            # Rough estimate: power ∝ throttle × efficiency
            total_power += config.max_power_kw * throttle * prop_type.efficiency_modifier * weight
        
        return total_power
    
    def __str__(self) -> str:
        parts = [f"{m['type'].name} ({m['weight']*100:.0f}%)" for m in self.modules]
        return f"HybridPropulsion({', '.join(parts)})"
