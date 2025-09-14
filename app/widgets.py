import cv2
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer


class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.video_capture = None

        # Create widgets
        self.video_label = QLabel("No Video Loaded")
        self.video_label.setAlignment(Qt.AlignCenter)

        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.time_slider = QSlider(Qt.Horizontal)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.video_label)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        layout.addLayout(controls_layout)
        layout.addWidget(self.time_slider)

        # Timer for playback
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.next_frame)

        # Connect signals
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.time_slider.valueChanged.connect(self.slider_value_changed)

    def load_video(self, video_capture: cv2.VideoCapture):
        self.video_capture = video_capture
        frame_count = self.get_frame_count()
        self.time_slider.setRange(0, frame_count - 1)
        self.set_frame(0)

    def play_video(self):
        if self.video_capture:
            fps = self.get_fps()
            if fps > 0:
                self.timer.start(1000 / fps)

    def pause_video(self):
        self.timer.stop()

    def next_frame(self):
        if self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                current_frame = int(
                    self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
                )
                self.time_slider.setValue(current_frame)
                self.display_frame(frame)
            else:
                self.timer.stop()

    def slider_value_changed(self, value):
        self.set_frame(value)

    def set_frame(self, frame_number):
        if self.video_capture:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video_capture.read()
            if ret:
                self.display_frame(frame)
                return frame
        return None

    def display_frame(self, frame):
        qt_image = self.convert_cv_to_qt(frame)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def convert_cv_to_qt(self, cv_img):
        """Convert from an opencv image to QImage."""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
        )
        return convert_to_Qt_format.scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio
        )

    def get_frame_count(self):
        if self.video_capture:
            return int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0

    def get_fps(self):
        if self.video_capture:
            return self.video_capture.get(cv2.CAP_PROP_FPS)
        return 0
