# Gesture-Based PC Control

A Python application that enables real-time computer control using hand gestures. Powered by OpenCV, MediaPipe, and PyAutoGUI, this tool translates your webcam feed into system commands like media playback, volume control, and window management.

## Features

The script uses hand landmarks to detect specific finger configurations and movements. Built-in cooldowns and sensitivity thresholds ensure stable operation and prevent accidental spamming of commands.

### Supported Gestures & Commands

*   **Volume Control (Index Finger):** Raise only your index finger. Move your hand up to increase the volume (+4), or move it down to decrease the volume (-4).
*   **Play / Pause (Two Fingers):** Raise your index and middle fingers and hold the pose for 0.8 seconds to toggle media playback.
*   **Fullscreen / Press 'F' (Three Fingers):** Raise your index, middle, and ring fingers and hold for 0.8 seconds to simulate pressing the 'F' key (commonly used for fullscreen in media players).
*   **Switch Windows (Four Fingers):** Raise four fingers (thumb excluded) and swipe horizontally. Swipe right to switch to the next window (`Alt` + `Esc`) or swipe left for the previous window (`Alt` + `Shift` + `Esc`).
*   **Mute / Unmute (Fist):** Hold a closed fist steady for 1 second to toggle system mute.

## Prerequisites

Python 3.8 or newer installed. A functioning webcam connected to your computer.

The required third-party libraries:
*   `opencv-python`
*   `mediapipe`
*   `pyautogui`

## Installation

1. Clone or download this repository to your local machine.
2. Open a terminal or command prompt in the project directory.
3. Install the required dependencies using pip:

```bash
pip install opencv-python mediapipe pyautogui
