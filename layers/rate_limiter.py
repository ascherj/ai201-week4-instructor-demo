"""
Rate Limiter (Sliding Window)
==============================
Tracks message frequency per user and flags when a user (or the server
as a whole) exceeds defined thresholds within a rolling time window.

Two thresholds:
    per_user  — how many messages one user can send per window
    server    — how many total messages the server can receive per window
                (used to detect raids: many different users spiking at once)

Demo talking point:
    "Rate limiting doesn't care about content — it only looks at frequency.
    It's the cheapest possible check: no API call, no LLM, just a counter.
    Run it first so the expensive layers only see messages that pass the
    basic volume check."

    During the raid simulation ask students:
    "Why would you rate-limit at the server level, not just per user?
    A coordinated raid uses many accounts — per-user limits alone won't catch it."
"""

import time
from collections import defaultdict, deque


class RateLimiter:
    """
    Sliding window rate limiter tracking per-user and server-wide message rates.

    Parameters
    ----------
    user_limit : int
        Max messages a single user can send within the window. Default: 5.
    server_limit : int
        Max total messages the server can receive within the window. Default: 30.
    window_seconds : int
        Size of the sliding time window in seconds. Default: 10.
    """

    def __init__(
        self,
        user_limit: int = 5,
        server_limit: int = 30,
        window_seconds: int = 10,
    ):
        self.user_limit = user_limit
        self.server_limit = server_limit
        self.window_seconds = window_seconds

        # Maps user_id → deque of message timestamps within the window
        self._user_windows: dict[str, deque] = defaultdict(deque)
        # Server-wide message timestamps
        self._server_window: deque = deque()

    def _prune(self, window: deque, now: float):
        """Remove timestamps older than the current window."""
        cutoff = now - self.window_seconds
        while window and window[0] < cutoff:
            window.popleft()

    def check(self, user_id: str) -> dict:
        """
        Record a message and check whether it exceeds rate limits.

        Parameters
        ----------
        user_id : str
            The ID of the user sending the message.

        Returns
        -------
        dict with keys:
            allowed : bool        — False if any limit is exceeded
            reason  : str | None  — which limit fired, or None if allowed
            user_count   : int    — messages this user sent in the current window
            server_count : int    — total server messages in the current window
        """
        now = time.time()

        user_window = self._user_windows[user_id]
        self._prune(user_window, now)
        self._prune(self._server_window, now)

        user_count   = len(user_window)
        server_count = len(self._server_window)

        # Check limits BEFORE recording — so the message that tips it is also blocked
        if user_count >= self.user_limit:
            return {
                "allowed": False,
                "reason": f"user rate limit exceeded ({user_count}/{self.user_limit} msgs in {self.window_seconds}s)",
                "user_count": user_count,
                "server_count": server_count,
            }

        if server_count >= self.server_limit:
            return {
                "allowed": False,
                "reason": f"server rate limit exceeded ({server_count}/{self.server_limit} msgs in {self.window_seconds}s) — possible raid",
                "user_count": user_count,
                "server_count": server_count,
            }

        # Record the message
        user_window.append(now)
        self._server_window.append(now)

        return {
            "allowed": True,
            "reason": None,
            "user_count": user_count + 1,
            "server_count": server_count + 1,
        }

    def reset(self):
        """Clear all rate limit state — useful between demo scenarios."""
        self._user_windows.clear()
        self._server_window.clear()

    def stats(self) -> dict:
        """Return current window counts for display."""
        now = time.time()
        self._prune(self._server_window, now)
        return {
            "server_messages_in_window": len(self._server_window),
            "active_users": len(self._user_windows),
            "window_seconds": self.window_seconds,
        }
