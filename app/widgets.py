import cv2
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtMultimedia import (
    QCamera,
    QMediaPlayer,
    QMediaCaptureSession,
    QMediaDevices,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
)


class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        self.camera = None
        self.capture_session = QMediaCaptureSession()
        self.capture_session.setVideoOutput(self.video_widget)
        self.source_type = None

        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.time_slider = QSlider(Qt.Horizontal)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_widget)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        layout.addLayout(controls_layout)
        layout.addWidget(self.time_slider)

        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.time_slider.sliderMoved.connect(self.set_position)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def load_video(self, file_name: str):
        if self.camera and self.camera.isActive():
            self.camera.stop()
        self.media_player.setVideoOutput(self.video_widget)
        self.source_type = "file"
        self.media_player.setSource(QUrl.fromLocalFile(file_name))
        self.play_button.setEnabled(True)
        self.time_slider.setEnabled(True)
        self.media_player.play()
        self.media_player.pause()

    def load_webcam(self):
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.capture_session.setVideoOutput(self.video_widget)
        self.source_type = "webcam"
        available_cameras = QMediaDevices.videoInputs()
        if not available_cameras:
            print("No webcam found.")
            return

        self.camera = QCamera(available_cameras[0])
        self.capture_session.setCamera(self.camera)
        self.play_button.setEnabled(True)
        self.time_slider.setEnabled(False)
        self.camera.start()

    def play_video(self):
        if self.source_type == "file":
            self.media_player.play()
        elif self.source_type == "webcam" and self.camera:
            self.camera.start()

    def pause_video(self):
        if self.source_type == "file":
            self.media_player.pause()
        elif self.source_type == "webcam" and self.camera:
            self.camera.stop()

    def set_position(self, position):
        if self.source_type == "file":
            self.media_player.setPosition(position)

    def position_changed(self, position):
        if self.source_type == "file":
            self.time_slider.setValue(position)

    def duration_changed(self, duration):
        if self.source_type == "file":
            self.time_slider.setRange(0, duration)

    def set_frame(self, frame_number):
        # This method might need adjustment depending on how you want to sync
        # with the analyzed video. For now, it seeks based on milliseconds.
        if self.source_type == "file" and self.media_player.duration() > 0:
            position = (
                frame_number
                / self.get_frame_count()
                * self.media_player.duration()
            )
            self.set_position(int(position))
        return None  # Returning None as we can't easily get the frame data here

    def get_frame_count(self):
        # This is an approximation. A more accurate way might be needed.
        if self.source_type == "file":
            video_capture = cv2.VideoCapture(
                self.media_player.source().toLocalFile()
            )
            if video_capture.isOpened():
                return int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0

    def get_fps(self):
        if self.source_type == "file":
            video_capture = cv2.VideoCapture(
                self.media_player.source().toLocalFile()
            )
            if video_capture.isOpened():
                return video_capture.get(cv2.CAP_PROP_FPS)
        return 0
