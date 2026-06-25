"""Portfolio bucket management.

Buckets represent investment time horizons. The bucket type determines:
- E2 exit threshold (consecutive BEAR emits before exit)
- Expected hold duration

Bucket assignment is caller-driven (e.g., from instrument metadata or user intent).
This module validates bucket types and provides the VALID_BUCKETS contract.
"""
from __future__ import annotations
from constants import E2_CONSECUTIVE_THRESHOLD

VALID_BUCKETS: frozenset[str] = frozenset(E2_CONSECUTIVE_THRESHOLD.keys())


def validate_bucket_type(bucket_type: str) -> str:
    """Return bucket_type if valid, raise ValueError if not.

    Valid values: 'near_term', 'medium_term', 'long_term'.
    """
    if bucket_type not in VALID_BUCKETS:
        raise ValueError(
            f"Unknown bucket type: {bucket_type!r}. "
            f"Must be one of: {sorted(VALID_BUCKETS)}"
        )
    return bucket_type


def e2_threshold(bucket_type: str) -> int:
    """Return the E2 consecutive-bear threshold for the given bucket."""
    validate_bucket_type(bucket_type)
    return E2_CONSECUTIVE_THRESHOLD[bucket_type]
