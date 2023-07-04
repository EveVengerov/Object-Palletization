import cv2
import numpy as np
import utils

# Input: canny image, copy of the original image, area over which the rectangle should lie; output: Coordinates of the corner of the distorted rectangle
def getRectangle(img, imgContour, rangeArea):
    contours,heirarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area<rangeArea[0] and area>rangeArea[1]:
            peri = cv2.arcLength(cnt,True)
            # print (area,peri)
            cv2.drawContours(imgContour,cnt,-1,(255,0,255),2)
            approx = cv2.approxPolyDP(cnt,0.1*peri,True)
            # print(len(approx))
            objcor = len(approx)
            x,y,w,h = cv2.boundingRect(approx)
            # cv2.rectangle(imgContour,(x,y),(x+w,y+h),(0,255,255),2)
            if objcor == 4:
                objType = "Rectangle"
                # print("Area of Rectangle is : %s" % area)

                n = approx.ravel() # Finding coordinates of the corners
                i = 0

                Corners = np.float32([[0,0],[0,0],[0,0],[0,0]])
                for j in n:
                    if (i % 2 == 0):
                        x = n[i]
                        y = n[i + 1]
                        Corners[int(i/2)] = x,y

                        cv2.circle(imgContour, (x,y), 5, (255,0, 0), cv2.FILLED)
                        # String containing the co-ordinates.
                        # string = str(x) + " " + str(y)
                        # if (i == 0):
                        #     # text on topmost co-ordinate.
                        #     cv2.putText(imgContour, "Arrow tip", (x, y),
                        #                 font, 0.5, (0, 255, 0), 1)
                        # else:
                        # text on remaining co-ordinates.
                        # cv2.putText(imgContour, string, (x, y),
                        #             font, 0.5, (0, 255, 0), 1)
                    i = i + 1
                # print(Corners)
                # cv2.putText(imgContour,objType,(x+(w//2)-35,y+(h//2)+5),cv2.FONT_ITALIC,0.4,(0,0,0),1)
                return Corners
            else: return None

def platform(img, showImage =False):
    kernel = np.ones((5,5),np.uint8 )
    font = cv2.FONT_HERSHEY_COMPLEX

    # img = cv2.imread("Resources/PlatformImg12.jpg")
    img = cv2.resize(img, (640, 480))
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5), 2)
    # ret, thresh = cv2.threshold(imgBlur, 120, 255, 0)
    # thresh = cv2.bitwise_not(thresh)
    imgCanny = cv2.Canny(imgBlur,100,100)
    imgDilation = cv2.dilate(imgCanny, kernel, iterations = 1)
    imgCanny= cv2.erode(imgDilation, kernel, iterations=1)

    # For showing Contour over the image
    imgContour = img.copy()
    cv2.imshow("Image contours", imgCanny)
    cv2.waitKey(0)
    WarpPnts = getRectangle(imgCanny, imgContour, [200000, 100000])
    # print(type(WarpPnts))
    #  To check if WarpPnts fetched is a list type or not , if bool is returned, no points are detected
    if isinstance(WarpPnts, np.ndarray ):
        print("Platform Detected")
    else:
        print("Platform not Detected")
        return -1

    # Crop and resize the platform to a 500x500 pixels square image
    CropSize = [500,500]
    croppedImage = utils.warpPerspective(img, WarpPnts, CropSize)
    croppedImageContour = croppedImage.copy()
    croppedImageCanny = utils.warpPerspective(imgCanny, WarpPnts, CropSize)


    # get coordinates of points
    Ppnts = getRectangle(croppedImageCanny, croppedImageContour, [50000,10000])
    if not isinstance(Ppnts, bool):
        print("Placement Station Detected")
    else:
        print("Placement Station not Detected")
        return -1

    print("Correcting Orientation... ")
    croppedImage = utils.correctOrientation(croppedImage, Ppnts)
    # croppedImageCanny = utils.correctOrientation(croppedImageCanny, Ppnts)
    # croppedImageContour = utils.correctOrientation(croppedImageContour, Ppnts)
    print("Corrected ")

    # Estimating meter to pixel ratio
    sumP = utils.dist(Ppnts[0], Ppnts[1]) + utils.dist(Ppnts[1], Ppnts[2]) + utils.dist(Ppnts[2], Ppnts[3]) + utils.dist(Ppnts[3], Ppnts[0])
    avgP = sumP/4

    Scale = 0.09/avgP #in m/pixel

    if showImage == True :
        # Show all images
        stackImage = utils.stackImages([[img, imgBlur],[imgCanny, imgContour]],0.7)
        cv2.imshow("Image Proccessing", stackImage)
        cv2.waitKey(0)
    return [croppedImage, Scale]

def detectCurves(img):
    # Convert it to grayscale

    inputImageGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Line Detection

    imgCanny = cv2.Canny(inputImageGray, 100, 200, apertureSize=3)
    imgCannyBGR = cv2.cvtColor(imgCanny, cv2.COLOR_GRAY2BGR)
    minLineLength = 100
    maxLineGap = 5

    lines = cv2.HoughLinesP(imgCanny, 1, np.pi / 180, 90, minLineLength, maxLineGap)

    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            cv2.line(imgCannyBGR, (x1, y1), (x2, y2), (0, 128, 0), 10)

    cv2.putText(imgCannyBGR, "Tracks Detected", (500, 250),0, 1, 255)

    # Show result

    imgCannyBGR = cv2.resize(imgCannyBGR, (800, 480))
    cv2.imshow("Trolley_Problem_Result",  imgCannyBGR)
    cv2.waitKey(0)


if __name__ == '__main__':
    img = cv2.imread("../Resources/PlatformImg18.jpg")
    # if platform(img) != -1:
    #         croppedImage, scale = platform(img)
    #         cv2.imshow("Processed Image", croppedImage)
    #         cv2.waitKey(0)
    img = detectCurves(img)


# # For Video Streaming
# url = "http://192.168.137.18:8080/video"
# cap = cv2.VideoCapture(url)
# while(True):
#     camera, img = cap.read()
#     if img is not None:
#         img = cv2.resize(img, (640, 480))
#         imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#         imgBlur = cv2.GaussianBlur(imgGray,(5,5), 2)
#         imgCanny = cv2.Canny(imgBlur,100,100)
#
#
#         imgContour = img.copy()
#
#         print("Detecting...")
#         getContours(imgCanny)
#
#         cv2.imshow("Shapes",imgContour)
#         cv2.imshow("Canny",imgCanny)
#
#     q = cv2.waitKey(1)
#     if q == ord("q"):
#         break
# cv2.destroyAllWindows()

