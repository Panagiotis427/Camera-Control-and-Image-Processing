"""Sample frames from video(s) using OpenCV."""
import os
import cv2


def split_video_to_frames(full_video_path, sample_method):

    capture = cv2.VideoCapture(full_video_path)
    video_fps = capture.get(cv2.CAP_PROP_FPS)
    print(f"\nVideo name : {full_video_path[full_video_path.rfind('/')+1:-4]}\n"+
          f"Video fps : {video_fps}")
    FRAME_ID = 0

    while capture.isOpened():

        success, frame = capture.read()
        
        if success:

            FRAME_ID += 1

             # sample SAMPLE_RATIO frames per second or sample from START_TIME to END_TIME seconds
            if ((sample_method == 'sample_frequently' and not ((FRAME_ID*SAMPLE_RATIO) % int(video_fps))) or 
            (sample_method == 'sample_time_interval' and START_TIME < FRAME_ID/video_fps < END_TIME)):
                full_frame_path = full_video_path.replace("videos","frames").replace(".avi","")
                cv2.imwrite(f'{full_frame_path}_t{(FRAME_ID/int(video_fps)):07.3f}.png', frame)
        else:
            break

    capture.release()

if __name__ == "__main__":

    # Set videos directory 
    SAMPLE_RATIO = 0.3 # sample SAMPLE_RATIO frames per second 
    START_TIME = 0 # start from START_TIME seconds in the video
    END_TIME = 10 # end at END_TIME seconds in the video
    full_video_path = f"/sample.avi"

    split_video_to_frames(full_video_path, sample_method='sample_frequently')
