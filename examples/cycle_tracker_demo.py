#!/usr/bin/env python3
"""
Example usage of CardCycleTracker.

This demonstrates how to use the CardCycleTracker class to track
opponent card plays in a Clash Royale match.
"""

from croverlay.cycle_tracker import CardCycleTracker


def main():
    print("=== CardCycleTracker Example Usage ===\n")

    # Create a tracker
    tracker = CardCycleTracker()

    # Simulate a sequence of card plays during a match
    print("Simulating opponent card plays...\n")

    # Opponent plays their starting hand
    plays = [
        ("Knight", False, 1.0),
        ("Archers", False, 2.5),
        ("Fireball", False, 4.0),
        ("Log", False, 5.5),
        ("Hog Rider", False, 7.0),
        ("Musketeer", False, 9.0),
        ("Ice Spirit", False, 10.0),
        ("Cannon", False, 12.0),
        # Cards cycling back
        ("Knight", False, 15.0),
        ("Archers", False, 17.0),
        ("Hog Rider", False, 19.0),
    ]

    for card_name, is_evolved, timestamp in plays:
        tracker.record_play(card_name, is_evolved, timestamp)
        print(f"[{timestamp:5.1f}s] Opponent played: {card_name}")

        # Show current knowledge
        discovered = tracker.get_discovered_deck()
        print(f"  Discovered cards ({len(discovered)}/8): {discovered}")

        if len(discovered) >= 4:
            hand = tracker.get_inferred_hand()
            print(f"  Inferred hand: {hand}")

        if len(discovered) >= 5:
            next_card = tracker.get_inferred_next_card()
            print(f"  Likely next card: {next_card}")

        print()

    print("\n=== Final Summary ===")
    print(f"Total discovered cards: {len(tracker.discovered_cards)}/8")
    print(f"Discovered deck: {tracker.get_discovered_deck()}")
    print(f"Total plays recorded: {len(tracker.play_history)}")
    print(f"Current inferred hand: {tracker.get_inferred_hand()}")
    print(f"Likely next card: {tracker.get_inferred_next_card()}")


if __name__ == "__main__":
    main()
