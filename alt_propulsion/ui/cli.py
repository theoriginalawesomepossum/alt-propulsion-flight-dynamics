"""
CLI with auto-detect interactive/non-interactive mode.
"""

import sys
import math
from typing import Optional
from alt_propulsion.models.craft_config import CraftConfig
from alt_propulsion.models.flight_analysis import FlightAnalysis
from alt_propulsion.models.enums import PropulsionType, FlightOutcome, TestPhase
from alt_propulsion.core.physics import PhysicsEngine
from alt_propulsion.core.modes import ModeDetector
from alt_propulsion.presets.demo_presets import get_demo_presets


class CLI:
    """Command-line interface with auto-detection."""
    
    def __init__(self):
        self.mode_detector = ModeDetector()
        self.mode = self.mode_detector.get_mode()
    
    def run(self):
        """Run CLI with auto-detection."""
        if self.mode == "interactive":
            self.run_interactive()
        else:
            self.run_batch()
    
    def run_interactive(self):
        """Run interactive mode with menus."""
        print("\n" + "=" * 70)
        print("  ALT-PROPULSION FLIGHT DYNAMICS ANALYZER v3.0")
        print("  Engineering-Grade Simulator for Scientists & Engineers")
        print("=" * 70)
        
        # Select mode
        print("\nSelect mode:")
        print("  1. Interactive Analysis (custom craft)")
        print("  2. Demo Presets (pre-configured examples)")
        print("  3. Exit")
        
        try:
            choice = input("Select mode [1]: ").strip() or "1"
            choice = int(choice)
        except (ValueError, EOFError):
            choice = 1
        
        if choice == 1:
            self.run_custom_craft()
        elif choice == 2:
            self.run_demo_presets()
        else:
            print("Goodbye!")
            return
        
        # Ask to continue
        try:
            again = input("\nAnalyze another? (y/n): ").strip().lower()
            if again in ('y', 'yes'):
                self.run()
        except EOFError:
            pass
    
    def run_batch(self):
        """Run batch mode (no prompts)."""
        print("\n" + "=" * 70)
        print("  ALT-PROPULSION FLIGHT DYNAMICS ANALYZER v3.0")
        print("  Batch Mode (Non-Interactive)")
        print("=" * 70)
        
        # Run all demo presets
        self.run_demo_presets()
    
    def run_custom_craft(self):
        """Run interactive custom craft configuration."""
        print("\n--- Propulsion Type ---")
        types = list(PropulsionType)
        for i, pt in enumerate(types[:10], 1):  # Show first 10
            print(f"  {i}. {pt.value}")
        if len(types) > 10:
            print(f"  ... and {len(types) - 10} more")
        
        try:
            choice = input("Select propulsion type [1]: ").strip() or "1"
            idx = int(choice) - 1
            prop_type = types[idx] if 0 <= idx < len(types) else PropulsionType.VTOL
        except (ValueError, IndexError, EOFError):
            prop_type = PropulsionType.VTOL
        
        # Get parameters with defaults
        print("\n--- Physical Parameters ---")
        try:
            mass = float(input("Craft mass (kg) [1000.0]: ").strip() or "1000")
            thrust = float(input("Total thrust (N) [12000.0]: ").strip() or "12000")
        except (ValueError, EOFError):
            mass, thrust = 1000.0, 12000.0
        
        # Create config
        config = CraftConfig(
            mass_kg=mass,
            thrust_newtons=thrust,
            propulsion_type=prop_type
        )
        
        # Analyze
        engine = PhysicsEngine()
        analysis = engine.analyze(config)
        
        # Display
        self.display_outcome(analysis)
    
    def run_demo_presets(self):
        """Run demo presets."""
        presets = get_demo_presets()
        
        for name, config in presets:
            print(f"\n{'─' * 60}")
            print(f"  CONFIG: {name}")
            print(f"  Type: {config.propulsion_type.value}")
            print(f"  Mass: {config.mass_kg} kg | Thrust: {config.thrust_newtons} N")
            print(f"{'─' * 60}")
            
            engine = PhysicsEngine()
            analysis = engine.analyze(config)
            self.display_outcome(analysis)
    
    def display_outcome(self, analysis: FlightAnalysis):
        """Display analysis results."""
        print("\n" + "=" * 60)
        print("         FLIGHT DYNAMICS ANALYSIS RESULTS")
        print("=" * 60)
        
        outcome_str = f"{analysis.outcome_emoji} {analysis.outcome.name}"
        print(f"\n  OUTCOME: {outcome_str}")
        print(f"  {'─' * 50}")
        
        print(f"  Thrust-to-Weight Ratio:  {analysis.twr:.3f}")
        print(f"  Stability Score:         {analysis.stability_score:.1%}")
        print(f"  Hover Efficiency:        {analysis.hover_efficiency:.1%}")
        print(f"  Max Altitude:            {analysis.max_altitude_formatted}")
        print(f"  Endurance:               {analysis.endurance_formatted}")
        print(f"  Climb Rate:              {analysis.climb_rate_ms:.1f} m/s")
        print(f"  Thermal Margin:          {analysis.thermal_margin:.1%}")
        print(f"  Structural Margin:       {analysis.structural_margin:.1%}")
        
        if analysis.warnings:
            print(f"\n  ⚠️  WARNINGS:")
            for w in analysis.warnings:
                print(f"     • {w}")
        
        if analysis.recommendations:
            print(f"\n  💡 RECOMMENDATIONS:")
            for r in analysis.recommendations:
                print(f"     • {r}")
        
        print("=" * 60 + "\n")


def main():
    """Main entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
