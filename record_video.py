"""Record a video using OpenCV."""

import os
import time
import cv2

# Set capture index, resolution, frame rate, duration and video type
CAMERA_INDEX = 2            # {0, 2}
RESOLUTION = 'FHD'          # {360p, 480p, 540p, HD/720p, FHD/1080p, 4K}
FPS = 30                    # {30, 60}
DURATION = 20               # seconds
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


def main():
    """Main"""
    video_writer = cv2.VideoWriter(OUTPUT_VIDEO_FILE, FOURCC, FPS, (WIDTH, HEIGHT))
    num_frames = 0
    timekeeping = [0, 0]
    # Show the camera input and record video
    while (capture.isOpened() and num_frames < DURATION*FPS):
        timekeeping = [timekeeping[-1], cv2.getTickCount()]
        ret, frame = capture.read()
        if ret:

            num_frames += 1
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            current_time_seconds = time.time()
            formatted_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(current_time_seconds))

            text = formatted_time + f"{current_time_seconds :.3f} "[-4:] + f"{WIDTH}x"\
                   f"{HEIGHT}@{FPS}fps. Frame #{num_frames}. Sampling rate: "\
                   f"{round(cv2.getTickFrequency()/(timekeeping[-1]-timekeeping[0]), 3)} fps"

            frame = put_text(frame, text, font_scale, font_thickness)

            #cv2.imshow("Camera Feed", frame)
            # Write each frame to the video file
            video_writer.write(frame)
            print(f"Process {os.getpid()} writing #{num_frames} frame.")
            # print({num_frames})

            # key = cv2.waitKey(1)
            # if key == ord('q') or num_frames == 120:
            # if num_frames == 60:
                # print("")
                # break

    # Release the capture, video writer, and close all windows
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
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
    main()
        