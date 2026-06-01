"""
Base class for propulsion modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from alt_propulsion.models.craft_config import CraftConfig


class PropulsionModule(ABC):
    """
    Abstract base class for all propulsion systems.
    
    Each propulsion type implements its own physics model.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return propulsion name."""
        pass
    
    @property
    @abstractmethod
    def is_speculative(self) -> bool:
        """Return True if speculative/experimental."""
        pass
    
    @abstractmethod
    def thrust_model(self, config: CraftConfig, env: Dict[str, Any]) -> float:
        """
        Calculate thrust given config and environment.
        
        Returns:
            Thrust in Newtons
        """
        pass
    
    @abstractmethod
    def efficiency_model(self, config: CraftConfig, env: Dict[str, Any]) -> float:
        """
        Calculate efficiency (0-1).
        
        Returns:
            Efficiency
        """
        pass
    
    @abstractmethod
    def stability_modifier(self, config: CraftConfig) -> float:
        """
        Return stability modifier (0-1).
        
        Returns:
            Stability modifier
        """
        pass
    
    @abstractmethod
    def power_consumption(self, config: CraftConfig, throttle: float) -> float:
        """
        Calculate power consumption.
        
        Args:
            throttle: Throttle level (0-1)
        
        Returns:
            Power in kW
        """
        pass
