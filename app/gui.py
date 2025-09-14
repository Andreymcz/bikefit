import asyncio
import sys
import cv2
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
)
import qasync

from widgets import VideoPlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bikefit GUI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Video players layout
        video_layout = QHBoxLayout()
        self.input_player = VideoPlayer()
        self.analyzed_player = VideoPlayer()
        video_layout.addWidget(self.input_player)
        video_layout.addWidget(self.analyzed_player)
        self.main_layout.addLayout(video_layout)

        # Controls layout
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        self.main_layout.addWidget(self.load_button)

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_name:
            video_capture = cv2.VideoCapture(file_name)
            if video_capture.isOpened():
                self.input_player.load_video(video_capture)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()
