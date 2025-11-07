"""
Valiqor Trace SDK

Public tracing SDK for AI workflow demos.
No network calls, no external services - pure local tracing.
"""

__version__ = "1.0.0"
__author__ = "Valiqor Team"

from .context_scanner import scan_repo
from .trace import Trace

__all__ = ["Trace", "scan_repo"]
