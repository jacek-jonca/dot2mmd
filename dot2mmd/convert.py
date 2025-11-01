from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple

try:
import pydot # type: ignore
_HAS_PYDOT = True
except Exception:
pydot = None
_HAS_PYDOT = False

__all__ = ["dot_to_mermaid"]
