import cv2
from playsound import playsound
import time
import win32gui, win32com.client
import re


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__(self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

    def open_window(self, name):
        self.find_window_wildcard(f".*{name}.*")
        self.set_foreground()


class MotionDetector:
    def __init__(self):
        self.video = cv2.VideoCapture(1)
        self.last_frame = None
        self.frame = None
        self.active = False
        self.last_detection = 0
        self.detection_level = 10
        self.detection_time = 0.5
        self.target_game = "Valorant"
        self.window_mgr = WindowMgr()

    def motion_detected(self):
        if self.active:
            playsound("res/alarm2.wav", 0)
            self.window_mgr.open_window("Camera")

        # Add blue rectangle around the self.frame
        self.last_detection = time.time()
        self.active = False

    def switch_detection(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            if event == cv2.EVENT_RBUTTONDOWN and not self.active:
                try:
                    self.window_mgr.open_window(self.target_game)
                except:
                    pass
            self.active = not self.active

    def camera_loop(self):
        cv2.namedWindow("Camera")
        self.window_mgr.open_window("Camera")
        while True:
            # Read the current self.frame
            _, self.frame = self.video.read()
            # Convert the self.frame to grayscale
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            # Convert the grayscale self.frame to GaussianBlur
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)
            # If the first self.frame is None, initialize it
            if self.last_frame is None:
                self.last_frame = blurred

            # Compute the absolute difference between the current self.frame and first self.frame
            delta_frame = cv2.absdiff(self.last_frame, blurred)
            # If the difference between current self.frame and when it was static is greater than 30 it will show white color(255)
            thresh_frame = cv2.threshold(delta_frame, self.detection_level, 255, cv2.THRESH_BINARY)[1]
            # Dilate the thresholded image to fill in holes, then find contours on thresholded image
            thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop over the contours
            for contour in cnts:
                if cv2.contourArea(contour) >= 1000:
                    self.motion_detected()

            if self.active:
                cv2.putText(self.frame, "ON", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 12)
            else:
                cv2.putText(self.frame, "OFF", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 12)
            if time.time() - self.last_detection < self.detection_time:
                cv2.rectangle(self.frame, (0, 0), (self.frame.shape[1], self.frame.shape[0]), (255, 0, 0), 15)
            cv2.imshow("Camera", self.frame)
            self.last_frame = blurred

            cv2.setMouseCallback("Camera", self.switch_detection, param=self.frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break


if __name__ == "__main__":
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys(" ")  # Undocks my focus from Python IDLE
    detector = MotionDetector()
    detector.camera_loop()
