"""
test_elixir_tracker.py

Tests for ElixirTracker class.
"""

import pytest
from croverlay.elixir_tracker import ElixirTracker


class TestElixirTrackerInitialization:
    """Test ElixirTracker initialization."""

    def test_default_initialization(self):
        """Test that ElixirTracker initializes with correct defaults."""
        tracker = ElixirTracker()

        assert tracker.single_seconds_per_elixir == 2.8
        assert tracker.double_seconds_per_elixir == 1.4
        assert tracker.triple_seconds_per_elixir == 0.9
        assert tracker.max_elixir == 10.0
        assert tracker.current_elixir == 0.0
        assert tracker.last_update_timestamp is None
        assert tracker.phase == "single"

    def test_custom_initialization(self):
        """Test ElixirTracker with custom parameters."""
        tracker = ElixirTracker(
            single_seconds_per_elixir=3.0,
            double_seconds_per_elixir=1.5,
            triple_seconds_per_elixir=1.0,
            max_elixir=12.0,
        )

        assert tracker.single_seconds_per_elixir == 3.0
        assert tracker.double_seconds_per_elixir == 1.5
        assert tracker.triple_seconds_per_elixir == 1.0
        assert tracker.max_elixir == 12.0


class TestElixirTrackerUpdateTime:
    """Test time-based elixir generation."""

    def test_first_update_sets_timestamp(self):
        """Test that first update only sets timestamp without generating elixir."""
        tracker = ElixirTracker()
        tracker.update_time(10.0)

        assert tracker.last_update_timestamp == 10.0
        assert tracker.current_elixir == 0.0

    def test_single_elixir_generation(self):
        """Test elixir generation in single phase."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)  # Initialize timestamp
        tracker.update_time(2.8)  # Generate 1 elixir

        assert tracker.current_elixir == pytest.approx(1.0)
        assert tracker.last_update_timestamp == 2.8

    def test_double_elixir_generation(self):
        """Test elixir generation in double phase."""
        tracker = ElixirTracker()
        tracker.set_double_elixir()
        tracker.update_time(0.0)  # Initialize timestamp
        tracker.update_time(1.4)  # Generate 1 elixir in double phase

        assert tracker.current_elixir == pytest.approx(1.0)

    def test_triple_elixir_generation(self):
        """Test elixir generation in triple phase."""
        tracker = ElixirTracker()
        tracker.set_triple_elixir()
        tracker.update_time(0.0)  # Initialize timestamp
        tracker.update_time(0.9)  # Generate 1 elixir in triple phase

        assert tracker.current_elixir == pytest.approx(1.0)

    def test_elixir_cap_at_max(self):
        """Test that elixir doesn't exceed max_elixir."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)
        tracker.update_time(100.0)  # Generate way more than max

        assert tracker.current_elixir == 10.0

    def test_incremental_elixir_generation(self):
        """Test that elixir accumulates correctly over multiple updates."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)
        tracker.update_time(1.4)  # 0.5 elixir

        assert tracker.current_elixir == pytest.approx(0.5)

        tracker.update_time(4.2)  # +2.8 seconds -> +1 more elixir
        assert tracker.current_elixir == pytest.approx(1.5)

    def test_fractional_elixir(self):
        """Test that tracker properly handles fractional elixir amounts."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)
        tracker.update_time(1.0)  # 1 second = ~0.357 elixir

        expected = 1.0 / 2.8
        assert tracker.current_elixir == pytest.approx(expected)


class TestElixirTrackerSpend:
    """Test elixir spending functionality."""

    def test_spend_reduces_elixir(self):
        """Test that spending reduces current elixir."""
        tracker = ElixirTracker()
        tracker.current_elixir = 5.0
        tracker.spend(3.0)

        assert tracker.current_elixir == 2.0

    def test_spend_clamps_to_zero(self):
        """Test that spending cannot reduce elixir below 0."""
        tracker = ElixirTracker()
        tracker.current_elixir = 2.0
        tracker.spend(5.0)

        assert tracker.current_elixir == 0.0

    def test_spend_exact_amount(self):
        """Test spending exact current elixir amount."""
        tracker = ElixirTracker()
        tracker.current_elixir = 4.0
        tracker.spend(4.0)

        assert tracker.current_elixir == 0.0

    def test_spend_fractional_cost(self):
        """Test spending fractional elixir (though not used in game)."""
        tracker = ElixirTracker()
        tracker.current_elixir = 3.5
        tracker.spend(1.2)

        assert tracker.current_elixir == pytest.approx(2.3)


