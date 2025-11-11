"""Tests for config_loader module."""

import json
import pytest
from pathlib import Path
from croverlay.config_loader import ConfigLoader, ElixirTiming


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def config_path(project_root):
    """Get path to the config file."""
    return project_root / "cr_overlay_knowledge.json"


@pytest.fixture
def config_loader(config_path):
    """Create a ConfigLoader instance."""
    return ConfigLoader(config_path)


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_init_with_default_path(self):
        """Test that ConfigLoader can be initialized without explicit path."""
        loader = ConfigLoader()
        assert loader._config is not None
        assert isinstance(loader._config, dict)

    def test_init_with_explicit_path(self, config_path):
        """Test that ConfigLoader can be initialized with explicit path."""
        loader = ConfigLoader(config_path)
        assert loader._config is not None
        assert isinstance(loader._config, dict)

    def test_init_with_invalid_path(self, tmp_path):
        """Test that ConfigLoader raises error for non-existent file."""
        invalid_path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            ConfigLoader(invalid_path)

    def test_schema_validation(self, config_loader):
        """Test that schema validation passes for valid config."""
        # Should not raise any exceptions
        config_loader._validate_schema()

    def test_get_cards_by_elixir(self, config_loader):
        """Test get_cards_by_elixir returns correct structure."""
        cards_by_elixir = config_loader.get_cards_by_elixir()

        # Verify it's a dict
        assert isinstance(cards_by_elixir, dict)

        # Verify keys are integers
        for cost in cards_by_elixir.keys():
            assert isinstance(cost, int)

        # Verify values are lists of strings
        for cards in cards_by_elixir.values():
            assert isinstance(cards, list)
            for card in cards:
                assert isinstance(card, str)

        # Verify specific known cards exist
        assert 1 in cards_by_elixir
        assert "Skeletons" in cards_by_elixir[1]

        assert 4 in cards_by_elixir
        assert "Hog Rider" in cards_by_elixir[4]

        # Verify no hardcoded card names - all should be from JSON
        # by checking that common elixir costs have multiple cards
        assert len(cards_by_elixir[2]) > 5  # Many 2-elixir cards
        assert len(cards_by_elixir[3]) > 10  # Many 3-elixir cards
        assert len(cards_by_elixir[4]) > 10  # Many 4-elixir cards

    def test_get_evolution_cycles(self, config_loader):
        """Test get_evolution_cycles returns correct structure."""
        evolution_cycles = config_loader.get_evolution_cycles()

        # Verify it's a dict
        assert isinstance(evolution_cycles, dict)

        # Verify keys are strings (card names) and values are integers (cycles)
        for card_name, cycles in evolution_cycles.items():
            assert isinstance(card_name, str)
            assert isinstance(cycles, int)
            assert cycles > 0  # Cycles should be positive

        # Verify specific known evolution cards
        assert "Barbarians" in evolution_cycles
        assert evolution_cycles["Barbarians"] == 1

        assert "Firecracker" in evolution_cycles
        assert evolution_cycles["Firecracker"] == 2

        # Verify it returns a copy (modifying return shouldn't affect original)
        evolution_cycles["TestCard"] = 99
        evolution_cycles2 = config_loader.get_evolution_cycles()
        assert "TestCard" not in evolution_cycles2

    def test_get_elixir_timing(self, config_loader):
        """Test get_elixir_timing returns correct structure."""
        elixir_timing = config_loader.get_elixir_timing()

        # Verify it's an ElixirTiming instance
        assert isinstance(elixir_timing, ElixirTiming)

        # Verify all fields are present and are floats
        assert isinstance(elixir_timing.single_seconds_per_elixir, (int, float))
        assert isinstance(elixir_timing.double_seconds_per_elixir, (int, float))
        assert isinstance(elixir_timing.triple_seconds_per_elixir, (int, float))

        # Verify values are reasonable (from the JSON)
        assert elixir_timing.single_seconds_per_elixir == 2.8
        assert elixir_timing.double_seconds_per_elixir == 1.4
        assert elixir_timing.triple_seconds_per_elixir == 0.9

        # Verify ordering makes sense (faster elixir in later phases)
        assert (
            elixir_timing.single_seconds_per_elixir
            > elixir_timing.double_seconds_per_elixir
        )
        assert (
            elixir_timing.double_seconds_per_elixir
            > elixir_timing.triple_seconds_per_elixir
        )


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_missing_cards_section(self, tmp_path):
        """Test validation fails when cards section is missing."""
        invalid_config = {"game_mechanics": {"elixir": {}}}
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="Missing required key.*cards"):
            ConfigLoader(config_file)

    def test_missing_game_mechanics_section(self, tmp_path):
        """Test validation fails when game_mechanics section is missing."""
        invalid_config = {"cards": {"cards_by_elixir": {}, "evolution_cycles": {}}}
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="Missing required key.*game_mechanics"):
            ConfigLoader(config_file)

    def test_missing_cards_by_elixir(self, tmp_path):
        """Test validation fails when cards_by_elixir is missing."""
        invalid_config = {
            "cards": {"evolution_cycles": {}},
            "game_mechanics": {
                "elixir": {
                    "single_elixir": {"exact_seconds_per_elixir": 2.8},
                    "double_elixir": {"exact_seconds_per_elixir": 1.4},
                    "triple_elixir": {"exact_seconds_per_elixir": 0.9},
                }
            },
        }
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="Missing.*cards_by_elixir"):
            ConfigLoader(config_file)

    def test_missing_evolution_cycles(self, tmp_path):
        """Test validation fails when evolution_cycles is missing."""
        invalid_config = {
            "cards": {"cards_by_elixir": {}},
            "game_mechanics": {
                "elixir": {
                    "single_elixir": {"exact_seconds_per_elixir": 2.8},
                    "double_elixir": {"exact_seconds_per_elixir": 1.4},
                    "triple_elixir": {"exact_seconds_per_elixir": 0.9},
                }
            },
        }
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="Missing.*evolution_cycles"):
            ConfigLoader(config_file)

    def test_missing_elixir_timing(self, tmp_path):
        """Test validation fails when elixir timing data is incomplete."""
        invalid_config = {
            "cards": {"cards_by_elixir": {}, "evolution_cycles": {}},
            "game_mechanics": {
                "elixir": {
                    "single_elixir": {"exact_seconds_per_elixir": 2.8}
                    # Missing double and triple
                }
            },
        }
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            json.dump(invalid_config, f)

        with pytest.raises(ValueError, match="Missing.*elixir"):
            ConfigLoader(config_file)


