import numpy as np
import cv2
import utils
import math

def dist(p,q):

    diff1 = (p[0]-q[0]) * (p[0]-q[0])
    diff2 = (p[1]-q[1]) * (p[1]-q[1])
    diff = math.sqrt(diff1+diff2)
    return diff

def arrangeCorners(Corners):
    pts = Corners
    rect = np.zeros((4, 2), dtype="float32")
    # the top-left point has the smallest sum whereas the
    # bottom-right has the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # compute the difference between the points -- the top-right
    # will have the minumum difference and the bottom-left will
    # have the maximum difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # print(rect)
    return rect

def warpPerspective(img, pnts, size):
    width, height = size

    NewPnts = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    pnts = utils.arrangeCorners(pnts)

    matrix = cv2.getPerspectiveTransform(pnts, NewPnts)
    WarpedImage = cv2.warpPerspective(img, matrix, (width, height))
    return WarpedImage

def getContours(img, imgContour):
    contours,heirarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area>100000 and area < 200000:
            peri = cv2.arcLength(cnt,True)
            print (area,peri)
            cv2.drawContours(imgContour,cnt,-1,(255,0,255),2)
            approx = cv2.approxPolyDP(cnt,0.1*peri,True)
            print(len(approx))
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
                        # String containing the co-ordinates.
                        string = str(x) + " " + str(y)
                        # if (i == 0):
                        #     # text on topmost co-ordinate.
                        #     cv2.putText(imgContour, "Arrow tip", (x, y),
                        #                 font, 0.5, (0, 255, 0), 1)
                        # else:
                        # text on remaining co-ordinates.
                        cv2.putText(imgContour, string, (x, y),
                                    cv2.FONT_ITALIC , 0.5, (0, 255, 0), 1)
                    i = i + 1
                print(Corners)
                cv2.putText(imgContour,objType,(x+(w//2)-35,y+(h//2)+5),cv2.FONT_ITALIC,0.4,(0,0,0),1)
                return Corners

def correctOrientation(img, pnts):
    corrImg = img
    w, h = img.shape[1], img.shape[0]
    diff = [0,0,0,0]


    diff[0] = dist(pnts[0], [0, 0])
    diff[1] = dist(pnts[1], [w, 0])
    diff[2] = dist(pnts[2], [w, h])
    diff[3] = dist(pnts[3], [0, h])

    min = np.argmin(diff)
    if min == 0:
        corrImg = cv2.rotate(img, cv2.ROTATE_180)
        print("rotated 180")
    elif min == 1:
        corrImg = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        print("rotated 90 clock")
    elif min == 3:
        corrImg = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        print("rotated 90 counterclock")
    else: print("no rotation")
    return corrImg

# To transform coordinates from frame of image to frame of robot, pntS should be in metres
def getTransformImg2Rbt(pntS):
    R = [0, 6.5/100 ,2/100]
    pntR = pntS
    pntR[0] = pntS[0] -25/200
    pntR[1] = 25/100+ R[1] - pntS[1]
    pntR[2] = R[2]
    return pntR

def stackImages(imgArray,scale,lables=[]):
    sizeW= imgArray[0][0].shape[1]
    sizeH = imgArray[0][0].shape[0]
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (sizeW, sizeH), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    return ver