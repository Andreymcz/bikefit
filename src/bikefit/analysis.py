"""Data class for storing analysis results."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Analysis:
    """Holds the results of a bike fit analysis session."""

    frame_count: int = 0
    """Total number of frames processed."""

    joints: Dict[int, Dict[str, Tuple[float, float, float]]] = field(default_factory=dict)
    """
    A dictionary where keys are frame numbers and values are dictionaries
    of joint data. The inner dictionary maps joint names (str) to a tuple
    of (x, y, visibility).
    """

    angles: Dict[int, Dict[str, float]] = field(default_factory=dict)
    """
    A dictionary where keys are frame numbers and values are dictionaries
    of angle data. The inner dictionary maps angle names (str) to their
    calculated values (float).
    """