class TestNoHardcodedData:
    """Tests to ensure no card names are hardcoded in the implementation."""

    def test_all_cards_from_json(self, config_loader, config_path):
        """Verify that all cards returned come from the JSON file."""
        # Read the JSON directly
        with open(config_path, "r") as f:
            raw_config = json.load(f)

        # Get cards from loader
        cards_by_elixir = config_loader.get_cards_by_elixir()

        # Flatten all cards from loader
        all_cards_from_loader = set()
        for cards in cards_by_elixir.values():
            all_cards_from_loader.update(cards)

        # Flatten all cards from JSON
        all_cards_from_json = set()
        for cards in raw_config["cards"]["cards_by_elixir"].values():
            all_cards_from_json.update(cards)

        # They should be identical
        assert all_cards_from_loader == all_cards_from_json

    def test_all_evolution_cards_from_json(self, config_loader, config_path):
        """Verify that all evolution data comes from the JSON file."""
        # Read the JSON directly
        with open(config_path, "r") as f:
            raw_config = json.load(f)

        # Get evolution cycles from loader
        evolution_cycles = config_loader.get_evolution_cycles()

        # Compare with JSON
        json_evolution = raw_config["cards"]["evolution_cycles"]

        # They should be identical
        assert evolution_cycles == json_evolution
