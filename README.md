# MotionEase
A lightweight Windows app that helps with motion sickness and screen-induced nausea.


MotionEase gives your eyes a stable reference point, guides you through calming paced breathing, and reminds you to look at the horizon — all in a single, dependency-free Python file.

Show Image
Show Image
Show Image


Why?

Motion sickness — whether in a car, on a boat, in VR, or just from scrolling too long — comes from a mismatch between what your eyes see and what your inner ear feels. MotionEase tackles that mismatch with three simple, evidence-informed tools, inspired by features like Apple's Vehicle Motion Cues.

Features

🎯 Visual Anchor Overlay

A fixed dot and horizon line drawn over your entire screen, always on top and fully click-through — it never blocks your mouse or keyboard. Your eyes keep a stable reference point while content scrolls or the vehicle moves.


Choose dot, horizon line, corner markers, or all three
Adjustable opacity
Toggle on/off with one click


🫁 Paced Breathing

An animated circle guides you through slow breathing (4s in · 2s hold · 6s out ≈ 5 breaths/min). Slow, controlled breathing calms the autonomic nervous system and measurably reduces nausea.

👀 Eye-Break Reminders

Set an interval and MotionEase reminds you to look up and fix your eyes on the horizon or a distant object for 20 seconds, letting your visual and balance systems re-sync.

💡 Quick Tips

Built-in practical advice for cars, boats, planes, gaming, and VR.

Installation

No dependencies. No pip installs. Just Python.

bashgit clone https://github.com/YOUR_USERNAME/motionease.git
cd motionease
python motion_ease.py

Requires Python 3.8+ on Windows (tkinter ships with the standard python.org installer).


The app runs on macOS/Linux too, but the overlay's transparency and click-through use the Windows API, so those features degrade gracefully elsewhere.



How the overlay works

The anchor overlay is a borderless, topmost tkinter window with a transparent color key. On Windows, MotionEase uses ctypes to set the WS_EX_TRANSPARENT | WS_EX_LAYERED extended window styles, making the window invisible to mouse input — clicks pass straight through to whatever is underneath.

Roadmap


 System tray mode
 Global hotkey to toggle the overlay
 Motion cues driven by accelerometer data (tablets/2-in-1s)
 Configurable colors and saved preferences


Contributions and ideas are welcome — open an issue or PR!

Disclaimer

MotionEase is a comfort aid, not a medical device. If you experience frequent or severe motion sickness, talk to a pharmacist or doctor.

License

MIT — do whatever helps you feel better.
