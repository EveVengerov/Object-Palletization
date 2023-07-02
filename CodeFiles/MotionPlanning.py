import cv2
import numpy as np
from CodeFiles import DriveRobot as dr, IK, PlatformDetection as pd
import TrackObjects as gt

station_position = np.array([0.05,  0.130,  0.02+0.25])


# For static Image
img = cv2.imread("../Resources/PlatformImg10.jpg")

# Get distortionless platform image
croppedImage, Scale = pd.platform(img)

# target_positions = np.empty(0,3)
# detect coordinates of the cubes to be picked
target_positions = np.array(gt.detectCubes(croppedImage, Scale))
size = target_positions.shape
if size[0] > 3:
  print("Too many Targets, maximum limit is 3")
else:
  # Sort all positions in ascending order of their asending order of distance from station
  target_diff = np.zeros(size[0])
  for i, target in zip(range(0,size[0]), target_positions):
    target_diff[i] = np.linalg.norm(target-station_position)

  target_diff = target_diff.reshape(-1, 1)
  print("List of Target diff: \n", target_diff)
  target_positions_min = np.append(target_positions, target_diff, axis=1)
  # print("List of Target diff: ", target_positions_min)
  columnIndex = 4
  target_positions_min = target_positions_min[target_positions_min[:, columnIndex-1].argsort()]
  print("Target Position ordered: \n", target_positions_min)
  print("\n")


  # Drive Robot Arm
  station_config = station_config = [[68, 89, 179, 93, 0, 110],
                  [68, 85, 150, 93, 0, 110],
                  [68, 80, 140, 93, 0, 110]]
  home_config = [90, 110, 110, 90, 90, 20]
  current_config = home_config

  for i, target in zip(range(0, size[0]),target_positions_min[:, :-1]):
    print("Robot Heading towards target at: ", target)
    print("\n")
    target_config = IK.doIK(target)
    dr.drive2Position(target_config, current_config, i)
    current_config = station_config[i]
  dr.returnHome(station_config[i])


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
