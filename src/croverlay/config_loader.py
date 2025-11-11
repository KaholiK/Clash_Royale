"""
config_loader.py

Loads and validates the cr_overlay_knowledge.json knowledge file.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ElixirTiming:
    """Data class for elixir timing information."""

    single_seconds_per_elixir: float
    double_seconds_per_elixir: float
    triple_seconds_per_elixir: float


class ConfigLoader:
    """Loads and exposes game configuration from cr_overlay_knowledge.json."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the config loader.

        Args:
            config_path: Optional path to the JSON file. If None, looks for
                        cr_overlay_knowledge.json in the project root.
        """
        if config_path is None:
            # Find project root by looking for cr_overlay_knowledge.json
            current = Path(__file__).resolve()
            # Navigate up from src/croverlay/config_loader.py to project root
            project_root = current.parent.parent.parent
            config_path = project_root / "cr_overlay_knowledge.json"

        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._validate_schema()

    def _load_config(self) -> dict:
        """Load the JSON configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _validate_schema(self) -> None:
        """Perform minimal schema validation."""
        # Check for required top-level keys
        required_keys = ["cards", "game_mechanics"]
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required key in config: {key}")

        # Check for required nested keys
        if "cards_by_elixir" not in self._config["cards"]:
            raise ValueError("Missing 'cards_by_elixir' in cards section")

        if "evolution_cycles" not in self._config["cards"]:
            raise ValueError("Missing 'evolution_cycles' in cards section")

        if "elixir" not in self._config["game_mechanics"]:
            raise ValueError("Missing 'elixir' in game_mechanics section")

        # Validate elixir timing structure
        elixir = self._config["game_mechanics"]["elixir"]
        required_elixir_keys = ["single_elixir", "double_elixir", "triple_elixir"]
        for key in required_elixir_keys:
            if key not in elixir:
                raise ValueError(f"Missing '{key}' in elixir section")

    def get_cards_by_elixir(self) -> dict[int, list[str]]:
        """
        Get cards organized by their elixir cost.

        Returns:
            Dictionary mapping elixir cost (int) to list of card names (str).
            Example: {1: ['Skeletons', 'Ice Spirit'], 2: ['Zap', 'Log'], ...}
        """
        cards_by_elixir_raw = self._config["cards"]["cards_by_elixir"]
        # Convert string keys to integers
        return {int(cost): cards for cost, cards in cards_by_elixir_raw.items()}

    def get_evolution_cycles(self) -> dict[str, int]:
        """
        Get evolution cycle information for cards.

        Returns:
            Dictionary mapping card name (str) to number of cycles (int).
            Example: {'Barbarians': 1, 'Firecracker': 2, ...}
        """
        return self._config["cards"]["evolution_cycles"].copy()

    def get_elixir_timing(self) -> ElixirTiming:
        """
        Get elixir timing information for different game phases.

        Returns:
            ElixirTiming data class with single/double/triple elixir timings
            in seconds per elixir.
        """
        elixir = self._config["game_mechanics"]["elixir"]

        return ElixirTiming(
            single_seconds_per_elixir=elixir["single_elixir"][
                "exact_seconds_per_elixir"
            ],
            double_seconds_per_elixir=elixir["double_elixir"][
                "exact_seconds_per_elixir"
            ],
            triple_seconds_per_elixir=elixir["triple_elixir"][
                "exact_seconds_per_elixir"
            ],
        )
