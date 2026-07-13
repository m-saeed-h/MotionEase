"""
MotionEase - a Windows helper app for motion sickness & cybersickness
=====================================================================
Features
--------
1. Visual Anchor Overlay : a fixed dot + horizon line drawn on top of your
   screen. Keeping a stable reference point in view reduces the
   visual-vestibular mismatch that causes screen-induced nausea
   (similar idea to Apple's "Vehicle Motion Cues").
2. Paced Breathing       : slow, guided diaphragmatic breathing, which has
   been shown to reduce nausea symptoms.
3. Eye-Break Reminder    : nudges you to look at the horizon / a distant
   object at regular intervals.
4. Quick Tips            : practical advice while travelling or gaming.

Requirements: Python 3.8+ on Windows (tkinter is included with the
standard python.org installer). No third-party packages needed.

Run with:  python motion_ease.py
"""

import sys
import time
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox

IS_WINDOWS = sys.platform.startswith("win")

# ----------------------------------------------------------------------
# Click-through helper (Windows only)
# ----------------------------------------------------------------------
def make_click_through(window):
    """Make a tkinter window ignore mouse clicks (Windows only)."""
    if not IS_WINDOWS:
        return
    try:
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    except Exception:
        pass  # degrade gracefully on non-Windows / odd setups


