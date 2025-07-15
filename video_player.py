"""Play and control a video frame by frame"""

import cv2


# Set control parameters
VIDEO_PATH = "/Captures/sample.avi"

capture = cv2.VideoCapture(VIDEO_PATH)
# [fps] and total frames of video
CAMERA_FPS = round(capture.get(5))
TOTAL_FRAMES = capture.get(cv2.CAP_PROP_FRAME_COUNT)

video_handling = {'pause' : [ord("p"), ord("P"), ord("π"), ord("Π"), ord(" ")],
                'forward': [ord("f"), ord("F"), ord("φ"), ord("Φ")],
                'backward': [ord("b"), ord("B"), ord("β"), ord("Β")],
                'quit' : [ord("q"), ord("Q"), ord(";"), 27]
                }


def show_video(video):
    """Show the video"""
     # Read a frame from the video
    ret, color_frame = video.read()

    if ret:
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        font_scaling = width//1920
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video.get(cv2.CAP_PROP_FPS))

        current_time_msec = video.get(cv2.CAP_PROP_POS_MSEC)/1000

        text =  f"Time in video: {current_time_msec :.3f} s | {width}x"\
                f"{height}@{fps}fps | Frame #{video.get(cv2.CAP_PROP_POS_FRAMES)}"

        color_frame = cv2.putText(color_frame, text, (50*font_scaling, 50*font_scaling),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1*font_scaling, (0, 240, 0),
                                    2*font_scaling, cv2.LINE_AA)
        color_frame = cv2.resize(color_frame, (1280, 720))

        # Resize and display the annotated frame
        cv2.imshow('Video', color_frame)
    else:
        # Repeat the loop if the end of the video is reached
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)


def main():
    """Main function"""

    # Loop through the video frames
    while capture.isOpened():

        show_video(capture)

        key = cv2.waitKey(1)
        # Pause the loop if 'p' or 'P' or Space character is pressed
        if key in video_handling["pause"]:
            # wait until any key is pressed
            key = cv2.waitKey(-1)
        # Move backwards or forwards the loop if 'b'/'B' or 'f'/'F' is pressed
        while key in video_handling["backward"] or key in video_handling["forward"]:
            if key in video_handling["backward"]:
                new_position_frame = -2+int(capture.get(cv2.CAP_PROP_POS_FRAMES))
            else:
                new_position_frame = 0+int(capture.get(cv2.CAP_PROP_POS_FRAMES))
            new_position_frame %= (TOTAL_FRAMES+1-0)
            capture.set(cv2.CAP_PROP_POS_FRAMES, new_position_frame)
            show_video(capture)
            key = cv2.waitKey(-1)
        # Break the loop if 'q' or 'Q' or Esc character is pressed
        if key in video_handling["quit"]:
            break

    # Release the video video object and close the display window
    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
