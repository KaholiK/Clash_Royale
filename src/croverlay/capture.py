"""
capture.py

Captures frames from the game window at a target FPS.
Windows-only screen capture utility using mss library or Win32 fallback.
"""

import time
import sys
import numpy as np
import cv2
from typing import Generator, Tuple, Optional


def frames(
    window_title: Optional[str] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    target_fps: float = 30.0,
    resize: Optional[Tuple[int, int]] = None,
    monitor: int = 1,
) -> Generator[Tuple[float, np.ndarray], None, None]:
    """
    Generator that yields frames captured from a window region at target FPS.

    This is a Windows-only implementation that uses the mss library if available,
    or falls back to Win32 API for screen capture.

    Args:
        window_title: Title of the window to capture (optional, for Win32 fallback).
                     If None and no region specified, captures the primary monitor.
        region: Tuple of (x, y, width, height) for the capture region.
                If None, captures the entire window or monitor.
        target_fps: Target frames per second for capture (default: 30.0).
        resize: Optional tuple of (width, height) to resize captured frames.
        monitor: Monitor number to capture from (1-indexed, default: 1).

    Yields:
        Tuple of (timestamp_seconds, frame_bgr) where:
        - timestamp_seconds: float timestamp when the frame was captured
        - frame_bgr: numpy array in BGR format (OpenCV standard)

    Raises:
        RuntimeError: If not running on Windows.
        ImportError: If neither mss nor pywin32 is available.

    Example:
        >>> for timestamp, frame in frames(region=(0, 0, 1920, 1080), target_fps=30):
        ...     # Process frame
        ...     if cv2.waitKey(1) & 0xFF == ord('q'):
        ...         break
    """
    if sys.platform != "win32":
        raise RuntimeError("Screen capture is only supported on Windows")

    # Try to use mss first, then fall back to Win32
    try:
        import mss  # noqa: F401

        use_mss = True
    except ImportError:
        use_mss = False
        try:
            import win32gui  # noqa: F401
            import win32ui  # noqa: F401
            import win32con  # noqa: F401
        except ImportError:
            raise ImportError(
                "Screen capture requires either 'mss' or 'pywin32' to be installed. "
                "Install with: pip install mss  or  pip install pywin32"
            )

    frame_delay = 1.0 / target_fps

    if use_mss:
        # Use mss for screen capture (faster and more reliable)
        yield from _capture_with_mss(region, monitor, frame_delay, resize)
    else:
        # Fall back to Win32 API
        yield from _capture_with_win32(window_title, region, frame_delay, resize)


def _capture_with_mss(
    region: Optional[Tuple[int, int, int, int]],
    monitor: int,
    frame_delay: float,
    resize: Optional[Tuple[int, int]],
) -> Generator[Tuple[float, np.ndarray], None, None]:
    """
    Capture frames using the mss library.

    Args:
        region: Capture region (x, y, width, height) or None for full monitor.
        monitor: Monitor number (1-indexed).
        frame_delay: Delay between frames in seconds.
        resize: Target size (width, height) or None.

    Yields:
        Tuple of (timestamp, frame_bgr).
    """
    import mss

    with mss.mss() as sct:
        # Get monitor configuration
        if region:
            x, y, width, height = region
            capture_region = {"top": y, "left": x, "width": width, "height": height}
        else:
            # Capture the entire specified monitor
            monitors = sct.monitors
            if monitor < 1 or monitor >= len(monitors):
                monitor = 1  # Default to primary monitor
            capture_region = monitors[monitor]

        last_capture_time = 0.0

        while True:
            current_time = time.time()

            # Rate limiting to achieve target FPS
            time_since_last = current_time - last_capture_time
            if time_since_last < frame_delay:
                time.sleep(frame_delay - time_since_last)
                current_time = time.time()

            # Capture the screen
            screenshot = sct.grab(capture_region)

            # Convert to numpy array (BGRA format from mss)
            frame = np.array(screenshot)

            # Convert BGRA to BGR (OpenCV standard)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Resize if requested
            if resize:
                frame_bgr = cv2.resize(
                    frame_bgr, resize, interpolation=cv2.INTER_LINEAR
                )

            last_capture_time = current_time

            yield (current_time, frame_bgr)


def _capture_with_win32(
    window_title: Optional[str],
    region: Optional[Tuple[int, int, int, int]],
    frame_delay: float,
    resize: Optional[Tuple[int, int]],
) -> Generator[Tuple[float, np.ndarray], None, None]:
    """
    Capture frames using Win32 API (fallback method).

    Args:
        window_title: Window title to capture or None for desktop.
        region: Capture region (x, y, width, height) or None.
        frame_delay: Delay between frames in seconds.
        resize: Target size (width, height) or None.

    Yields:
        Tuple of (timestamp, frame_bgr).
    """
    import win32gui
    import win32ui
    import win32con

    # Get the device context
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            raise ValueError(f"Window with title '{window_title}' not found")
    else:
        hwnd = win32gui.GetDesktopWindow()

    # Determine capture region
    if region:
        x, y, width, height = region
    else:
        if window_title and hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            x, y = left, top
            width, height = right - left, bottom - top
        else:
            x, y = 0, 0
            width = win32gui.GetSystemMetrics(win32con.SM_CXSCREEN)
            height = win32gui.GetSystemMetrics(win32con.SM_CYSCREEN)

    last_capture_time = 0.0

    # Create device contexts
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    try:
        while True:
            current_time = time.time()

            # Rate limiting to achieve target FPS
            time_since_last = current_time - last_capture_time
            if time_since_last < frame_delay:
                time.sleep(frame_delay - time_since_last)
                current_time = time.time()

            # Capture the screen
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)

            # Convert to numpy array
            bmpstr = saveBitMap.GetBitmapBits(True)
            frame = np.frombuffer(bmpstr, dtype=np.uint8)
            frame = frame.reshape((height, width, 4))

            # Convert BGRA to BGR
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Resize if requested
            if resize:
                frame_bgr = cv2.resize(
                    frame_bgr, resize, interpolation=cv2.INTER_LINEAR
                )

            last_capture_time = current_time

            yield (current_time, frame_bgr)

    finally:
        # Cleanup
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())
