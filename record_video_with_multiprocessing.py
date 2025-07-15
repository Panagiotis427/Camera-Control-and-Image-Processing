"""Record a video using OpenCV and Multiprocessing."""

import os
import time
import multiprocessing
import cv2


# Set capture index, resolution, frame rate, duration and video type
CAMERA_INDEX = 2            # {0, 2}
RESOLUTION = '4K'           # {360p, 480p, 540p, HD/720p, FHD/1080p, 4K}
FPS = 30                    # {30, 60}
DURATION = 2                # seconds
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

# Open capture
capture = cv2.VideoCapture(CAMERA_INDEX)
capture.set(cv2.CAP_PROP_FOURCC, FOURCC)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
capture.set(cv2.CAP_PROP_FPS, FPS)
scaling = int(max(capture.get(cv2.CAP_PROP_FRAME_WIDTH)/1920, 1))
font=cv2.FONT_HERSHEY_SIMPLEX
color = (0, 255, 0)
font_scale = scaling
font_thickness = 2*scaling


def put_text(frame, text, f_scale, thickness):
    """Put text on a frame"""

    # Get the width and height of the frame
    frame_height, frame_width = frame.shape[:2]

    # Calculate max width based on frame width
    max_width = int(0.9 * frame_width)

    # Calculate text size to check if it exceeds max_width
    text_size = cv2.getTextSize(text, font, f_scale, thickness)[0][0]

    # Check if text exceeds max_width
    if text_size > max_width:
        text_lines = []
        words = text.split()
        line = ''
        for word in words:
            # Check if adding this word exceeds max_width
            if cv2.getTextSize(line + ' ' + word, font, f_scale, thickness)[0][0] <= max_width:
                line += ' ' + word
            else:
                text_lines.append(line.strip())
                line = word
        if line:
            text_lines.append(line.strip())

        # Draw text on multiple lines
        x = int(0.05 * frame_width)  # Start drawing text from the left
        y = frame_height - int(0.05 * frame_height * len(text_lines))
        for line in text_lines:
            frame = cv2.putText(frame, line, (x, y), font, f_scale, color, thickness, cv2.LINE_AA)
            y += int(20 * scaling * thickness)  # Adjust line spacing
    else:
        # Draw text on a single line
        frame = cv2.putText(frame, text, (int(0.05 * frame_width), frame_height - \
                            int(0.05 * frame_height)), font, f_scale, color, thickness, cv2.LINE_AA)
    return frame


def read_frames(queue, stop_event):
    """Read frames"""

    read_frame_count = 0
    # while (capture.isOpened() and read_frame_count < DURATION*FPS and
        #    (cv2.getTickCount() - timekeeping)/cv2.getTickFrequency() <= 1/FPS):
    while capture.isOpened() and read_frame_count < DURATION*FPS:
        timekeeping = cv2.getTickCount()
        ret, image = capture.read()
        if not ret:
            break
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        read_frame_count += 1
        formatted_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
        text = f"RESOLUTION: {image.shape[1]}x{image.shape[0]}. FPS: {FPS}. " \
               f"FRAME: {read_frame_count}. TIME: {formatted_time}" +\
               f"{time.time():.3f}"[-4:] + f". PROCESS ID: {os.getpid()}. " \
               f"READING RATE: {round(cv2.getTickFrequency()/(cv2.getTickCount()-timekeeping), 3)} fps."

        image = put_text(image, text, font_scale, font_thickness)
        queue.put(image)
        print(f"Process {os.getpid()} reading #{read_frame_count} frame.")

    capture.release()
    stop_event.set()  # Signal that capture is complete

def write_frames(queue, stop_event):
    """Write frames"""
    out = cv2.VideoWriter(OUTPUT_VIDEO_FILE, FOURCC, FPS, (WIDTH, HEIGHT))
    write_frame_count = 0

    while not stop_event.is_set() or not queue.empty():
        if not queue.empty():
            frame = queue.get()
            out.write(frame)
            write_frame_count += 1
            print(f"Process {os.getpid()} writing #{write_frame_count} frame.")

    out.release()

if __name__ == "__main__":
    frame_queue = multiprocessing.Queue()
    stop = multiprocessing.Event()

    read_process = multiprocessing.Process(target=read_frames, args=(frame_queue, stop,))
    write_process = multiprocessing.Process(target=write_frames, args=(frame_queue, stop,))

    read_process.start()
    write_process.start()

    read_process.join()
    write_process.join()
