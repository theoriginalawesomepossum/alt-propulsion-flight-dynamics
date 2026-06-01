"""
Mode detection for interactive/non-interactive execution.
"""

import sys
import os
from typing import Literal


class ModeDetector:
    """
    Automatically detects execution mode and configures behavior.
    
    Modes:
    - interactive: Terminal with stdin pipe (TTY)
    - batch: No stdin pipe (redirected, CI, automation)
    - api: Called as library (no CLI)
    """
    
    def is_tty(self) -> bool:
        """Check if stdin is a TTY (terminal)."""
        return sys.stdin.isatty()
    
    def is_ci(self) -> bool:
        """Check if running in CI/CD environment."""
        ci_vars = ['GITHUB_ACTIONS', 'TRAVIS', 'CIRCLECI', 'JENKINS_URL', 'GITLAB_CI']
        return any(os.environ.get(var) for var in ci_vars)
    
    def get_mode(self) -> Literal["interactive", "batch", "api"]:
        """
        Detect execution mode.
        
        Returns:
            "interactive" if TTY
            "batch" if no TTY or CI
            "api" if explicitly called as library
        """
        if self.is_ci():
            return "batch"
        
        if self.is_tty():
            return "interactive"
        
        return "batch"
    
    def should_show_menu(self) -> bool:
        """Return True if menu/prompting is appropriate."""
        return self.get_mode() == "interactive"
    
    def auto_fallback(self):
        """
        Auto-fallback configuration.
        
        If not interactive, set up for batch mode.
        """
        mode = self.get_mode()
        if mode != "interactive":
            # Suppress prompts, use defaults
            os.environ['ALT_PROPULSION_BATCH'] = 'true'
        
        return mode
    
    def __str__(self) -> str:
        return f"ModeDetector(mode={self.get_mode()})"
