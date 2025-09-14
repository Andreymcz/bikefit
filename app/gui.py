import sys
import cv2
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QSlider,
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer

from bikefit import BikeFit, Analysis


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bikefit GUI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        self.layout.addWidget(self.load_button)

        self.video_label = QLabel("No video loaded")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        self.layout.addWidget(self.pause_button)

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.valueChanged.connect(self.slider_value_changed)
        self.layout.addWidget(self.time_slider)

        self.video_capture = None
        self.bikefit_analyzer = None
        self.analysis = Analysis()
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

    def play_video(self):
        if self.video_capture:
            fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.timer.start(1000 / fps)

    def pause_video(self):
        self.timer.stop()

    def next_frame(self):
        if self.video_capture:
            current_frame = self.time_slider.value()
            if current_frame < self.time_slider.maximum():
                self.time_slider.setValue(current_frame + 1)
            else:
                self.timer.stop()

    def slider_value_changed(self, value):
        self.display_frame(value)

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_name:
            self.video_capture = cv2.VideoCapture(file_name)
            self.bikefit_analyzer = BikeFit(cv2.VideoCapture(file_name))
            self.bikefit_analyzer.on_new_frame(self.update_analysis)
            self.bikefit_analyzer.start_analysis()
            frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.time_slider.setRange(0, frame_count - 1)
            self.display_frame(0)

    def update_analysis(self, frame_number, joints, angles):
        self.analysis.joints[frame_number] = joints
        self.analysis.angles[frame_number] = angles

    def display_frame(self, frame_number):
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video_capture.read()
            if ret:
                self.draw_landmarks(frame, frame_number)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)

    def draw_landmarks(self, frame, frame_number):
        if frame_number in self.analysis.joints:
            joints = self.analysis.joints[frame_number]
            h, w, _ = frame.shape
            for joint_name, (x, y, visibility) in joints.items():
                if visibility > 0.5:
                    cv2.circle(frame, (int(x * w), int(y * h)), 5, (0, 255, 0), -1)

        if frame_number in self.analysis.angles:
            angles = self.analysis.angles[frame_number]
            y_offset = 30
            for angle_name, angle_value in angles.items():
                cv2.putText(
                    frame,
                    f"{angle_name}: {angle_value:.2f}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                y_offset += 30


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
