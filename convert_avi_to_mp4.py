"""Convert an AVI video file to MP4 format using OpenCV."""

import cv2

# 1. Open the source .avi file
input_path = '/Captures/sample.avi'
cap = cv2.VideoCapture(input_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video file {input_path}")

# 2. Prepare the .mp4 writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'H','2','6','4' if your build supports it
fps    = cap.get(cv2.CAP_PROP_FPS)
w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
output_path = input_path.replace('.avi','.mp4')
out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

# 3. Read & write frames
while True:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)

# 4. Clean up
cap.release()
out.release()
print(f"Conversion complete: saved to {output_path}")
