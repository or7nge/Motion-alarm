import cv2
import pyautogui
import time
from playsound import playsound

DETECTION_LEVEL = 10


# Motion detection
def motion_detection():
    # Read the first frame
    last_frame = None
    # Read the video
    video = cv2.VideoCapture(1)
    active = False

    # Loop over the frames of the video
    while True:
        # Read the current frame
        check, frame = video.read()
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert the grayscale frame to GaussianBlur
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        # If the first frame is None, initialize it
        if last_frame is None:
            last_frame = blurred
            continue
        # Compute the absolute difference between the current frame and first frame
        delta_frame = cv2.absdiff(last_frame, blurred)
        # If the difference between current frame and when it was static is greater than 30 it will show white color(255)
        thresh_frame = cv2.threshold(
            delta_frame, DETECTION_LEVEL, 255, cv2.THRESH_BINARY
        )[1]
        # Dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
        (cnts, _) = cv2.findContours(
            thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        # Loop over the contours
        for contour in cnts:
            if not active:
                break
            if cv2.contourArea(contour) < 1000:
                continue

            print("MOTION")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            pyautogui.keyUp("alt")
            playsound("alarm.wav")
            active = False

        # Display the resulting frame
        if active:
            cv2.imshow("Frame", frame)
        else:
            cv2.imshow("Frame", gray)
        last_frame = blurred

        if cv2.waitKey(1) & 0xFF == ord(" "):
            active = not active
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        # If q


motion_detection()
