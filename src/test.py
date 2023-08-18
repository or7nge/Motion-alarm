import cv2
import pyautogui
from playsound import playsound


class MotionDetector:
    def __init__(self, detection_level):
        self.video = cv2.VideoCapture(1)
        self.last_frame = None
        self.active = False
        self.detection_level = detection_level

        # Create a button
        self.button = pyautogui.create_button(
            text="Activate/Deactivate Motion Detection",
            callback=self.activate_deactivate_motion_detection,
        )

    def motion_detected(self):
        print("MOTION")
        playsound("res/alarm.wav", 0)
        self.active = False

    def activate_deactivate_motion_detection(self):
        self.active = not self.active

    def camera_loop(self):
        while True:
            # Read the current frame
            check, frame = self.video.read()
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Convert the grayscale frame to GaussianBlur
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)
            # If the first frame is None, initialize it
            if self.last_frame is None:
                self.last_frame = blurred

            # Compute the absolute difference between the current frame and first frame
            delta_frame = cv2.absdiff(self.last_frame, blurred)
            # If the difference between current frame and when it was static is greater than 30 it will show white color(255)
            thresh_frame = cv2.threshold(delta_frame, self.detection_level, 255, cv2.THRESH_BINARY)[1]
            # Dilate the thresholded image to fill in holes, then find contours on thresholded image
            thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop over the contours
            for contour in cnts:
                if not self.active:
                    break
                if cv2.contourArea(contour) >= 1000:
                    self.motion_detected()

            # Display the resulting frame
            if self.active:
                cv2.imshow("Motion detection", frame)
            else:
                cv2.imshow("Motion detection", gray)
            self.last_frame = blurred

            # Check if the button is clicked
            if pyautogui.is_button_pressed(self.button):
                self.activate_deactivate_motion_detection()
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


if __name__ == "__main__":
    detector = MotionDetector(10)
    detector.camera_loop()
