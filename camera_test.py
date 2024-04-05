import cv2
cap = cv2.VideoCapture(1)
ret, image = cap.read()
print(ret)
cv2.imwrite('test.png', image)
