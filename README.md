# cr-elixir-cycle-overlay

A Clash Royale elixir and card-cycle tracking overlay for Windows using screen capture and computer vision.

## Overview

This project provides a real-time overlay that tracks:
- **Opponent's Elixir**: Estimates the opponent's current elixir count based on card plays and time-based generation
- **Card Cycle**: Identifies which cards the opponent has played and predicts their hand/next cards

The overlay uses only screen capture and computer vision techniques to analyze the game window. It does not:
- Read game memory
- Inject code into the game
- Modify game behavior
- Automate any gameplay actions

## Technology Stack

- **Python 3.8+**
- **OpenCV** for computer vision and card detection
- **NumPy** for numerical operations
- **PyQt6** for transparent overlay UI

## Project Structure

```
cr-elixir-cycle-overlay/
├── README.md
├── pyproject.toml
├── cr_overlay_knowledge.json
├── src/
│   └── croverlay/
│       ├── __init__.py
│       ├── capture.py          # Screen capture from game window
│       ├── detect.py            # Card detection and classification
│       ├── elixir_tracker.py   # Elixir generation and spending tracking
│       ├── cycle_tracker.py    # Card cycle inference
│       ├── overlay_ui.py       # PyQt overlay window
│       ├── config_loader.py    # Load game knowledge from JSON
│       └── calibration.py      # Window position and scaling
└── tests/
```

## Installation

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

(To be implemented)

## How It Works

The overlay analyzes frames captured from the Clash Royale game window to:
1. Detect when the opponent plays a card
2. Identify which card was played using computer vision
3. Track elixir spending and time-based regeneration
4. Infer the opponent's deck composition and card cycle

All tracking is based on the game mechanics documented in `cr_overlay_knowledge.json`, which contains:
- Elixir generation rates (single/double/triple elixir phases)
- Complete card list with elixir costs
- Card evolution mechanics
- Cycle tracking algorithms

## Important Notice: Educational Use and Terms of Service

**⚠️ IMPORTANT DISCLAIMER ⚠️**

This project is provided **FOR EDUCATIONAL PURPOSES ONLY** to demonstrate computer vision techniques and game state tracking.

**Using this overlay while playing Clash Royale online may violate Supercell's Terms of Service**, which prohibit the use of third-party software that provides unfair advantages. Specifically:

- Supercell's ToS prohibits "cheats, exploits, automation software, bots, hacks, mods or any unauthorized third-party software designed to modify or interfere with the Service, any Supercell game or any Supercell game experience"
- Using this overlay in online matches could result in account suspension or permanent ban
- This software is intended only for educational purposes and offline analysis

**By using this software, you acknowledge that:**
1. You understand the risks of using third-party overlays with online games
2. You are solely responsible for any consequences, including potential account bans
3. The authors of this software assume no liability for any account actions taken by Supercell
4. This software should only be used in offline or practice environments for learning purposes

**Use at your own risk. You have been warned.**

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Game mechanics based on Clash Royale Wiki and official Supercell update notes
- Card data aligned with community resources like DeckShop