# ----------------------------------------------------------------------
# Visual anchor overlay
# ----------------------------------------------------------------------
class AnchorOverlay:
    """Always-on-top transparent overlay with a stable dot + horizon line."""

    TRANSPARENT_COLOR = "#010101"  # unlikely colour, keyed out on Windows

    def __init__(self, root, style="dot+line", color="#00d26a", opacity=0.85):
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)

        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        self.win.geometry(f"{sw}x{sh}+0+0")

        if IS_WINDOWS:
            self.win.attributes("-transparentcolor", self.TRANSPARENT_COLOR)
        self.win.attributes("-alpha", opacity)

        self.canvas = tk.Canvas(
            self.win, bg=self.TRANSPARENT_COLOR, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        cx, cy = sw // 2, sh // 2
        r = 9

        if "line" in style:
            # horizon line with a gap in the middle so text stays readable
            self.canvas.create_line(40, cy, cx - 60, cy, fill=color, width=2)
            self.canvas.create_line(cx + 60, cy, sw - 40, cy, fill=color, width=2)
        if "dot" in style:
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=color, outline="white", width=2,
            )
        if "corners" in style:
            # small stable markers near screen edges (peripheral cues)
            m, s = 60, 14
            for x, y in [(m, m), (sw - m, m), (m, sh - m), (sw - m, sh - m)]:
                self.canvas.create_oval(
                    x - s // 2, y - s // 2, x + s // 2, y + s // 2,
                    fill=color, outline="white",
                )

        self.win.update_idletasks()
        make_click_through(self.win)

    def close(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass


# ----------------------------------------------------------------------
# Main application
# ----------------------------------------------------------------------
class MotionEaseApp:
    BG = "#101418"
    CARD = "#1a2028"
    FG = "#e8edf2"
    ACCENT = "#00d26a"

    def __init__(self, root):
        self.root = root
        self.overlay = None
        self.breath_running = False
        self.break_job = None

        root.title("MotionEase - Motion Sickness Helper")
        root.geometry("560x620")
        root.configure(bg=self.BG)
        root.minsize(480, 560)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab", padding=(16, 8),
            background=self.CARD, foreground=self.FG,
        )
        style.map("TNotebook.Tab", background=[("selected", self.ACCENT)],
                  foreground=[("selected", "#08110c")])

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_anchor = tk.Frame(nb, bg=self.BG)
        self.tab_breath = tk.Frame(nb, bg=self.BG)
        self.tab_break = tk.Frame(nb, bg=self.BG)
        self.tab_tips = tk.Frame(nb, bg=self.BG)

        nb.add(self.tab_anchor, text="  Visual Anchor  ")
        nb.add(self.tab_breath, text="  Breathing  ")
        nb.add(self.tab_break, text="  Eye Breaks  ")
        nb.add(self.tab_tips, text="  Tips  ")

        self._build_anchor_tab()
        self._build_breath_tab()
        self._build_break_tab()
        self._build_tips_tab()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- helpers ----------------
    def _label(self, parent, text, size=11, bold=False, wrap=480, pady=4):
        lbl = tk.Label(
            parent, text=text, bg=self.BG, fg=self.FG, justify="left",
            wraplength=wrap,
            font=("Segoe UI", size, "bold" if bold else "normal"),
        )
        lbl.pack(anchor="w", padx=18, pady=pady)
        return lbl

    def _button(self, parent, text, cmd, primary=True):
        btn = tk.Button(
            parent, text=text, command=cmd,
            bg=self.ACCENT if primary else self.CARD,
            fg="#08110c" if primary else self.FG,
            activebackground="#2be386", relief="flat",
            font=("Segoe UI", 11, "bold"), padx=16, pady=8, cursor="hand2",
        )
        return btn

    # ---------------- Visual Anchor tab ----------------
    def _build_anchor_tab(self):
        t = self.tab_anchor
        self._label(t, "Visual Anchor Overlay", 16, bold=True, pady=(16, 2))
        self._label(
            t,
            "Draws a fixed dot and horizon line over everything on screen. "
            "Your eyes get a stable reference point while content scrolls or "
            "the vehicle moves, which reduces the sensory mismatch behind "
            "nausea. The overlay is click-through, so it never blocks your work.",
        )

        opts = tk.Frame(t, bg=self.BG)
        opts.pack(anchor="w", padx=18, pady=8)

        tk.Label(opts, text="Style:", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w")
        self.style_var = tk.StringVar(value="dot+line")
        for i, (label, val) in enumerate([
            ("Dot + horizon line", "dot+line"),
            ("Dot only", "dot"),
            ("Corner markers", "corners"),
            ("Everything", "dot+line+corners"),
        ]):
            tk.Radiobutton(
                opts, text=label, value=val, variable=self.style_var,
                bg=self.BG, fg=self.FG, selectcolor=self.CARD,
                activebackground=self.BG, activeforeground=self.FG,
                font=("Segoe UI", 10),
            ).grid(row=i + 1, column=0, sticky="w", pady=1)

        tk.Label(opts, text="Opacity:", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 11)).grid(row=0, column=1, sticky="w",
                                             padx=(40, 0))
        self.opacity_var = tk.DoubleVar(value=0.85)
        tk.Scale(
            opts, from_=0.3, to=1.0, resolution=0.05, orient="horizontal",
            variable=self.opacity_var, bg=self.BG, fg=self.FG,
            highlightthickness=0, troughcolor=self.CARD, length=160,
        ).grid(row=1, column=1, rowspan=3, padx=(40, 0), sticky="n")

        btns = tk.Frame(t, bg=self.BG)
        btns.pack(anchor="w", padx=18, pady=12)
        self.anchor_btn = self._button(btns, "Show overlay", self.toggle_overlay)
        self.anchor_btn.pack(side="left")

        self.anchor_status = self._label(t, "Overlay is off.", 10, pady=(4, 0))

    def toggle_overlay(self):
        if self.overlay:
            self.overlay.close()
            self.overlay = None
            self.anchor_btn.config(text="Show overlay")
            self.anchor_status.config(text="Overlay is off.")
        else:
            self.overlay = AnchorOverlay(
                self.root,
                style=self.style_var.get(),
                opacity=self.opacity_var.get(),
            )
            self.anchor_btn.config(text="Hide overlay")
            self.anchor_status.config(
                text="Overlay is on. It stays above all windows and is "
                     "click-through."
            )

    # ---------------- Breathing tab ----------------
    def _build_breath_tab(self):
        t = self.tab_breath
        self._label(t, "Paced Breathing", 16, bold=True, pady=(16, 2))
        self._label(
            t,
            "Slow, controlled breathing calms the autonomic nervous system "
            "and measurably reduces nausea. Follow the circle: breathe in as "
            "it grows, hold, and breathe out slowly as it shrinks.",
        )

        self.breath_canvas = tk.Canvas(
            t, width=300, height=300, bg=self.BG, highlightthickness=0
        )
        self.breath_canvas.pack(pady=6)

        self.breath_text = self.breath_canvas.create_text(
            150, 150, text="Press start", fill=self.FG,
            font=("Segoe UI", 14, "bold"),
        )
        self.breath_circle = self.breath_canvas.create_oval(
            110, 110, 190, 190, outline=self.ACCENT, width=4
        )

        self.breath_btn = self._button(t, "Start breathing", self.toggle_breath)
        self.breath_btn.pack(pady=4)

    def toggle_breath(self):
        self.breath_running = not self.breath_running
        if self.breath_running:
            self.breath_btn.config(text="Stop")
            self._breath_cycle_start = time.time()
            self._animate_breath()
        else:
            self.breath_btn.config(text="Start breathing")
            self.breath_canvas.itemconfig(self.breath_text, text="Press start")

    def _animate_breath(self):
        """4s inhale, 2s hold, 6s exhale (12s cycle, ~5 breaths/min)."""
        if not self.breath_running:
            return
        elapsed = (time.time() - self._breath_cycle_start) % 12.0
        cx, cy = 150, 150
        r_min, r_max = 40, 110

        if elapsed < 4:  # inhale
            frac = elapsed / 4
            r = r_min + (r_max - r_min) * frac
            phase = "Breathe in..."
        elif elapsed < 6:  # hold
            r = r_max
            phase = "Hold"
        else:  # exhale
            frac = (elapsed - 6) / 6
            r = r_max - (r_max - r_min) * frac
            phase = "Breathe out slowly..."

        self.breath_canvas.coords(
            self.breath_circle, cx - r, cy - r, cx + r, cy + r
        )
        self.breath_canvas.itemconfig(self.breath_text, text=phase)
        self.root.after(33, self._animate_breath)

    # ---------------- Eye break tab ----------------
    def _build_break_tab(self):
        t = self.tab_break
        self._label(t, "Eye-Break Reminder", 16, bold=True, pady=(16, 2))
        self._label(
            t,
            "Looking up from the screen at the horizon or a distant object "
            "gives your visual and balance systems a chance to re-sync. "
            "Set an interval and MotionEase will remind you.",
        )

        row = tk.Frame(t, bg=self.BG)
        row.pack(anchor="w", padx=18, pady=8)
        tk.Label(row, text="Remind me every", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 11)).pack(side="left")
        self.interval_var = tk.IntVar(value=10)
        tk.Spinbox(row, from_=1, to=60, width=4,
                   textvariable=self.interval_var,
                   font=("Segoe UI", 11)).pack(side="left", padx=6)
        tk.Label(row, text="minutes", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 11)).pack(side="left")

        self.break_btn = self._button(t, "Start reminders", self.toggle_breaks)
        self.break_btn.pack(anchor="w", padx=18, pady=8)
        self.break_status = self._label(t, "Reminders are off.", 10)

    def toggle_breaks(self):
        if self.break_job:
            self.root.after_cancel(self.break_job)
            self.break_job = None
            self.break_btn.config(text="Start reminders")
            self.break_status.config(text="Reminders are off.")
        else:
            mins = max(1, self.interval_var.get())
            self.break_btn.config(text="Stop reminders")
            self.break_status.config(
                text=f"Reminders on - every {mins} minute(s)."
            )
            self._schedule_break(mins)

    def _schedule_break(self, mins):
        self.break_job = self.root.after(mins * 60 * 1000,
                                         lambda: self._fire_break(mins))

    def _fire_break(self, mins):
        try:
            self.root.bell()
        except tk.TclError:
            pass
        messagebox.showinfo(
            "MotionEase - time for a break",
            "Look away from the screen.\n\n"
            "Fix your eyes on the horizon or the most distant thing you can "
            "see for at least 20 seconds. Take a few slow breaths.",
        )
        if self.break_job is not None:
            self._schedule_break(mins)

    # ---------------- Tips tab ----------------
    def _build_tips_tab(self):
        t = self.tab_tips
        self._label(t, "Quick Tips", 16, bold=True, pady=(16, 2))
        tips = (
            "- Look at the horizon or a fixed distant point whenever you can.\n"
            "- Sit where motion is felt least: front seat of a car, over the "
            "wings on a plane, midship and low on a boat.\n"
            "- Get fresh, cool air on your face; avoid strong smells.\n"
            "- Avoid reading on a phone in a moving vehicle; if you must, "
            "hold it high and near your eye line.\n"
            "- Eat something light and dry before travelling; avoid heavy, "
            "greasy meals and alcohol.\n"
            "- Ginger (tea, chews, capsules) helps some people.\n"
            "- For gaming/VR: lower field-of-view movement effects, disable "
            "camera bob, raise the frame rate, and take breaks early - do "
            "not push through nausea.\n"
            "- Slow breathing at ~5 breaths per minute (use the Breathing "
            "tab) at the first sign of queasiness.\n\n"
            "If motion sickness is frequent or severe, a pharmacist or "
            "doctor can suggest options such as antihistamine travel "
            "tablets - this app is a comfort aid, not medical advice."
        )
        self._label(t, tips, 10)

    # ---------------- shutdown ----------------
    def on_close(self):
        if self.overlay:
            self.overlay.close()
        if self.break_job:
            self.root.after_cancel(self.break_job)
        self.root.destroy()


def main():
    root = tk.Tk()
    MotionEaseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
