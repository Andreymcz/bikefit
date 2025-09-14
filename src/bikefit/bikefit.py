"""
This module contains the main BikeFit class for analyzing bike fitting videos.
"""

import threading
import time
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from bikefit.analysis import Analysis


class BikeFit:
    """
    A class to analyze bike fitting videos, detect human joints, and calculate angles.
    """

    def __init__(self, video_source: cv2.VideoCapture):
        """
        Initializes the BikeFit analyzer.

        Args:
            video_source: An initialized cv2.VideoCapture object.
        """
        self.video_source = video_source
        self._analysis = Analysis()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def start_analysis(self):
        """Starts the analysis in a separate thread."""
        if self._is_running:
            print("Analysis is already running.")
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run_analysis, daemon=True)
        self._thread.start()

    def stop_analysis(self):
        """Stops the analysis and waits for the thread to finish."""
        if not self._is_running:
            print("Analysis is not running.")
            return

        self._is_running = False
        if self._thread:
            self._thread.join()  # Wait for the thread to complete

    def get_analysis(self) -> Analysis:
        """
        Returns the analysis results.

        Returns:
            An Analysis object containing the collected data.
        """
        with self._lock:
            return self._analysis
        
    def on_new_frame(self, new_frame_callback):
        """
        Registers a callback function to be called on each new frame processed.

        Args:
            new_frame_callback: A callable that takes the current frame number and analysis data.
        """
        self._new_frame_callback = new_frame_callback

    def _calculate_angle(self, a, b, c):
        """Calculates the angle between three points (in degrees)."""
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def _run_analysis(self):
        """The main analysis loop that runs in a thread."""
        frame_number = 0
        while self._is_running:
            ret, frame = self.video_source.read()
            if not ret:
                print("End of video or cannot read frame.")
                self.stop_analysis()
                break

            # Convert the BGR image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process the image and find pose
            results = self.pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                frame_joints = {}
                frame_angles = {}

                # Get coordinates
                left_shoulder = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                ]
                left_elbow = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
                ]
                left_wrist = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y,
                ]
                left_hip = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y,
                ]
                left_knee = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y,
                ]
                left_ankle = [
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
                ]

                right_shoulder = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
                ]
                right_elbow = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
                ]
                right_wrist = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y,
                ]
                right_hip = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y,
                ]
                right_knee = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
                ]
                right_ankle = [
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
                ]

                # Store joint data
                frame_joints["left_shoulder"] = (left_shoulder[0], left_shoulder[1], landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility)
                frame_joints["left_elbow"] = (left_elbow[0], left_elbow[1], landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility)
                frame_joints["left_wrist"] = (left_wrist[0], left_wrist[1], landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].visibility)
                frame_joints["left_hip"] = (left_hip[0], left_hip[1], landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].visibility)
                frame_joints["left_knee"] = (left_knee[0], left_knee[1], landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].visibility)
                frame_joints["left_ankle"] = (left_ankle[0], left_ankle[1], landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility)

                frame_joints["right_shoulder"] = (right_shoulder[0], right_shoulder[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility)
                frame_joints["right_elbow"] = (right_elbow[0], right_elbow[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility)
                frame_joints["right_wrist"] = (right_wrist[0], right_wrist[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility)
                frame_joints["right_hip"] = (right_hip[0], right_hip[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].visibility)
                frame_joints["right_knee"] = (right_knee[0], right_knee[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility)
                frame_joints["right_ankle"] = (right_ankle[0], right_ankle[1], landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility)

                # Calculate angles
                left_elbow_angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
                left_knee_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
                right_elbow_angle = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
                right_knee_angle = self._calculate_angle(right_hip, right_knee, right_ankle)

                frame_angles["left_elbow"] = left_elbow_angle
                frame_angles["left_knee"] = left_knee_angle
                frame_angles["right_elbow"] = right_elbow_angle
                frame_angles["right_knee"] = right_knee_angle

                # Lock before updating shared analysis object
                with self._lock:
                    self._analysis.frame_count += 1
                    self._analysis.joints[frame_number] = frame_joints
                    self._analysis.angles[frame_number] = frame_angles
                # Call the new frame callback if set
                if hasattr(self, '_new_frame_callback'):
                    self._new_frame_callback(frame_number, frame_joints, frame_angles)

                frame_number += 1

            except Exception as e:
                # Landmark not found or other error
                pass

            # A small sleep to prevent CPU maxing out, and to simulate real-time processing
            time.sleep(1 / 60) # ~60 FPS

        # Release resources
        self.video_source.release()
        self.pose.close()
