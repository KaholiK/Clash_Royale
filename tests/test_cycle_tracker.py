"""Tests for CardCycleTracker class."""

import pytest
from croverlay.cycle_tracker import CardCycleTracker, CardPlay


class TestCardPlay:
    """Tests for CardPlay dataclass."""

    def test_card_play_creation(self):
        """Test creating a CardPlay instance."""
        play = CardPlay(card_name="Knight", is_evolved=False, timestamp=1.5)
        assert play.card_name == "Knight"
        assert play.is_evolved is False
        assert play.timestamp == 1.5

    def test_card_play_evolved(self):
        """Test CardPlay with evolved card."""
        play = CardPlay(card_name="Barbarians", is_evolved=True, timestamp=10.0)
        assert play.card_name == "Barbarians"
        assert play.is_evolved is True
        assert play.timestamp == 10.0


class TestCardCycleTracker:
    """Tests for CardCycleTracker class."""

    def test_initialization(self):
        """Test tracker initializes with empty state."""
        tracker = CardCycleTracker()
        assert len(tracker.discovered_cards) == 0
        assert len(tracker.play_history) == 0
        assert tracker.get_discovered_deck() == []

    def test_record_single_play(self):
        """Test recording a single card play."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)

        assert len(tracker.discovered_cards) == 1
        assert "Knight" in tracker.discovered_cards
        assert len(tracker.play_history) == 1
        assert tracker.play_history[0].card_name == "Knight"
        assert tracker.play_history[0].is_evolved is False
        assert tracker.play_history[0].timestamp == 1.0

    def test_record_multiple_plays(self):
        """Test recording multiple card plays."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("Archers", False, 2.0)
        tracker.record_play("Fireball", False, 3.0)

        assert len(tracker.discovered_cards) == 3
        assert "Knight" in tracker.discovered_cards
        assert "Archers" in tracker.discovered_cards
        assert "Fireball" in tracker.discovered_cards
        assert len(tracker.play_history) == 3

    def test_record_same_card_twice(self):
        """Test recording the same card multiple times."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("Archers", False, 2.0)
        tracker.record_play("Knight", False, 3.0)

        # Should only have 2 unique cards
        assert len(tracker.discovered_cards) == 2
        # But 3 plays in history
        assert len(tracker.play_history) == 3
        assert tracker.play_history[0].card_name == "Knight"
        assert tracker.play_history[2].card_name == "Knight"

    def test_record_evolved_card(self):
        """Test recording an evolved card play."""
        tracker = CardCycleTracker()
        tracker.record_play("Barbarians", False, 1.0)
        tracker.record_play("Barbarians", False, 2.0)
        tracker.record_play("Barbarians", True, 3.0)

        assert len(tracker.discovered_cards) == 1
        assert len(tracker.play_history) == 3
        assert tracker.play_history[2].is_evolved is True

    def test_get_discovered_deck_sorted(self):
        """Test that discovered deck is returned sorted."""
        tracker = CardCycleTracker()
        tracker.record_play("Wizard", False, 1.0)
        tracker.record_play("Archers", False, 2.0)
        tracker.record_play("Knight", False, 3.0)

        deck = tracker.get_discovered_deck()
        assert deck == ["Archers", "Knight", "Wizard"]

    def test_get_discovered_deck_max_8(self):
        """Test that we can track up to 8 unique cards."""
        tracker = CardCycleTracker()
        cards = [
            "Knight",
            "Archers",
            "Fireball",
            "Log",
            "Hog Rider",
            "Musketeer",
            "Ice Spirit",
            "Cannon",
        ]

        for i, card in enumerate(cards):
            tracker.record_play(card, False, float(i))

        assert len(tracker.discovered_cards) == 8
        assert sorted(tracker.get_discovered_deck()) == sorted(cards)

    def test_get_inferred_hand_empty(self):
        """Test inferring hand with no plays."""
        tracker = CardCycleTracker()
        hand = tracker.get_inferred_hand()
        assert hand == []

    def test_get_inferred_hand_few_cards(self):
        """Test inferring hand with fewer than 4 cards discovered."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("Archers", False, 2.0)

        hand = tracker.get_inferred_hand()
        assert sorted(hand) == ["Archers", "Knight"]

    def test_get_inferred_hand_basic(self):
        """Test inferring hand with basic play sequence."""
        tracker = CardCycleTracker()
        # Play 4 cards in order
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("Archers", False, 2.0)
        tracker.record_play("Fireball", False, 3.0)
        tracker.record_play("Log", False, 4.0)

        # After playing all 4, the hand should contain the 4 cards
        # (since they were all played, we guess based on recency)
        hand = tracker.get_inferred_hand()
        assert len(hand) == 4
        assert set(hand) == {"Knight", "Archers", "Fireball", "Log"}

    def test_get_inferred_hand_with_cycle(self):
        """Test inferring hand after cards have cycled."""
        tracker = CardCycleTracker()
        # Discover 8 cards
        cards = [
            "Knight",
            "Archers",
            "Fireball",
            "Log",
            "Hog Rider",
            "Musketeer",
            "Ice Spirit",
            "Cannon",
        ]

        for i, card in enumerate(cards):
            tracker.record_play(card, False, float(i))

        # Play Knight again (it cycles back)
        tracker.record_play("Knight", False, 10.0)

        # Hand should be the 4 cards played least recently
        # Knight was just played at 10.0, so it should NOT be in hand
        # The 4 oldest plays are: Archers(2), Fireball(3), Log(4), Hog Rider(5)
        hand = tracker.get_inferred_hand()
        assert len(hand) == 4
        assert "Knight" not in hand
        assert "Archers" in hand

    def test_get_inferred_next_card_empty(self):
        """Test inferring next card with no plays."""
        tracker = CardCycleTracker()
        next_card = tracker.get_inferred_next_card()
        assert next_card is None

    def test_get_inferred_next_card_few_cards(self):
        """Test inferring next card with fewer than 5 cards."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("Archers", False, 2.0)
        tracker.record_play("Fireball", False, 3.0)
        tracker.record_play("Log", False, 4.0)

        next_card = tracker.get_inferred_next_card()
        assert next_card is None  # Need at least 5 cards

    def test_get_inferred_next_card_basic(self):
        """Test inferring next card with 8 cards discovered."""
        tracker = CardCycleTracker()
        # Discover 8 cards
        cards = [
            "Knight",
            "Archers",
            "Fireball",
            "Log",
            "Hog Rider",
            "Musketeer",
            "Ice Spirit",
            "Cannon",
        ]

        for i, card in enumerate(cards):
            tracker.record_play(card, False, float(i))

        # The next card should be the one played longest ago
        # that's not in the inferred hand
        # Hand contains 4 cards played least recently
        # Next card should be from the remaining 4, the one played earliest
        next_card = tracker.get_inferred_next_card()
        assert next_card is not None

        # After playing all 8 in order, the hand should be cards 0-3 (oldest)
        # and the next should be from cards 4-7, specifically card 4 (Hog Rider)
        hand = tracker.get_inferred_hand()
        assert next_card not in hand

    def test_get_inferred_next_card_after_cycle(self):
        """Test inferring next card after cards have cycled."""
        tracker = CardCycleTracker()
        cards = [
            "Knight",
            "Archers",
            "Fireball",
            "Log",
            "Hog Rider",
            "Musketeer",
            "Ice Spirit",
            "Cannon",
        ]

        # Initial plays
        for i, card in enumerate(cards):
            tracker.record_play(card, False, float(i))

        # Play some cards again
        tracker.record_play("Knight", False, 10.0)
        tracker.record_play("Archers", False, 11.0)

        next_card = tracker.get_inferred_next_card()
        assert next_card is not None

        # Next card should be one of the cards not recently played
        # and not in the current hand
        hand = tracker.get_inferred_hand()
        assert next_card not in hand

    def test_full_game_simulation(self):
        """Test a realistic game scenario."""
        tracker = CardCycleTracker()

        # Opponent plays their starting hand
        tracker.record_play("Knight", False, 1.0)
        assert len(tracker.discovered_cards) == 1

        tracker.record_play("Archers", False, 2.5)
        assert len(tracker.discovered_cards) == 2

        tracker.record_play("Fireball", False, 4.0)
        assert len(tracker.discovered_cards) == 3

        tracker.record_play("Log", False, 5.5)
        assert len(tracker.discovered_cards) == 4

        # Now we know 4 cards, more cards get revealed
        tracker.record_play("Hog Rider", False, 7.0)
        assert len(tracker.discovered_cards) == 5

        tracker.record_play("Musketeer", False, 9.0)
        tracker.record_play("Ice Spirit", False, 10.0)
        tracker.record_play("Cannon", False, 12.0)

        # All 8 cards discovered
        assert len(tracker.discovered_cards) == 8
        deck = tracker.get_discovered_deck()
        assert len(deck) == 8

        # Cards cycle back
        tracker.record_play("Knight", False, 15.0)
        tracker.record_play("Archers", False, 17.0)

        # Still 8 unique cards
        assert len(tracker.discovered_cards) == 8
        # But 10 plays
        assert len(tracker.play_history) == 10

        # Can still infer hand and next card
        hand = tracker.get_inferred_hand()
        assert len(hand) == 4

        next_card = tracker.get_inferred_next_card()
        assert next_card is not None
        assert next_card not in hand


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_timestamps_order(self):
        """Test that timestamps can be in any order (handles lag/delays)."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 5.0)
        tracker.record_play("Archers", False, 3.0)  # Out of order
        tracker.record_play("Fireball", False, 7.0)

        assert len(tracker.play_history) == 3
        # History maintains insertion order, not timestamp order
        assert tracker.play_history[0].timestamp == 5.0
        assert tracker.play_history[1].timestamp == 3.0

    def test_zero_timestamp(self):
        """Test that timestamp can be 0 (battle start)."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 0.0)
        assert tracker.play_history[0].timestamp == 0.0

    def test_negative_timestamp(self):
        """Test that negative timestamps are handled (if using relative times)."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, -1.0)
        assert tracker.play_history[0].timestamp == -1.0

    def test_duplicate_card_names(self):
        """Test that card names are case-sensitive."""
        tracker = CardCycleTracker()
        tracker.record_play("Knight", False, 1.0)
        tracker.record_play("knight", False, 2.0)  # Different case

        # Should treat as different cards
        assert len(tracker.discovered_cards) == 2

    def test_empty_card_name(self):
        """Test handling of empty card name."""
        tracker = CardCycleTracker()
        tracker.record_play("", False, 1.0)

        assert "" in tracker.discovered_cards
        assert len(tracker.discovered_cards) == 1

    def test_special_characters_in_card_name(self):
        """Test card names with special characters."""
        tracker = CardCycleTracker()
        tracker.record_play("Mini P.E.K.K.A", False, 1.0)

        assert "Mini P.E.K.K.A" in tracker.discovered_cards
