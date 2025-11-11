"""
cycle_tracker.py

Contains CardCycleTracker implementing opponent_card_cycle_model.
"""

from dataclasses import dataclass
from typing import List, Set, Optional


@dataclass
class CardPlay:
    """Represents a single card play event."""

    card_name: str
    is_evolved: bool
    timestamp: float


class CardCycleTracker:
    """
    Tracks opponent card cycle following tracking_logic.opponent_card_cycle_model.

    Maintains:
    - discovered_cards: set of card names seen so far (max 8)
    - play_history: ordered list of card plays with timestamps and evolved flag

    Provides methods to infer current hand and next card based on play history.
    Assumes 8-card deck and 4-card hand with no other game-specific assumptions.
    """

    def __init__(self):
        """Initialize an empty CardCycleTracker."""
        self.discovered_cards: Set[str] = set()
        self.play_history: List[CardPlay] = []

    def record_play(self, card_name: str, is_evolved: bool, t: float) -> None:
        """
        Record a card play by the opponent.

        Args:
            card_name: Name of the card played
            is_evolved: Whether the card was evolved
            t: Timestamp of the play (monotonic time in seconds)
        """
        # Append to play history
        self.play_history.append(
            CardPlay(card_name=card_name, is_evolved=is_evolved, timestamp=t)
        )

        # Add to discovered cards if not already present
        if card_name not in self.discovered_cards:
            self.discovered_cards.add(card_name)

    def get_discovered_deck(self) -> List[str]:
        """
        Return the list of discovered cards.

        Returns:
            List of discovered card names (up to 8)
        """
        return sorted(list(self.discovered_cards))

    def get_inferred_hand(self) -> List[str]:
        """
        Return a rough guess for the opponent's current hand (4 cards).

        Uses a simple heuristic:
        - After a card is played, it goes to the back of the deck
        - The hand contains the 4 cards that haven't been played most recently
        - If fewer than 4 distinct cards are known, returns what we know

        Returns:
            List of card names likely in hand (up to 4)
        """
        if not self.play_history:
            # No plays yet, no inference possible
            return []

        if len(self.discovered_cards) < 4:
            # Not enough cards discovered to fill a hand
            return sorted(list(self.discovered_cards))

        # Track when each card was last played
        last_play_time = {}
        for play in self.play_history:
            last_play_time[play.card_name] = play.timestamp

        # Cards that were played least recently are more likely to be in hand
        # Sort by last play time (oldest first = most likely in hand)
        cards_by_recency = sorted(
            self.discovered_cards,
            key=lambda card: last_play_time.get(card, float("-inf")),
        )

        # Return the 4 cards played least recently
        return cards_by_recency[:4]

    def get_inferred_next_card(self) -> Optional[str]:
        """
        Return a rough guess for the next card to be drawn.

        Uses a simple heuristic:
        - The next card is likely the one that was played longest ago
        - and is not currently in the inferred hand

        Returns:
            Card name most likely to be drawn next, or None if not enough data
        """
        if not self.play_history:
            return None

        if len(self.discovered_cards) < 5:
            # Need at least 5 cards to have something outside the hand
            return None

        inferred_hand = self.get_inferred_hand()

        # Track when each card was last played
        last_play_time = {}
        for play in self.play_history:
            last_play_time[play.card_name] = play.timestamp

        # Find cards not in hand
        cards_not_in_hand = [
            card for card in self.discovered_cards if card not in inferred_hand
        ]

        if not cards_not_in_hand:
            return None

        # The next card is likely the one played least recently among cards not in hand
        next_card = min(
            cards_not_in_hand, key=lambda card: last_play_time.get(card, float("-inf"))
        )

        return next_card
