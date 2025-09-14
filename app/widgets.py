import asyncio
import cv2
import numpy as np
from PySide6.QtCore import Qt, QUrl, Slot, Signal
from PySide6.QtMultimedia import (
    QCamera,
    QMediaPlayer,
    QMediaCaptureSession,
    QMediaDevices,
    QVideoFrame,
    QVideoSink,
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
    recording_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_sink = QVideoSink()
        self.video_sink.videoFrameChanged.connect(self.on_frame_changed)

        self.is_recording = False
        self.listeners = []

        self.camera = None
        self.capture_session = QMediaCaptureSession()
        self.source_type = None

        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.record_button = QPushButton("Record")
        self.time_slider = QSlider(Qt.Horizontal)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_widget)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.record_button)
        layout.addLayout(controls_layout)
        layout.addWidget(self.time_slider)

        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.record_button.clicked.connect(self.toggle_recording)
        self.time_slider.sliderMoved.connect(self.set_position)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def on_frame_changed(self, frame: QVideoFrame):
        print("on_frame_changed called")
        if self.is_recording and frame.isValid():
            print("Recording and frame is valid")
            # Map the video frame to get access to the image data
            image = frame.toImage()
            if image.format() != image.Format.Format_BGR888:
                image = image.convertToFormat(image.Format.Format_BGR888)

            # Create a copy of the data to avoid issues with the buffer
            ptr = image.bits()
            ptr.setsize(image.sizeInBytes())
            arr = np.array(ptr).reshape(image.height(), image.width(), 3).copy()

            for listener in self.listeners:
                asyncio.create_task(listener(arr))

    def toggle_recording(self):
        print("toggle_recording called")
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_button.setText("Stop")
            self.time_slider.setEnabled(False)
            self.play_video()
        else:
            self.record_button.setText("Record")
            if self.source_type == "file":
                self.time_slider.setEnabled(True)
            self.pause_video()
        self.recording_changed.emit(self.is_recording)

    def load_video(self, file_name: str):
        if self.is_recording:
            return
        if self.camera and self.camera.isActive():
            self.camera.stop()
        self.capture_session.setVideoSink(None)
        self.media_player.setVideoSink(self.video_sink)
        self.media_player.setVideoOutput(self.video_widget)
        self.source_type = "file"
        self.media_player.setSource(QUrl.fromLocalFile(file_name))
        self.play_button.setEnabled(True)
        self.time_slider.setEnabled(True)
        self.media_player.play()
        self.media_player.pause()

    def load_webcam(self):
        if self.is_recording:
            return
        self.media_player.setVideoSink(None)
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.capture_session.setVideoSink(self.video_sink)
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
