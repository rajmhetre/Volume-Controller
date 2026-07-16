# Gesture Volume Controller (pyautogui version)

Control your system's volume using hand gestures via webcam — pinch your thumb and index finger closer together to lower volume, spread them apart to raise it. Uses OS media keys instead of a platform audio API, so there's no `pycaw`/`comtypes` dependency headache.

## Tech Stack
- Python 3.10+
- OpenCV — webcam capture & rendering
- MediaPipe — hand landmark detection
- pyautogui — simulates volume up/down media key presses
- NumPy — range mapping

## Folder Structure
```
gesture-volume-controller-v2/
├── volume_controller.py
├── requirements.txt
└── README.md
```

## Setup & Run
```bash
pip install -r requirements.txt --no-cache-dir --timeout 120
python volume_controller.py
```

## How It Works
1. MediaPipe detects 21 hand landmarks per frame.
2. Distance is measured between thumb tip (landmark 4) and index tip (landmark 8).
3. That distance is mapped to a target volume percentage (0–100).
4. Instead of setting volume directly, the script presses the `volumeup`/`volumedown` media keys repeatedly to move the OS's actual volume toward that target — the same as pressing your keyboard's volume keys.

## Controls
- Pinch fingers together → volume decreases
- Spread fingers apart → volume increases
- Press `q` to quit

## Notes
- **Cross-platform**: works on Windows, macOS, and most Linux setups since it relies on OS media keys, not a platform-specific audio API.
- The on-screen % bar is an *estimate* tracked locally (starts at 50%) since media keys don't report the OS's real current volume back to the script. It may drift slightly from the actual system volume over a long session — press `q` and restart if it gets out of sync, or manually check your OS volume once to realign.
- Tweak `STEP` (key press size) and `PRESS_DELAY` (seconds between presses) in the script to make volume changes feel faster/slower or smoother/snappier.
- If `MIN_DIST`/`MAX_DIST` (20–200) don't match your hand/camera distance well, adjust those two values to calibrate sensitivity.
