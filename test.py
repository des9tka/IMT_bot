import cv2

cap = cv2.VideoCapture(0)

cap.set(3, 1000)
cap.set(4, 700)

while True:
    success, img = cap.read()
    cv2.imshow('Result', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
