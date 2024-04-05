import cv2
cap = cv2.VideoCapture(1)
cap.set(3, 1920)
cap.set(4, 1060)

ret, image = cap.read()
print(ret)
cv2.imwrite('test.png', image)
