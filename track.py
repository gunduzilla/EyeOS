#TODO: Make a method that auto-calibrates for eye detection by looping through possible thresholds until one is found in which the eyes are highlighted

import cv2
import numpy as np


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
detector_params = cv2.SimpleBlobDetector_Params()
detector_params.filterByArea = True
detector_params.maxArea = 1500
detector = cv2.SimpleBlobDetector_create(detector_params)


def detect_faces(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = cascade.detectMultiScale(gray_frame, 1.3, 5)
    if len(coords) > 1:
        biggest = (0, 0, 0, 0)
        for i in coords:
            if i[3] > biggest[3]:
                biggest = i
        biggest = np.array([i], np.int32)
    elif len(coords) == 1:
        biggest = coords
    else:
        return None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
    return {"frame": frame, "biggest": biggest[0]}


def detect_eyes(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes = cascade.detectMultiScale(gray_frame, 1.3, 5)
    width = np.size(img, 1)
    height = np.size(img, 0)
    left_eye = None
    right_eye = None
    for (x, y, w, h) in eyes:
        if y > height / 2:
            pass
        eyecenter = x + w / 2
        if eyecenter < width * 0.5:
            left_eye = img[y:y + h, x:x + w]
        else:
            right_eye = img[y:y + h, x:x + w]
    return left_eye, right_eye


def cut_eyebrows(img):
    height, width = img.shape[:2]
    eyebrow_h = int(height / 4)
    img = img[eyebrow_h:height, 0:width]

    return img


def blob_process(img, threshold, detector):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    img = cv2.erode(img, None, iterations=2)
    img = cv2.dilate(img, None, iterations=4)
    img = cv2.medianBlur(img, 5)
    keypoints = detector.detect(img)
    return keypoints


def bruh(x):
    pass

eyeX = 0
eyeY = 0
thresholdCalibrated = False
threshold = 0

def loop():
    global eyeX, eyeY, threshold, thresholdCalibrated
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Frame')
    while True:
        _, frame = cap.read()
        faces = detect_faces(frame, face_cascade)
        if faces is not None:
            face_frame = faces['frame']
            biggest = faces['biggest']
            
            centerX = biggest[0] + biggest[2] // 2
            centerY = biggest[1] + biggest[3] // 2
            
            cv2.rectangle(frame, (centerX - 1, centerY - 1), (centerX + 1, centerY + 1), 0.5)
            eyes = detect_eyes(face_frame, eye_cascade)
            for eye in eyes:
                if eye is not None:
                    eye = cut_eyebrows(eye)
                    keypoints = blob_process(eye, threshold, detector)
                    pts = [i.pt for i in keypoints]
                    if len(pts) > 0:
                        thresholdCalibrated = True
                        sumX = sumY = 0
                        for point in pts:
                            sumX += point[0]
                            sumY += point[1]
                        meanX = sumX / len(pts)
                        meanY = sumY / len(pts)
                        eyeX, eyeY = meanX - centerX, meanY - centerY
                    else:
                        if not thresholdCalibrated:
                            print("Trying threshold", threshold)
                            threshold += 5
                    
                    cv2.drawKeypoints(eye, keypoints, eye, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

