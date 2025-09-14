import pytest
import cv2
import time

from bikefit import BikeFit, Analysis


@pytest.fixture
def bikefit():
    # Initialize BikeFit with a video source
    video_path = "data/pretinha_samples.mp4"
    video_source = cv2.VideoCapture(video_path)
    assert video_source.isOpened(), f"Failed to open video: {video_path}"
    return BikeFit(video_source=video_source)


def test_collect_joints_angles(bikefit: BikeFit):
    """
    Test the main analysis workflow: start, wait, stop, and get analysis.
    """
    # Start the analysis
    bikefit.start_analysis()

    # Let the analysis run for a few seconds
    time.sleep(5)

    # Stop the analysis
    bikefit.stop_analysis()

    # Get the analysis results
    analysis = bikefit.get_analysis()

    # Assert that the analysis object is valid
    assert isinstance(analysis, Analysis)

    # Assert that some frames were processed
    assert analysis.frame_count > 0, "No frames were processed."

    # Assert that joint data was collected
    assert len(analysis.joints) > 0, "No joint data was collected."
    assert len(analysis.joints) == analysis.frame_count

    # Assert that angle data was collected
    assert len(analysis.angles) > 0, "No angle data was collected."
    assert len(analysis.angles) == analysis.frame_count

    # Check the content of a single frame's data
    first_frame_number = next(iter(analysis.joints))
    first_frame_joints = analysis.joints[first_frame_number]
    first_frame_angles = analysis.angles[first_frame_number]

    # Check for specific joints
    expected_joints = [
        "left_shoulder", "left_elbow", "left_wrist",
        "left_hip", "left_knee", "left_ankle"
    ]
    for joint_name in expected_joints:
        assert joint_name in first_frame_joints
        # Check that joint data is a tuple of (x, y, visibility)
        assert isinstance(first_frame_joints[joint_name], tuple)
        assert len(first_frame_joints[joint_name]) == 3

    # Check for specific angles
    expected_angles = ["left_elbow", "left_knee"]
    for angle_name in expected_angles:
        assert angle_name in first_frame_angles
        # Check that angle data is a float
        assert isinstance(first_frame_angles[angle_name], float)




def test_should_notify_when_new_frame_is_processed(bikefit: BikeFit):
    """
    Test that the on_new_frame callback is invoked when a new frame is processed.
    """
    frames_processed = []

    def on_new_frame(frame_number: int, joints: dict, angles: dict):
        frames_processed.append(frame_number)

    bikefit.on_new_frame(on_new_frame)

    # Start the analysis
    bikefit.start_analysis()    

    # Let the analysis run for a few seconds
    time.sleep(5)

    # Stop the analysis
    bikefit.stop_analysis()

    # Assert that the callback was invoked at least once
    assert len(frames_processed) > 0, "The on_new_frame callback was not invoked."
    # Assert that at least 30 frames per second were processed
    frames_per_second = len(frames_processed) / 5
    assert frames_per_second > 25, f"Processed less than 25+ frames per second: {frames_per_second:.2f}"

    # Assert that frame numbers are sequential
    assert frames_processed == list(range(min(frames_processed), max(frames_processed) + 1)), "Frame numbers are not sequential."