"""
This module contains the main BikeFit class for analyzing bike fitting videos.
"""

import asyncio
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

    def __init__(self):
        """
        Initializes the BikeFit analyzer.
        """
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

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

    async def analise_cyclist_frame(self, frame):
        """
        Analyzes a single frame to detect cyclist's joints and angles.

        Args:
            frame: The video frame to analyze.

        Returns:
            A tuple containing two dictionaries:
            - frame_joints: Joint data for the frame.
            - frame_angles: Angle data for the frame.
        """
        return await asyncio.to_thread(self._process_frame, frame)

    def _process_frame(self, frame):
        """
        The synchronous part of the frame analysis.
        """
        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and find pose
        results = self.pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        frame_joints = {}
        frame_angles = {}

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
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

        except Exception as e:
            # Landmark not found or other error
            pass

        return frame_joints, frame_angles
