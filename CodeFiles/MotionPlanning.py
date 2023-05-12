import cv2
from CodeFiles import DriveRobot as dr, IK, PlatformDetection as pd
import TrackObjects as gt


# For static Image
img = cv2.imread("Resources\\PlatformImg10.jpg")

# Get distortionless platform image
croppedImage, Scale = pd.platform(img)

# detect coordinates of the cubes to be picked
target_positions = gt.detectCubes(croppedImage, Scale)
# print("Target Coordinates: %s", % target_position[0])

for target in target_positions:
    target_config = IK.doIK(target)
    dr.drive2Position(target_config)


# # For Video Streaming
# url = "http://192.168.137.18:8080/video"
# cap = cv2.VideoCapture(url)
# while(True):
#     camera, img = cap.read()
#     if img is not None:
#         print("Detecting...")
#         pd.detect(img)
#
#     q = cv2.waitKey(1)
#     if q == ord("q"):
#         break