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

        # Video player
        self.input_player = VideoPlayer()
        self.main_layout.addWidget(self.input_player)

        # Controls layout
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        self.main_layout.addWidget(self.load_button)

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
