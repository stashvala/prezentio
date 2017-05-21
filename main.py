import cv2
import time
import collections
import pyautogui as pag
import numpy as np

def get_holes(image, thresh):
    gray = image

    im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]
    im_bw_inv = cv2.bitwise_not(im_bw)

    contour = cv2.findContours(im_bw_inv, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contour = contour[0]

    nt = cv2.bitwise_not(im_bw)
    im_bw_inv = cv2.bitwise_or(im_bw_inv, nt)
    return im_bw_inv


def remove_background(image, thresh, scale_factor=.25, kernel_range=range(1, 15), border=None):
    border = border or kernel_range[-1]

    holes = get_holes(image, thresh)
    small = cv2.resize(holes, None, fx=scale_factor, fy=scale_factor)
    bordered = cv2.copyMakeBorder(small, border, border, border, border, cv2.BORDER_CONSTANT)

    for i in kernel_range:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*i+1, 2*i+1))
        bordered = cv2.morphologyEx(bordered, cv2.MORPH_CLOSE, kernel)

    unbordered = bordered[border: -border, border: -border]
    mask = cv2.resize(unbordered, (image.shape[1], image.shape[0]))
    fg = cv2.bitwise_and(image, image, mask=mask)
    return fg

def edgedetect (channel):
    sobelX = cv2.Sobel(channel, cv2.CV_16S, 1, 0)
    sobelY = cv2.Sobel(channel, cv2.CV_16S, 0, 1)
    sobel = np.hypot(sobelX, sobelY)

    sobel[sobel > 255] = 255; # Some values seem to go above 255. However RGB channels has to be within 0-255

if __name__ == '__main__':
    print("Start")

    hand_cascade = cv2.CascadeClassifier('hand.xml')
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    camera = cv2.VideoCapture(0)

    time_thresh = 1
    hist_thresh = 8

    start = 0
    history = []
    detected = 0

    # Constants for finding range of skin color in YCrCb
    min_YCrCb = np.array([0, 133, 77], np.uint8)
    max_YCrCb = np.array([255, 173, 127], np.uint8)

    face_queue = collections.deque(maxlen=10)
    while True:
        return_value, image = camera.read()
        imgraw = image
        image = cv2.GaussianBlur(image, (7, 7), 1.5, 1.5)
        gray_face = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        imageYCrCb = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)

        # Find region with skin tone in YCrCb image
        skinRegion = cv2.inRange(imageYCrCb, min_YCrCb, max_YCrCb)

        image = cv2.bitwise_and(image, image, mask=skinRegion)
        image[skinRegion == 0] = [255, 255, 255]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #gray = remove_background(gray, 230)

        hands = hand_cascade.detectMultiScale(gray, 1.3, 5)

        if len(hands) == 0:
            if detected == 1:
                print("right")
                pag.press('right')
            elif detected == 2:
                print("left")
                pag.press('left')

            detected = 0
            start = 0
            history = []

        for (x, y, w, h) in hands:
            if detected == 0:
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            else:
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

            if start == 0:
                start = time.time()

            if (time.time() - start) > time_thresh and len(history) > hist_thresh:
                avgx = 0
                avgy = 0
                for i in history:
                    avgx += i[0]
                    avgy += i[1]
                avgx /= len(history)
                avgy /= len(history)

                avgfacex = 0
                avgfacey = 0
                avgfacew = 0
                avgfaceh = 0
                for i in face_queue:
                    avgfacex += i[0]
                    avgfacey += i[1]
                    avgfacew += i[2]
                    avgfaceh += i[3]


                if detected == 0:
                    if avgy < avgfacey:
                        detected = 1
                        print("r")
                    else:
                        detected = 2
                        print("l")

            else:
                history.append([x, y])

        face = face_cascade.detectMultiScale(gray_face, 1.3, 5)
        for (x2, y2, w2, h2) in face:
            cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)
            face_queue.append([x2, y2, w2, h2])

        cv2.imshow('image', image)
        cv2.imshow('imgraw', imgraw)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("End")
