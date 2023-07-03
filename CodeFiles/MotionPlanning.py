import cv2
import numpy as np
from CodeFiles import DriveRobot as dr, IK, PlatformDetection as pd
import TrackObjects as gt

z_offset = 0.13
# pivot_position = [0, 0.10, 0.02 + 0.3 + 0.05]
pivot_position = [0, 0.4, 0.02 + 0.3 + 0.05]
pivot_orientation = [0.1, 0.5, -0.1]
station_position = np.array([0.06,  0.15,  0.02+ z_offset ])
station_position1 = np.array([0.06,  0.150,  0.02+ z_offset +0.05])
station_position2 = np.array([0.08,  0.150,  0.02+ z_offset +0.10])

# station_config = [[68, 89, 160, 93, 0, 110],
#                   [68, 85, 140, 93, 0, 110],
#                   [68, 80, 130, 93, 0, 110]]

home_config = [90, 110, 80, 90, 90, 40]

# For static Image
img = cv2.imread("../Resources/PlatformImg16.jpg")
gt.detectAndTrack(img)


# # For Video Streaming
# url = "http://192.168.29.59:8080/video"
# vid = cv2.VideoCapture(url)
# while(True):
#     camera, img = vid.read()
#     if img is not None:
#         print("Detecting...")
#         if gt.detectAndTrack(img) == -1:
#           continue
#         else:break
#     else: break
#     q = cv2.waitKey(1)
#     if q == ord("q"):
#         break


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

  # Adding off set in z direction to compensate for end-effector
  target_positions_min[:,2] = z_offset
  station_positions = [station_position, station_position1, station_position2]

  # Drive Robot Arm
  current_config = home_config
  pivot_config= IK.doIK(pivot_position,pivot_orientation)
  pivot_config = dr.getTargetConfig(pivot_config)



  for i, target in zip(range(0, size[0]),target_positions_min[:, :-1]):
    print("Robot Heading towards target at: ", target)
    print("\n")
    target_config = IK.doIK(target)
    target_config = dr.getTargetConfig(target_config)

    print("Station Position:", i)
    station_config = IK.doIK(station_positions[i])
    station_config = dr.getTargetConfig(station_config)

    dr.drive2Position(target_config, current_config, station_config, pivot_config)

    current_config = pivot_config
  dr.returnHome(pivot_config)


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
