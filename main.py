import cv2
import cvzone
import numpy as np
import pickle
import os

# Параметры парковочных мест
width, height = 96, 221

# Список позиций парковочных мест
posList = []

# Путь к видеофайлу
video_path = 'C:/Users/Ivanov-AS/Downloads/carParkVideo.mp4'

# Путь к файлу с сохраненными позициями
positions_file = 'parking_positions.pkl'

# Загрузка позиций из файла
if os.path.exists(positions_file):
    with open(positions_file, 'rb') as f:
        posList = pickle.load(f)

# Инициализация видеокаптуры
cap = cv2.VideoCapture(video_path)

def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
        save_positions()
    if events == cv2.EVENT_RBUTTONDOWN:
        for pos in posList:
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.remove(pos)
                save_positions()
                break

def save_positions():
    with open(positions_file, 'wb') as f:
        pickle.dump(posList, f)

def checkParkingSpace(imgPro, img, pos):
    x, y = pos
    imgCrop = imgPro[y:y+height, x:x+width]
    count = cv2.countNonZero(imgCrop)
    cvzone.putTextRect(img, str(count), (x, y+height-10), scale=1, thickness=1, offset=0)
    return count

def display_stats(img):
    free_spaces = 0
    total_spaces = len(posList)
    for pos in posList:
        count = checkParkingSpace(imgDilate, img, pos)
        if count < 2000:
            free_spaces += 1
    cvzone.putTextRect(img, f"Free: {free_spaces}/{total_spaces}", (10, 20), scale=1, thickness=1, offset=0)

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 1)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    for pos in posList:
        count = checkParkingSpace(imgDilate, img, pos)
        if count < 2000:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, 2)

    display_stats(img)

    cv2.imshow('Image', img)
    cv2.setMouseCallback('Image', mouseClick)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
