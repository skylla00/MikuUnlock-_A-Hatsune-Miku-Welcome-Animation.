import os
import sys
import ctypes
from ctypes import wintypes

import pygame
from PyQt6.QtCore import (
    QByteArray,
    QAbstractNativeEventFilter,
    QTimer,
    QPropertyAnimation,
    Qt,
)
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QApplication, QLabel, QWidget


kernel32 = ctypes.windll.kernel32
kernel32.SetLastError(0)
mutex_handle = kernel32.CreateMutexW(
    None, True, "Local\\OhayoooMikuUnlock"
)
if kernel32.GetLastError() == 183:
    sys.exit(0)

app = QApplication(sys.argv)

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
base_dir = getattr(sys, "_MEIPASS", script_dir)

gif_path = next(
    os.path.join(root, file)
    for root, dirs, files in os.walk(base_dir)
    if ".venv" not in dirs
    for file in files
    if os.path.basename(root).lower() == "images"
    and file.lower().endswith(".gif")
)
audio_path = next(
    os.path.join(root, file)
    for root, dirs, files in os.walk(base_dir)
    if ".venv" not in dirs
    for file in files
    if os.path.basename(root).lower() == "audio"
    and file.lower().endswith((".mp3", ".wav", ".ogg"))
)

if getattr(sys, "frozen", False):
    startup_command = os.path.abspath(sys.executable)
else:
    pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if os.path.isfile(pythonw_path):
        executable = pythonw_path
    else:
        executable = sys.executable
    startup_command = (
        f'"{os.path.abspath(executable)}" '
        f'"{os.path.abspath(sys.argv[0])}"'
    )

try:
    import winreg
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    ) as run_key:
        winreg.SetValueEx(
            run_key,
            "MikuUnlock",
            0,
            winreg.REG_SZ,
            startup_command,
        )
except (ImportError, OSError):
    pass

pygame.mixer.init()
pygame.mixer.music.load(audio_path)

preloaded_movie = QMovie(gif_path)
preloaded_movie.jumpToFrame(0)
gif_size = preloaded_movie.frameRect().size()


def play_animation():
    if getattr(app, "miku_window", None) is not None:
        return

    movie = preloaded_movie
    movie.jumpToFrame(0)

    window = QWidget()
    app.miku_window = window
    window.setWindowFlags(
        Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Tool
    )
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.setWindowOpacity(0.0)

    label = QLabel(window)
    label.resize(gif_size)
    label.setMovie(movie)
    label.setScaledContents(True)
    window.resize(gif_size)

    screen = app.primaryScreen().availableGeometry()
    window.move(
        screen.center().x() - gif_size.width() // 2,
        screen.bottom() - gif_size.height() - 15,
    )
    window.movie = movie
    window.movie = movie
    pygame.mixer.music.play()
    window.show()
    movie.start()

    fade_in = QPropertyAnimation(window, QByteArray(b"windowOpacity"))
    fade_in.setDuration(600)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.start()
    window.fade_in = fade_in

    def start_fade_out():
        fade_out = QPropertyAnimation(window, QByteArray(b"windowOpacity"))
        fade_out.setDuration(600)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.start()
        window.fade_out = fade_out

    def close_animation():
        window.close()
        movie.stop()
        pygame.mixer.music.stop()
        app.miku_window = None

    QTimer.singleShot(2400, start_fade_out)
    QTimer.singleShot(3000, close_animation)


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


class SessionEventFilter(QAbstractNativeEventFilter):
    WM_WTSSESSION_CHANGE = 0x02B1
    WTS_SESSION_UNLOCK = 8
    NOTIFY_FOR_THIS_SESSION = 0

    def __init__(self):
        super().__init__()

    def nativeEventFilter(self, event_type, message):
        try:
            native_message = ctypes.cast(
                int(message), ctypes.POINTER(MSG)
            ).contents
            if (
                native_message.message == self.WM_WTSSESSION_CHANGE
                and native_message.wParam == self.WTS_SESSION_UNLOCK
            ):
                if getattr(app, "unlock_timer", None) is None:
                    app.unlock_timer = QTimer()
                    app.unlock_timer.setSingleShot(True)
                    app.unlock_timer.timeout.connect(play_animation)
                app.unlock_timer.start(1000)
        except (TypeError, ValueError, ctypes.ArgumentError):
            pass
        return False, 0


class SessionMonitor(QWidget):
    def __init__(self, event_filter):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Tool)
        self.hide()
        self.event_filter = event_filter

        ctypes.windll.wtsapi32.WTSRegisterSessionNotification(
            int(self.winId()), event_filter.NOTIFY_FOR_THIS_SESSION
        )

    def closeEvent(self, event):
        ctypes.windll.wtsapi32.WTSUnRegisterSessionNotification(
            int(self.winId())
        )
        app.removeNativeEventFilter(self.event_filter)
        super().closeEvent(event)


session_event_filter = SessionEventFilter()
app.installNativeEventFilter(session_event_filter)
session_monitor = SessionMonitor(session_event_filter)

sys.exit(app.exec())