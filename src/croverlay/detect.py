"""
detect.py

Runs CV pipeline to detect new opponent card placements and classify
card name + evolved flag.
"""

from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np


@dataclass
class DetectedPlay:
    """
    Represents a detected card play on the battlefield.

    Attributes:
        card_name: The name of the card played, or None if classification fails
        is_evolved: Whether this is an evolved version of the card
        bbox: Bounding box as (x, y, width, height) of the detected region
        timestamp: Time in seconds when the play was detected
    """

    card_name: Optional[str]
    is_evolved: bool
    bbox: tuple[int, int, int, int]  # (x, y, w, h)
    timestamp: float


class CardDetector:
    """
    Detects opponent card plays using frame differencing and classification.

    This is a scaffold implementation that uses simple frame differencing to
    detect motion in the opponent play area, then attempts to classify the
    detected regions as specific cards.
    """

    def __init__(
        self, motion_threshold: float = 25.0, min_contour_area: int = 500
    ):
        """
        Initialize the card detector.

        Args:
            motion_threshold: Threshold for frame diff to detect motion
            min_contour_area: Minimum contour area for valid detection
        """
        self.motion_threshold = motion_threshold
        self.min_contour_area = min_contour_area

        # TODO: Load trained classifier model from <PATH-TO-DATASET-ROOT>
        # The dataset should contain:
        #   - <PATH-TO-DATASET-ROOT>/train/base/<card_name>/*.png
        #   - <PATH-TO-DATASET-ROOT>/train/evo/<card_name>/*.png
        # Example structure:
        #   - <PATH-TO-DATASET-ROOT>/train/base/Skeletons/*.png
        #   - <PATH-TO-DATASET-ROOT>/train/evo/Skeletons/*.png
        #   - <PATH-TO-DATASET-ROOT>/train/base/Archer_Queen/*.png
        self.classifier = None  # Placeholder for real classifier

    def detect_plays(
        self,
        prev_frame: np.ndarray,
        current_frame: np.ndarray,
        timestamp: float = 0.0,
    ) -> list[DetectedPlay]:
        """
        Detect card plays between two consecutive frames.

        Uses simple frame differencing to find regions where new
        objects appeared, then classifies each detected region.

        Args:
            prev_frame: Previous frame from the game capture (BGR format)
            current_frame: Current frame from the game capture (BGR format)
            timestamp: Timestamp in seconds for this detection

        Returns:
            List of DetectedPlay objects for each detected card play
        """
        if prev_frame is None or current_frame is None:
            return []

        # Convert frames to grayscale for motion detection
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # Compute absolute difference between frames
        frame_diff = cv2.absdiff(prev_gray, curr_gray)

        # Apply threshold to get binary mask of changed regions
        _, thresh = cv2.threshold(
            frame_diff, self.motion_threshold, 255, cv2.THRESH_BINARY
        )

        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Find contours of changed regions
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detected_plays = []

        # Process each detected contour
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter out small contours (noise)
            if area < self.min_contour_area:
                continue

            # Get bounding box for the contour
            x, y, w, h = cv2.boundingRect(contour)
            bbox = (x, y, w, h)

            # Extract the region from current frame for classification
            crop = current_frame[y: y + h, x: x + w]

            # Classify the cropped region
            # TODO: Replace with actual classifier that uses the trained model
            card_name, is_evolved = self._classify_crop(crop)

            detected_plays.append(
                DetectedPlay(
                    card_name=card_name,
                    is_evolved=is_evolved,
                    bbox=bbox,
                    timestamp=timestamp,
                )
            )

        return detected_plays

    def _classify_crop(self, crop: np.ndarray) -> tuple[Optional[str], bool]:
        """
        Classify a cropped region as a specific card.

        This is a placeholder implementation that always returns None.

        TODO: Implement real classification using trained CNN or
        template matching. The classifier should:
        1. Load from <PATH-TO-DATASET-ROOT>/models/card_classifier.pkl
        2. Preprocess the crop (resize, normalize, etc.)
        3. Run inference to get card name and evolution status
        4. Return (card_name, is_evolved) tuple

        For CNN approach:
        - Use a lightweight model like MobileNet trained on battlefield crops
        - Input: Cropped card image from battlefield (not hand art)
        - Output: Classification into 121 card classes + evolved flag

        For template matching approach:
        - Load templates from <PATH-TO-DATASET-ROOT>/templates/
        - Use multi-scale template matching
        - Check for purple evolution effects to determine is_evolved

        Args:
            crop: Cropped image region containing potential card

        Returns:
            Tuple of (card_name, is_evolved) where card_name is None if
            classification fails or confidence is too low
        """
        # Placeholder: always return None for card_name
        return (None, False)
