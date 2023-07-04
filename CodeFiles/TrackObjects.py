import cv2
import numpy as np
from CodeFiles import PlatformDetection as Pd, utils


# Function to identify colored cubes on the platform
def getContour(img, imgContour, rangeArea=[50000,1000]):
    contours,heirarchy = cv2.findContours(img,cv2. RETR_LIST,cv2.CHAIN_APPROX_NONE)
    C = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)


        if area<rangeArea[0] and area>rangeArea[1]:
            peri = cv2.arcLength(cnt,True)

            # Draw contours
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 2)

            # Find Centroid
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                cx, cy = 0, 0
            C.append([cx,cy])


            cv2.circle(imgContour, (cx, cy), 7, (255, 255, 0), -1)
            string = str(cx) + " " + str(cy)
            cv2.putText(imgContour,  string, (cx, cy-10), 2, 0.5, (0, 255, 0), 1)


            approx = cv2.approxPolyDP(cnt,0.07*peri,True)
    # print(C[1])
    return C

def detectCubes(img, Scale, showImage=False):
    img = cv2.resize(img, (640, 480))
    img = cv2.GaussianBlur(img, (5, 5), 2)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # img = Pd.croppedImage

    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h_min = 0
    s_min = 108
    v_min = 24

    h_max = 180
    s_max = 255
    v_max = 255

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)

    result = cv2.bitwise_and(img, img, mask=mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    imgContours = img.copy()

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    resultGray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # For erd and pink detection
    # ret, thresh = cv2.threshold(resultGray, 100, 255, 0)
    # ret,thresh = cv2.threshold(resultGray, 145,255,0) #For only pink detection

    C = getContour(mask, imgContours)
    if not isinstance(C, bool):
        print("Objects Not Detected")
    else :
        print("Object Detected")
        return -1
    i = 0
    TargetPosition = []
    for c in C:
        cinm = np.float32([0, 0, 0])
        cinm[0] = c[0] * Scale
        cinm[1] = c[1] * Scale
        cinm[2] = 0

        cinm = utils.getTransformImg2Rbt(cinm)
        TargetPosition.append(cinm)
        print("Target coordinates [{}] in cms/100 {} ".format(i, cinm) % cinm)
        i = i+1



    if showImage == True :
        # Show Processed Image
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        stackImage = utils.stackImages([[img, mask, imgContours]],0.7)
        cv2.imshow('Stacked Images', stackImage)
        cv2.waitKey(0)

    return TargetPosition

def detectAndTrack(img, showImage = True):
    croppedImageScale = Pd.platform(img, showImage)
    if croppedImageScale != -1:
        croppedImage, Scale = croppedImageScale[0], croppedImageScale[1]
        TargetPositions = detectCubes(croppedImage, Scale, showImage)
        if TargetPositions != -1:
            return TargetPositions
        else: print("Make sure the objects are clearly visible to the camera")
    else:
        print("Make sure the platform is clearly visible to the camera")
        return -1


if __name__ == '__main__':
    img = cv2.imread("../Resources/PlatformImg8.jpg")
    detectAndTrack(img)

    # # For Video Streaming
    # url = "http://192.168.29.60:8080/video"
    # vid = cv2.VideoCapture(url)
    # while(True):
    #     camera, img = vid.read()
    #     if img is not None:
    #         print("Detecting...")
    #         if detectAndTrack(img) == -1:
    #           continue
    #         else:break
    #     else: break
    #     q = cv2.waitKey(1)
    #     if q == ord("q"):
    #         break
