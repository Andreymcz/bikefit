import asyncio
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QRadioButton,
)
import qasync

from widgets import VideoPlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bikefit GUI")
        self.resize(1024, 768)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Source selection
        self.source_layout = QHBoxLayout()
        self.video_file_radio = QRadioButton("Video File")
        self.webcam_radio = QRadioButton("Webcam")
        self.video_file_radio.setChecked(True)
        self.source_layout.addWidget(self.video_file_radio)
        self.source_layout.addWidget(self.webcam_radio)
        self.main_layout.addLayout(self.source_layout)

        # Video player
        self.input_player = VideoPlayer()
        self.main_layout.addWidget(self.input_player)

        # Controls layout
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_source)
        self.main_layout.addWidget(self.load_button)

    def load_source(self):
        if self.video_file_radio.isChecked():
            self.load_video()
        else:
            self.input_player.load_webcam()

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_name:
            self.input_player.load_video(file_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()
