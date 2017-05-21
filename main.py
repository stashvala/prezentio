import cv2
import time
import collections
import pyautogui as pag

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

    face_queue = collections.deque(maxlen=10)

    while True:
        return_value, image = camera.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

                avgfacex /= len(face_queue)
                avgfacey /= len(face_queue)
                avgfacew /= len(face_queue)
                avgfaceh /= len(face_queue)

                if detected == 0:
                    if avgy < avgfacey:
                        detected = 1
                        print("r")
                    else:
                        detected = 2
                        print("l")

            else:
                history.append([x, y])

        face = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x2, y2, w2, h2) in face:
            cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)
            face_queue.append([x2, y2, w2, h2])

        cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("End")