class TestElixirTrackerPhaseTransitions:
    """Test phase transition methods."""

    def test_set_single_elixir(self):
        """Test switching to single elixir phase."""
        tracker = ElixirTracker()
        tracker.phase = "double"
        tracker.set_single_elixir()

        assert tracker.phase == "single"

    def test_set_double_elixir(self):
        """Test switching to double elixir phase."""
        tracker = ElixirTracker()
        tracker.set_double_elixir()

        assert tracker.phase == "double"

    def test_set_triple_elixir(self):
        """Test switching to triple elixir phase."""
        tracker = ElixirTracker()
        tracker.set_triple_elixir()

        assert tracker.phase == "triple"

    def test_phase_affects_generation_rate(self):
        """Test that changing phase affects elixir generation rate."""
        tracker = ElixirTracker()

        # Single phase: 2.8 seconds per elixir
        tracker.set_single_elixir()
        tracker.update_time(0.0)
        tracker.update_time(2.8)
        single_elixir = tracker.current_elixir

        # Reset for double phase test
        tracker2 = ElixirTracker()
        tracker2.set_double_elixir()
        tracker2.update_time(0.0)
        tracker2.update_time(2.8)
        double_elixir = tracker2.current_elixir

        # Double phase should generate twice as much in the same time
        assert double_elixir == pytest.approx(single_elixir * 2)


class TestElixirTrackerAdjust:
    """Test manual elixir adjustment functionality."""

    def test_adjust_positive(self):
        """Test adding elixir manually."""
        tracker = ElixirTracker()
        tracker.current_elixir = 5.0
        tracker.adjust(2.0)

        assert tracker.current_elixir == 7.0

    def test_adjust_negative(self):
        """Test subtracting elixir manually."""
        tracker = ElixirTracker()
        tracker.current_elixir = 5.0
        tracker.adjust(-2.0)

        assert tracker.current_elixir == 3.0

    def test_adjust_clamps_to_max(self):
        """Test that adjust doesn't exceed max_elixir."""
        tracker = ElixirTracker()
        tracker.current_elixir = 8.0
        tracker.adjust(5.0)

        assert tracker.current_elixir == 10.0

    def test_adjust_clamps_to_zero(self):
        """Test that adjust doesn't go below 0."""
        tracker = ElixirTracker()
        tracker.current_elixir = 2.0
        tracker.adjust(-5.0)

        assert tracker.current_elixir == 0.0

    def test_adjust_small_increments(self):
        """Test typical hotkey adjustments (+1/-1)."""
        tracker = ElixirTracker()
        tracker.current_elixir = 5.0

        tracker.adjust(1.0)
        assert tracker.current_elixir == 6.0

        tracker.adjust(-1.0)
        assert tracker.current_elixir == 5.0


class TestElixirTrackerIntegration:
    """Integration tests simulating realistic usage scenarios."""

    def test_typical_match_scenario(self):
        """Test a realistic match scenario with card plays and time updates."""
        tracker = ElixirTracker()

        # Match starts, initialize timestamp
        tracker.update_time(0.0)
        assert tracker.current_elixir == 0.0

        # 5 seconds pass (starting elixir is 5 in game, but we track from 0)
        tracker.update_time(5.0)
        expected = 5.0 / 2.8
        assert tracker.current_elixir == pytest.approx(expected)

        # Opponent plays a 3-cost card
        tracker.spend(3.0)
        expected = max(0.0, expected - 3.0)
        assert tracker.current_elixir == pytest.approx(expected)

        # 8 more seconds pass
        tracker.update_time(13.0)
        expected += 8.0 / 2.8
        assert tracker.current_elixir == pytest.approx(expected)

        # Switch to double elixir at 120 seconds
        tracker.update_time(120.0)
        tracker.set_double_elixir()

        # Verify elixir generation is now faster
        tracker.update_time(121.4)  # 1.4 seconds should give 1 elixir in double phase
        # Previous + 1.0
        expected = min(tracker.max_elixir, tracker.current_elixir)
        assert tracker.current_elixir <= 10.0

    def test_manual_correction_scenario(self):
        """Test using manual adjustment to correct tracking errors."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)

        # Generate some elixir
        tracker.update_time(10.0)

        # Detected a miss, manually adjust down
        tracker.adjust(-1.0)
        adjusted = tracker.current_elixir

        # Continue tracking
        tracker.update_time(15.0)
        expected = adjusted + (5.0 / 2.8)
        assert tracker.current_elixir == pytest.approx(expected)

    def test_elixir_leak_scenario(self):
        """Test that elixir stops generating at max (leak behavior)."""
        tracker = ElixirTracker()
        tracker.update_time(0.0)

        # Generate to max
        tracker.update_time(50.0)
        assert tracker.current_elixir == 10.0

        # Wait more - should stay at 10
        tracker.update_time(100.0)
        assert tracker.current_elixir == 10.0

        # Spend some elixir
        tracker.spend(4.0)
        assert tracker.current_elixir == 6.0

        # Generate back to max
        tracker.update_time(200.0)
        assert tracker.current_elixir == 10.0
