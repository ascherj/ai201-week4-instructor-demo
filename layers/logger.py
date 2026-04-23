"""
Moderation Logger
=================
Records every moderation decision with enough context to audit and
improve the system over time.

Demo talking point:
    "Logging is not optional in a production safety system. Without it
    you have no idea if your rules are calibrated correctly. Are you
    banning things that should be timeouts? Letting through things that
    should be flagged? The log is how you find out.

    In production this would write to a database. Here it writes to memory
    and lets you print a table at the end of the demo."
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ModerationEvent:
    timestamp: str
    user_id: str
    username: str
    message: str
    decision: str          # "allow", "timeout", "ban", "rate_limited"
    reason: str
    layer: str             # which layer made the decision
    confidence: str = ""   # "high", "medium", "low" — from LLM layer only


class ModerationLogger:
    """
    In-memory structured log of moderation decisions.
    Prints a formatted table for demo display.
    """

    def __init__(self):
        self._events: list[ModerationEvent] = []

    def log(
        self,
        user_id: str,
        username: str,
        message: str,
        decision: str,
        reason: str,
        layer: str,
        confidence: str = "",
    ):
        """Record a moderation decision."""
        self._events.append(ModerationEvent(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            user_id=user_id,
            username=username,
            message=message[:80] + ("..." if len(message) > 80 else ""),
            decision=decision,
            reason=reason,
            layer=layer,
            confidence=confidence,
        ))

    def print_log(self, last_n: int | None = None):
        """Print the moderation log as a formatted table."""
        events = self._events[-last_n:] if last_n else self._events
        if not events:
            print("  (no events logged yet)")
            return

        decision_icons = {
            "allow":        "✓",
            "timeout":      "⏱",
            "ban":          "✗",
            "rate_limited": "🚫",
        }

        print(f"\n{'Time':<10} {'User':<20} {'Decision':<12} {'Layer':<18} {'Reason'}")
        print("-" * 90)
        for e in events:
            icon = decision_icons.get(e.decision, "?")
            print(
                f"{e.timestamp:<10} "
                f"{e.username[:19]:<20} "
                f"{icon} {e.decision:<10} "
                f"{e.layer[:17]:<18} "
                f"{e.reason[:50]}"
            )
        print()

    def summary(self) -> dict:
        """Return counts by decision type."""
        counts: dict[str, int] = {}
        for e in self._events:
            counts[e.decision] = counts.get(e.decision, 0) + 1
        return counts

    def clear(self):
        """Reset the log — useful between demo scenarios."""
        self._events.clear()

    def __len__(self):
        return len(self._events)
