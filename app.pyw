import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import pygame
from mutagen.mp3 import MP3
import threading
import time
from pynput import keyboard
import os
import ctypes  
import json


# Fix blurry UI on Windows (DPI scaling)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

pygame.mixer.init()

def format_time(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    return f"{m:02}:{s:02}"

class SimpleAudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Audio Player")
        self.root.geometry("480x115")
        self.root.configure(bg="#f7f7f7")
        self.root.resizable(False, False)

        # Style setup for modern crisp look
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 9), padding=4)
        style.configure("Horizontal.TScale", troughcolor="#e6e6e6", background="#0078d7")

        self.file_path = None
        self.playing = False
        self.length = 0
        self.user_dragging = False
        self.start_time = 0
        self.paused_elapsed = 0

        # --- Header (Label + Browse Button) ---
        header = tk.Frame(root, bg="#f7f7f7")
        header.pack(fill="x", padx=8, pady=(6, 2))

        self.label = tk.Label(header, text="🎵 Drop or Browse an MP3 file", bg="#f7f7f7", fg="#222", font=("Segoe UI", 9))
        self.label.pack(side="left", padx=(4, 6))

        browse_btn = ttk.Button(header, text="Browse", command=self.browse_file, takefocus=0)
        browse_btn.pack(side="right")

        # --- Combined Time and Progress Bar Row ---
        progress_row_frame = tk.Frame(root, bg="#f7f7f7")
        progress_row_frame.pack(fill="x", padx=8, pady=(0, 4)) # outer padding

        # Elapsed Label (Left) - Packed First
        self.elapsed_label = tk.Label(progress_row_frame, text="00:00", bg="#f7f7f7", fg="#444", font=("Consolas", 9))
        self.elapsed_label.pack(side="left", padx=(4, 6))

        # Total Label (Right) - Packed Second (to reserve its space)
        self.total_label = tk.Label(progress_row_frame, text="00:00", bg="#f7f7f7", fg="#444", font=("Consolas", 9))
        self.total_label.pack(side="right", padx=(6, 4)) # side="right" must be explicitly set

        # --- Progress bar (custom drawn for crispness) (Middle, Expands) - Packed LAST ---
        self.progress = tk.DoubleVar()
        self.progress_height = 10  # increased thickness
        self.progress_frame = tk.Canvas(progress_row_frame, bg="#f7f7f7", height=self.progress_height,
                                        bd=0, highlightthickness=0, relief="flat")
        # Pack to the left, fill horizontally, and expand to take space
        self.progress_frame.pack(side="left", fill="x", expand=True, padx=6)


        # Create background (unprogressed) track and progress bar
        # Initial width of 1 is enough, _draw_progress will fix it on update
        self.track_bg = self.progress_frame.create_rectangle(
            0, 0, 1, self.progress_height, fill="#e0e0e0", width=0
        )
        self.progress_bar = self.progress_frame.create_rectangle(
            0, 0, 0, self.progress_height, fill="#0078d7", width=0
        )

        self.progress_frame.bind("<Button-1>", self.on_click)
        self.progress_frame.bind("<B1-Motion>", self.on_drag)
        self.progress_frame.bind("<ButtonRelease-1>", self.on_release)

        # --- Play Button ---
        self.btn_frame = tk.Frame(root, bg="#f7f7f7", takefocus=0 )
        self.btn_frame.pack(pady=(2, 6))

        self.play_button = tk.Button(
            self.btn_frame, text="▶", font=("Segoe UI Symbol", 11, "bold"),
            command=self.toggle_play_pause, relief="flat",
            bg="#0078d7", fg="white", width=5, height=1,
            cursor="hand2", activebackground="#005a9e", bd=0,
            takefocus=0, # Already present
            highlightthickness=0 # <-- FIX: Removes the focus outline
        )
        self.play_button.pack()

        self.play_button.bind("<Enter>", lambda e: self.play_button.config(bg="#1083e2"))
        self.play_button.bind("<Leave>", lambda e: self.play_button.config(bg="#0078d7"))

        # --- Drag and Drop ---
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # --- Background update thread ---
        threading.Thread(target=self.update_ui, daemon=True).start()

        # --- Global Hotkeys ---
        listener = keyboard.GlobalHotKeys({
            'a': lambda: self.seek(-5),
            '<space>': self.toggle_play_pause,
            'd': lambda: self.seek(5)
        })
        listener.start()

        # This prevents the spacebar from activating the 'Browse' button's command.
        self.root.focus_set()

        # Load last session
        self.root.after(500, self.load_state)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        
    # ---- File Selection ----
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.load_audio(file_path)

    def on_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            self.load_audio(path)

    # ---- Audio Controls ----
    def load_audio(self, path):
        if not path.lower().endswith(".mp3"):
            self.label.config(text="❌ Unsupported file")
            return
        self.file_path = path
        audio = MP3(path)
        self.length = audio.info.length
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.start_time = time.time()
        self.paused_elapsed = 0
        self.playing = True
        self.play_button.config(text="⏸")
        self.label.config(text=f"🎧 {os.path.basename(path)}")
        self.total_label.config(text=format_time(self.length))

    def toggle_play_pause(self):
        if not self.file_path: return

        self.save_state()

        if self.playing:
            self.paused_elapsed = self.get_elapsed()
            pygame.mixer.music.pause()
            self.playing = False
            self.play_button.config(text="▶")
        else:
            pygame.mixer.music.play(start=self.paused_elapsed)
            self.start_time = time.time() - self.paused_elapsed
            self.playing = True
            self.play_button.config(text="⏸")

    def seek(self, delta):
        if not self.file_path: return
        new_time = max(0, min(self.length, self.get_elapsed() + delta))
        self.paused_elapsed = new_time
        if self.playing:
            pygame.mixer.music.play(start=new_time)
            self.start_time = time.time() - new_time
        self.update_labels()
        self.save_state()

    # ---- Progress Bar and Timing ----
    def on_click(self, event):
        if not self.file_path: return
        self.user_dragging = True
        self._update_progress(event.x)

    def on_drag(self, event):
        if not self.file_path: return
        self._update_progress(event.x)

    def on_release(self, event):
        if not self.file_path: return
        self.user_dragging = False
        self._seek_to(event.x)

    def _update_progress(self, x):
        width = self.progress_frame.winfo_width()
        x = max(0, min(x, width))
        self.progress.set((x / width) * 100)
        self._draw_progress()

    def _seek_to(self, x):
        width = self.progress_frame.winfo_width()
        new_time = (x / width) * self.length
        self.paused_elapsed = new_time
        if self.playing:
            pygame.mixer.music.play(start=new_time)
            self.start_time = time.time() - new_time
        self.update_labels()

    def _draw_progress(self):
        width = self.progress_frame.winfo_width()
        percent = self.progress.get() / 100
        # Ensure correct coordinates are passed based on current width
        self.progress_frame.coords(self.track_bg, 0, 0, width, self.progress_height)
        self.progress_frame.coords(self.progress_bar, 0, 0, width * percent, self.progress_height)


    def get_elapsed(self):
        return self.paused_elapsed if not self.playing else time.time() - self.start_time

    def update_labels(self):
        elapsed = self.get_elapsed()
        self.elapsed_label.config(text=format_time(elapsed))
        if not self.user_dragging and self.length > 0:
            self.progress.set((elapsed / self.length) * 100)
            self._draw_progress()

    def update_ui(self):
        while True:
            if self.file_path and self.length > 0:
                self.update_labels()
                # Periodically save current progress
                if self.playing:
                    self.save_state()
            time.sleep(0.2)

    CACHE_FILE = "player_cache.json"

    def save_state(self):
        """Save the current file and playback time."""
        if not self.file_path:
            return
        state = {
            "path": self.file_path,
            "time": self.get_elapsed()
        }
        try:
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception as e:
            print("Error saving cache:", e)

    def load_state(self):
        """Load the last played file and position if available."""
        if not os.path.exists(self.CACHE_FILE):
            return
        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            path = state.get("path")
            t = state.get("time", 0)
            if path and os.path.exists(path):
                self.load_audio(path)
                # Start paused at last position
                pygame.mixer.music.pause()
                self.playing = False
                self.paused_elapsed = t
                self.update_labels()
                self.play_button.config(text="▶")
                self.label.config(text=f"⏪ Resumed {os.path.basename(path)}")
        except Exception as e:
            print("Error loading cache:", e)

    def on_close(self):
        self.save_state()
        self.root.destroy()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SimpleAudioPlayer(root)
    root.mainloop()
