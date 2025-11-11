"""
elixir_tracker.py

Contains ElixirTracker class implementing opponent_elixir_model.
"""


class ElixirTracker:
    """
    Tracks opponent elixir based on time-based generation and card plays.

    Implements the opponent_elixir_model from cr_overlay_knowledge.json.
    """

    def __init__(
        self,
        single_seconds_per_elixir: float = 2.8,
        double_seconds_per_elixir: float = 1.4,
        triple_seconds_per_elixir: float = 0.9,
        max_elixir: float = 10.0,
    ):
        """
        Initialize the ElixirTracker.

        Args:
            single_seconds_per_elixir: Seconds to generate 1 elixir in single phase (default 2.8)
            double_seconds_per_elixir: Seconds to generate 1 elixir in double phase (default 1.4)
            triple_seconds_per_elixir: Seconds to generate 1 elixir in triple phase (default 0.9)
            max_elixir: Maximum elixir cap (default 10.0)
        """
        self.single_seconds_per_elixir = single_seconds_per_elixir
        self.double_seconds_per_elixir = double_seconds_per_elixir
        self.triple_seconds_per_elixir = triple_seconds_per_elixir
        self.max_elixir = max_elixir

        # State variables
        self.current_elixir = 0.0
        self.last_update_timestamp = None
        self.phase = "single"  # "single", "double", or "triple"

    def update_time(self, now_seconds: float) -> None:
        """
        Advance current_elixir based on time elapsed since last update.

        Args:
            now_seconds: Current timestamp in seconds (monotonic time)
        """
        if self.last_update_timestamp is not None:
            delta_t = now_seconds - self.last_update_timestamp

            # Determine seconds_per_elixir based on current phase
            if self.phase == "single":
                seconds_per_elixir = self.single_seconds_per_elixir
            elif self.phase == "double":
                seconds_per_elixir = self.double_seconds_per_elixir
            elif self.phase == "triple":
                seconds_per_elixir = self.triple_seconds_per_elixir
            else:
                # Default to single if phase is unknown
                seconds_per_elixir = self.single_seconds_per_elixir

            # Increase current_elixir
            elixir_gain = delta_t / seconds_per_elixir
            self.current_elixir = min(
                self.current_elixir + elixir_gain, self.max_elixir
            )

        self.last_update_timestamp = now_seconds

    def spend(self, cost: float) -> None:
        """
        Subtract elixir cost when a card is played.

        Args:
            cost: Elixir cost of the card played
        """
        self.current_elixir = max(0.0, self.current_elixir - cost)

    def set_single_elixir(self) -> None:
        """Switch to single elixir phase."""
        self.phase = "single"

    def set_double_elixir(self) -> None:
        """Switch to double elixir phase."""
        self.phase = "double"

    def set_triple_elixir(self) -> None:
        """Switch to triple elixir phase."""
        self.phase = "triple"

    def adjust(self, delta: float) -> None:
        """
        Manually adjust elixir (used for hotkey corrections).

        Args:
            delta: Amount to add/subtract from current_elixir (can be positive or negative)
        """
        self.current_elixir = max(
            0.0, min(self.current_elixir + delta, self.max_elixir)
        )
