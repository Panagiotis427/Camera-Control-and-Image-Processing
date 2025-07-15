"""Hikrobot Camera Control."""

import os
import sys
import ctypes
import numpy as np
import MvCameraControl_class as MvCC
import cv2
import time

# Manually set the correct path to the Hikrobot DLLs
sdk_runtime_path = r"C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64"

if not os.path.exists(os.path.join(sdk_runtime_path, "MvCameraControl.dll")):
    raise FileNotFoundError(f"Cannot find MvCameraControl.dll in {sdk_runtime_path}")

# Add DLL path to the environment
os.environ["PATH"] += os.pathsep + sdk_runtime_path

# Load the DLL manually
MvCamCtrldll = ctypes.WinDLL(os.path.join(sdk_runtime_path, "MvCameraControl.dll"))

# Now import the MVS Camera Control class
sys.path.append(r"C:\Program Files\MVS\Development\Samples\Python\MvImport")


IMAGE_RESIZE_FACTOR = 0.3
CAMERA_SETTINGS = {
    "Width": None,
    "Height": None,
    "AcquisitionFrameRate": None,
    "ExposureTime": 50000,
    "Gain": 10,
    "Brightness": None,
    "Gamma": None,
    "TriggerMode": None,  # Trigger mode value (Off, On, etc.)
    "PixelFormat": None  # Pixel format value (Mono8, BayerBG8, etc.)
}
# width=1280, height=720, fps=30, exposure_time=20000, gain=10, brightness=100,
# gamma=1.2, trigger_mode=0x8000, pixel_format=0x02100014
RECORD_VIDEO = True
OUTPUT_FILE = f"hikrobot_video_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}.avi"
DURATION = 4 #seconds


def configure_hikrobot_camera(camera):
    """
    Adjusts the camera settings such as resolution, FPS, brightness, exposure, and gain.
    """

    if all(value is None for value in CAMERA_SETTINGS.values()):
        print("No camera settings provided. Using default settings.")
        ret = camera.MV_CC_SetCommandValue("UserSetLoad")
        if ret != 0:
            print(f"Failed to restore factory settings: {ret}")
        else:
            print("Factory settings restored successfully!")

    for setting, value in CAMERA_SETTINGS.items():
        
        if value is None:
            continue

        ret = camera.MV_CC_SetIntValue(setting, value)
        if ret != 0:
            ret = camera.MV_CC_SetFloatValue(setting, value)
            if ret != 0:
                ret = camera.MV_CC_SetEnumValue(setting, value)
                if ret != 0:
                    print(f"Failed to set {setting} to {value}")
                    return

    print("Camera settings applied successfully!")

    # Save and load custom settings
    """
    camera.MV_CC_SetCommandValue("UserSetSave")
    print("Custom settings saved!")

    camera.MV_CC_SetCommandValue("UserSetLoad")
    print("Custom settings loaded!")
    """

# Function to process video frames in real-time
def main(duration=DURATION):
    # --Control Camera
    # Create a device list
    pstDevList = MvCC.MV_CC_DEVICE_INFO_LIST()
    nTLayerType = MvCC.MV_GIGE_DEVICE | MvCC.MV_USB_DEVICE

    # Enumerate devices
    ret = MvCC.MvCamera.MV_CC_EnumDevices(nTLayerType, pstDevList)
    if ret != 0 or pstDevList.nDeviceNum == 0:
        print("No camera is available:", ret, pstDevList.nDeviceNum)
        sys.exit()

    # Choose the first camera
    nDeviceIndex = 0
    stDevInfo = ctypes.cast(pstDevList.pDeviceInfo[nDeviceIndex], ctypes.POINTER(MvCC.MV_CC_DEVICE_INFO)).contents

    # Create camera handle
    camera = MvCC.MvCamera()
    ret = camera.MV_CC_CreateHandle(stDevInfo)
    if ret != 0:
        print("create handle fail! ret[0x%x]" % ret)
        sys.exit()

    # Open device and start grabbing
    ret = camera.MV_CC_OpenDevice(MvCC.MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("open device fail! ret[0x%x]" % ret)
        sys.exit()

    # Configure camera settings
    configure_hikrobot_camera(camera)

    ret = camera.MV_CC_StartGrabbing()
    if ret != 0:
        print("start grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    # --Control Camera

    if RECORD_VIDEO:
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        # Create instances to store the retrieved values
        stFloatValue = MvCC.MVCC_FLOATVALUE()
        stIntValue = MvCC.MVCC_INTVALUE()

        # Retrieve the frame rate, width, and height
        ret = camera.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatValue)
        if ret != 0:
            print("Failed to get frame rate! ret[0x%x]" % ret)
            sys.exit()
        fps = stFloatValue.fCurValue

        ret = camera.MV_CC_GetIntValue("Width", stIntValue)
        if ret != 0:
            print("Failed to get frame width! ret[0x%x]" % ret)
            sys.exit()
        frame_width = stIntValue.nCurValue

        ret = camera.MV_CC_GetIntValue("Height", stIntValue)
        if ret != 0:
            print("Failed to get frame height! ret[0x%x]" % ret)
            sys.exit()
        frame_height = stIntValue.nCurValue

        # Ensure fps is valid
        if fps < 1:
            print("Invalid frame rate! fps must be >= 1")
            sys.exit()

        out = cv2.VideoWriter(OUTPUT_FILE, fourcc, fps, (frame_width, frame_height))
        print(f"Recording video for {duration} seconds...")
        start_time = time.time()
  
    frame_index = 0

    if not RECORD_VIDEO:
        start_time = 0
        DURATION = np.inf
     
    while time.time() - start_time < duration:
        # --Capture Frame
        # Create an empty container for image data and information
        stOutFrame = MvCC.MV_FRAME_OUT()
        ctypes.memset(ctypes.byref(stOutFrame), 0, ctypes.sizeof(stOutFrame))
        
        # Get one frame of image
        ret = camera.MV_CC_GetImageBuffer(stFrame=stOutFrame, nMsec=10000)

        # Process the captured frame
        if ret != 0:
            print("No Image is captured[0x%x]" % ret)
            continue  # Skip the current iteration if no image is captured

        if stOutFrame.pBufAddr is not None:
            # Copy the raw image buffer
            buf_cache = (ctypes.c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
            ctypes.memmove(ctypes.byref(buf_cache), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)

            # Convert buffer to a NumPy array
            bayer_image = np.frombuffer(buf_cache, dtype=np.uint8).reshape(
                (stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nWidth))

            # Demosaicing using OpenCV
            frame = cv2.cvtColor(bayer_image, cv2.COLOR_BAYER_RG2RGB)

            # Resize the image
            result_nparray = cv2.resize(frame, (0, 0), fx=IMAGE_RESIZE_FACTOR, fy=IMAGE_RESIZE_FACTOR)

            if RECORD_VIDEO:
                # Write frame to video
                out.write(frame)

            # Increment frame index
            frame_index += 1

            # Display the resized image using OpenCV
            cv2.imshow('Camera Feed', result_nparray)

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Free the image buffer
            camera.MV_CC_FreeImageBuffer(stOutFrame)
            # --Capture Frame

    # Stop grabbing and clean up
    camera.MV_CC_StopGrabbing()
    camera.MV_CC_CloseDevice()
    camera.MV_CC_DestroyHandle()
    cv2.destroyAllWindows()
    if RECORD_VIDEO:
        out.release()
        print(f"Recording complete! Video saved as {OUTPUT_FILE}!")


if __name__ == "__main__":
    main()
