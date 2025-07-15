"""Concatenate images to video using OpenCV."""

import os
import time
import cv2


# Set capture index, resolution, frame rate, duration and video type
FRAMES_DIR = "frames"       # directory containing frames
RESOLUTION = '4K'           # {360p, 480p, 540p, HD/720p, FHD/1080p, 4K}
FPS = 60                    # {30, 60}
DURATION = 3                # seconds
VIDEO_TYPE = 'avi'          # {avi, mp4}

# Define the video file and codec
TIMESTAMP = time.strftime("%Y%m%d_%H%M%S_", time.localtime(time.time()))
OUTPUT_VIDEO_FILE = f"videos/{TIMESTAMP}_{RESOLUTION}@{FPS}.{VIDEO_TYPE}"
CODEC = {'avi': 'MJPG', 'mp4': 'H264'}
FOURCC = cv2.VideoWriter_fourcc(*CODEC[VIDEO_TYPE])         # type: ignore

# Standard video resolutions, scaling
STD_RESOLUTIONS =  {
    "360p": (640, 360),
    "480p": (848, 480),
    "540p": (960, 540),
    "HD": (1280, 720), 
    "FHD": (1920, 1080),
    "2K": (2560, 1440),
    "4K": (3840, 2160)}
WIDTH, HEIGHT = STD_RESOLUTIONS[RESOLUTION][0], STD_RESOLUTIONS[RESOLUTION][1]

# List all files in the directory
frames = [f for f in os.listdir(FRAMES_DIR) if f.endswith(".png")]  # Assuming frames are .png

# Sort frames to ensure they are in correct order
frames.sort()

out = cv2.VideoWriter(OUTPUT_VIDEO_FILE, FOURCC, FPS, (WIDTH, HEIGHT))
# Concatenate frames to create video
for frame_name in frames:
    frame = cv2.imread(os.path.join(FRAMES_DIR, frame_name))
    out.write(frame)

# Release the video writer object
out.release()
