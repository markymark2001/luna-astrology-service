"""Infrastructure constants for astrology runtime behavior and monitoring."""

# Queue-wait threshold for warning about astrology compute backlog.
# 250ms is long enough to filter out normal scheduling noise while still
# surfacing real queueing before users see large latency spikes.
ASTROLOGY_COMPUTE_QUEUE_WARNING_MS = 250.0

# End-to-end latency threshold for warning about slow astrology compute tasks.
# 4000ms flags requests trending toward the backend's context timeout budget.
ASTROLOGY_COMPUTE_TOTAL_WARNING_MS = 4000.0

# Cooldown between repeated Sentry warnings for the same task and signal type.
# Limits alert volume while preserving visibility into sustained pressure.
ASTROLOGY_COMPUTE_WARNING_COOLDOWN_SECONDS = 300.0
