from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PatternRuleConfig:
    """
    Configuration for deterministic fraud-pattern evaluation.

    Values marked as unverified must not be treated as authoritative
    fraud rules until they are confirmed from the challenge dataset,
    README, policy, or other authoritative source.
    """

    # Pattern 1: Card Testing
    P1_MIN_AUTHS: int = 3
    P1_TIME_WINDOW_HOURS: int = 1

    # The exact dollar threshold is currently unverified.
    # None means Pattern 1 cannot be fully evaluated.
    P1_SMALL_AUTH_THRESHOLD: Optional[float] = None

    # Pattern 2 / Pattern 3: Card-not-present velocity
    P2_TIME_WINDOW_HOURS: int = 48
    P2_BURST_MIN: int = 2
    P2_BURST_MAX: int = 4

    # Pattern 5: Account takeover
    # Exact timeframe is currently unverified.
    P5_MIXED_CHANNEL_HOURS: Optional[int] = None
