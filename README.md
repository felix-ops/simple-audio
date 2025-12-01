# Minimalist Audiobook Player 🎧

A lightweight, distraction-free MP3 player designed for multitasking.

I built this tool specifically to **listen to audiobooks while reading light novels** in a browser or PDF reader. It features **Global Hotkeys**, allowing you to play, pause, and seek without ever having to `Alt+Tab` away from your reading material.

## ✨ What can it do?

*   **Global Hotkeys:** Control playback while your focus remains on your browser or document.
    *   `Spacebar`: Toggle Play/Pause
    *   `A`: Rewind 5 seconds
    *   `D`: Forward 5 seconds
*   **Resume Playback:** Automatically remembers exactly where you left off, even if you close the app.
*   **Drag & Drop:** Simply drag an MP3 file onto the window to start playing.

## 🛠️ Prerequisites

You need **Python 3.x** installed. The player relies on a few external libraries for audio handling and hotkeys.

### Installation

1.  Clone this repository or download the script.
2.  Install the required dependencies using pip:

```bash
pip install tkinterdnd2 pygame mutagen pynput
```

*(Note: `tkinter` usually comes pre-installed with Python. If you are on Linux, you may need to install `python3-tk` separately).*

## 🚀 How to Run

Simply run the Python script:

```bash
python app.pyw
```

## 📖 Usage Guide

1.  **Launch the App.**
2.  **Load Audio:** Click the **Browse** button or simply **Drag and Drop** an `.mp3` file into the window.
3.  **Multitask:** Switch to your web browser or ebook reader.
4.  **Control:**
    *   Press **Space** to pause when you need to focus on a complex paragraph.
    *   Press **A** to quickly jump back if you missed a sentence.
    *   Press **D** to skip boring parts.

## 💾 Progress Saving
The app creates a small file named `player_cache.json` in the same directory. This stores the file path and timestamp of your last session, so you can close the player and resume your book immediately next time.

## 📦 Building an EXE (Optional)
If you want to run this without opening a terminal every time, you can bundle it into a standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --hidden-import=tkinterdnd2 app.pyw
```
*(You will find the executable in the `dist` folder).*

## 📄 License
Feel free to modify and use this for your own personal projects.
