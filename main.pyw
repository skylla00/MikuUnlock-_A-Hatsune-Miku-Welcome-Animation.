import os
import sys

import pygame
from PyQt6.QtCore import QByteArray, QTimer, QPropertyAnimation
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt


app = QApplication(sys.argv)

script_dir = os.path.dirname(os.path.abspath(__file__))

gif_path = next(
    os.path.join(root, file)
    for root, dirs, files in os.walk(script_dir)
    if ".venv" not in dirs
    for file in files
    if os.path.basename(root).lower() == "images" and file.lower().endswith(".gif")
)
audio_path = next(
    os.path.join(root, file)
    for root, dirs, files in os.walk(script_dir)
    if ".venv" not in dirs
    for file in files
    if os.path.basename(root).lower() == "audio"
    and file.lower().endswith((".mp3", ".wav", ".ogg"))
)

movie = QMovie(gif_path)
movie.jumpToFrame(0)
gif_size = movie.frameRect().size()

window = QWidget()
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
    screen.bottom() - gif_size.height() - 15
)

pygame.mixer.init()
pygame.mixer.music.load(audio_path)
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

QTimer.singleShot(2400, start_fade_out)
QTimer.singleShot(3000, app.quit)

sys.exit(app.exec())