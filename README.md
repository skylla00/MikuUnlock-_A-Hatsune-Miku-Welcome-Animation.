# Ohayooo!

**Ohayooo!** is a Windows background application that displays and plays a short Hatsune Miku animation whenever the Windows session is unlocked.

<p align="center">
  <img src="assets/images/miku-hatsune-miku.gif" alt="Hatsune Miku unlock animation" width="360">
</p>

## How it works

1. The application runs silently in the background.
2. It listens for Windows session events through the Windows Terminal Services API.
3. It detects when the current Windows session is unlocked.
4. It waits briefly to ignore duplicate unlock events.
5. The GIF animation and audio are started together.
6. The window fades in, stays visible, fades out, and closes after approximately three seconds.

The application runs until it is closed manually and can be packaged as a single-file Windows executable.

## Features

- Runs in the background without a visible console window
- Detects real Windows unlock events
- Plays a GIF with synchronized audio
- Uses a transparent, borderless, always-on-top window
- Centers the animation horizontally above the taskbar
- Automatically closes after the configured animation duration
- Prevents multiple instances through a Windows named mutex
- Registers itself to start with the current Windows user
- Includes media and dependencies in the packaged executable

## Requirements

- Windows 11
- Python 3.13
- PyQt6
- pygame-ce
- PyInstaller

## Project structure

```text
.
|-- main.pyw
|-- assets/
|   |-- images/
|   |   `-- miku-hatsune-miku.gif
|   `-- audio/
|       `-- hello-miku.mp3
`-- dist/
    `-- MikuUnlock.exe
```

## Run from source

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

Install the dependencies:

```powershell
pip install PyQt6 pygame-ce pyinstaller
```

Run the application:

```powershell
.\\.venv\\Scripts\\pythonw.exe main.pyw
```

Lock the screen with `Win + L`, then unlock it. The animation should start after the configured unlock delay.

## Build the executable

From the project directory, run:

```powershell
.\\.venv\\Scripts\\pyinstaller.exe --clean --noconsole --onefile --name MikuUnlock --add-data "assets;assets" --hidden-import=pygame main.pyw
```

The finished executable is generated at:

```text
dist/MikuUnlock.exe
```

## Installation

1. Run `MikuUnlock.exe`.
2. Lock and unlock Windows to confirm that it works.
3. Close the process from Task Manager when testing is complete.

On first launch, the executable registers `MikuUnlock` under the current user's startup registry key:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

The executable can therefore start automatically after the user signs in. Windows Defender or another antivirus application may warn about a newly compiled unsigned executable; verify the downloaded file before running it.

## Timing

- Fade-in duration: 600 ms
- Fade-out starts at 2,400 ms
- Fade-out duration: 600 ms
- Window closes at approximately 3,000 ms

## Stop the application

Open **Task Manager**, find `MikuUnlock.exe`, and select **End task**.