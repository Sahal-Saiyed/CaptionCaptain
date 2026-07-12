import cv2
import base64
import math
from typing import List


class VideoProcessor:
    def __init__(self, target_frames: int = 8, max_width: int = 1024):
        self.target_frames = target_frames
        self.max_width = max_width

    def _resize_frame(self, frame):
        """Resizes the frame to reduce Base64 payload size while maintaining aspect ratio."""
        height, width = frame.shape[:2]
        if width > self.max_width:
            scaling_factor = self.max_width / float(width)
            new_height = int(height * scaling_factor)
            frame = cv2.resize(frame, (self.max_width, new_height), interpolation=cv2.INTER_AREA)
        return frame

    def _frame_to_base64(self, frame) -> str:
        """Encodes an OpenCV frame to a base64 string."""
        # Compress the image to JPEG with 80% quality to further reduce payload size
        success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not success:
            raise ValueError("Failed to encode frame to JPEG.")

        b64_string = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{b64_string}"

    def extract_base64_frames(self, video_url: str) -> List[str]:
        """Opens a video stream, calculates intervals, and returns mathematically spaced base64 frames."""
        print(f"Extracting {self.target_frames} frames from: {video_url}")

        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            print(f"CRITICAL ERROR: Could not open video stream for {video_url}")
            return []

        # Get total frame count to calculate our extraction intervals
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            print("CRITICAL ERROR: Video has no frames or is unreadable.")
            cap.release()
            return []

        # Calculate the exact frame numbers we want to grab
        interval = math.floor(total_frames / self.target_frames)
        target_frame_indices = [i * interval for i in range(self.target_frames)]

        # Ensure we don't accidentally ask for a frame beyond the video length
        target_frame_indices = [min(idx, total_frames - 1) for idx in target_frame_indices]

        base64_frames = []

        for frame_idx in target_frame_indices:
            # Tell OpenCV to jump instantly to the specific frame timestamp
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            success, frame = cap.read()

            if success:
                resized_frame = self._resize_frame(frame)
                b64_str = self._frame_to_base64(resized_frame)
                base64_frames.append(b64_str)
            else:
                print(f"Warning: Failed to read frame {frame_idx}. Skipping.")

        cap.release()
        print(f"Successfully extracted {len(base64_frames)} base64 frames.")
        return base64_frames


# --- Local Testing Block ---
if __name__ == "__main__":
    # We will test this using the "Urban traffic" video URL provided in the hackathon guide
    test_url = "https://storage.googleapis.com/amd-hackathon-clips/1860079-uhd_2560_1440_25fps.mp4"

    processor = VideoProcessor(target_frames=5)
    frames = processor.extract_base64_frames(test_url)

    if frames:
        print("\nTest successful! Here is a tiny snippet of the first base64 frame payload:")
        # Print just the first 100 characters so it doesn't flood your terminal
        print(f"{frames[0][:100]}...")
    else:
        print("Test failed. No frames extracted.")