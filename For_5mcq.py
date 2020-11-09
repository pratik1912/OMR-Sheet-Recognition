# for output you have to write in CLI.... python filename.py --image foldername_of_images\image_name

from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,help="path to the input image")
args = vars(ap.parse_args())

ANSWER_KEY = {0: 2, 1: 2, 2: 1, 3: 1, 4: 3, 5: 1, 6: 0, 7: 1, 8: 2, 9: 1}

image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)

cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
docCnt = None


if len(cnts) > 0:
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            docCnt = approx
            break

crop = four_point_transform(image, docCnt.reshape(4, 2))
paper = four_point_transform(image, docCnt.reshape(4, 2))
warped = four_point_transform(gray, docCnt.reshape(4, 2))

thresh = cv2.threshold(warped, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
questionCnts = []

for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)
    if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
        questionCnts.append(c)


questionCnts = contours.sort_contours(questionCnts,method="top-to-bottom")[0]
correct = 0

for (q, i) in enumerate(np.arange(0, len(questionCnts), 4)):
    cnts = contours.sort_contours(questionCnts[i:i + 4])[0]
    bubbled = None


    for (j, c) in enumerate(cnts):
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
        total = cv2.countNonZero(mask)

        if bubbled is None or total > bubbled[0]:
            bubbled = (total, j)

    color = (0, 0, 255)
    k = ANSWER_KEY[q]


    if k == bubbled[1]:
        color = (0, 255, 0)
        correct += 1

    paper1 = cv2.drawContours(paper, [cnts[k]], -1, color, 3)
    
score = correct
print("[INFO] score: {:.2f}/5".format(score))
cv2.putText(paper, "{:.2f}/5".format(score), (30, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
cv2.imshow("Original-1", image)
cv2.imshow("edged-2",edged)
cv2.imshow("crop-3",crop)
cv2.imshow("Grayscale-4",warped)
cv2.imshow("thresh-5",thresh)
cv2.imshow("Exam", paper1)
cv2.waitKey(0)