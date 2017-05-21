import cv2
import time

if __name__ == '__main__':
    print("Start")

    hand_cascade = cv2.CascadeClassifier('hand.xml')
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    camera = cv2.VideoCapture(0)

    time_thresh = 1
    hist_thresh = 10

    start = 0
    history = []

    while True:
        return_value, image = camera.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        hands = hand_cascade.detectMultiScale(gray, 1.3, 5)
        face = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(hands) == 0:
            start = 0
            history = []

        for (x, y, w, h) in hands:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            #print("before if = ", start)
            if start == 0:
                start = time.time()
                #print("start = ", start)

            print((time.time() - start))
            if (time.time() - start) > time_thresh and len(history) > hist_thresh:
                avgx = 0
                avgy = 0
                for i in history:
                    avgx += i[0]
                    avgy += i[1]
                avgx /= len(history)
                avgy /= len(history)
                stddevx = 0
                stddevy = 0
                for i in history:
                    stddevx += (avgx - i[0]) ^ 2
                    stddevy += (avgy - i[1]) ^ 2
                if stddevx < 2 and stddevy < 2:
                    print("Success")
                    history = 0
                    start = 0

            else:
                history.append([x, y])

                # for (x2, y2, w2, h2) in face:
                # cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)

        cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("End")
