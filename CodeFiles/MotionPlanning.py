import cv2
import numpy as np
from CodeFiles import DriveRobot as dr, IK, PlatformDetection as pd
import TrackObjects as gt

station_position = np.array([0.05,  0.130,  0.02+0.25])


# For static Image
img = cv2.imread("Resources\\PlatformImg10.jpg")

# Get distortionless platform image
croppedImage, Scale = pd.platform(img)

# target_positions = np.empty(0,3)
# detect coordinates of the cubes to be picked
target_positions = np.array(gt.detectCubes(croppedImage, Scale))
# print("Target Coordinates: %s", % target_position[0])

# Sort all positions in ascending order of their asending order of distance from station
target_diff = np.empty()
for target in target_positions:
  target_diff = np.append(target_diff, np.linalg.norm(target-station_position), axis = 0)

target_positions_min = np.hstack(target_positions, target_diff)
columnIndex = 3
target_positions_min = target_positions_min[target_positions_min[:columnIndex].argsort()]

# Drive Robot Arm 
for target in target_positions_min[:-2]:
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
