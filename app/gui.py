import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

from src.bikefit.bikefit import BikeFit
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

        self.bikefit = BikeFit()
        self.input_player.add_listener(self.analise_frame)
        self.input_player.recording_changed.connect(self.on_recording_changed)

        # Controls layout
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_source)
        self.main_layout.addWidget(self.load_button)

    def on_recording_changed(self, is_recording):
        self.video_file_radio.setEnabled(not is_recording)
        self.webcam_radio.setEnabled(not is_recording)
        self.load_button.setEnabled(not is_recording)

    async def analise_frame(self, frame):
        _, angles = await self.bikefit.analise_cyclist_frame(frame)
        if angles:
            print(angles)

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
