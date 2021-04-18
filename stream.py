import cv2
import numpy as np
import pafy

url = "https://youtu.be/1EiC9bvVGnk"
vid = pafy.new(url)
play = vid.getbest()

window_name = 'Stream'

src_pts = np.array([[209, 282], [209, 330], [484, 337], [493, 296]])
dst_pts = np.array([[209, 296], [209, 353], [493, 353], [493, 296]])
homography, mask = cv2.findHomography(src_pts, dst_pts)
print(homography)

cap = cv2.VideoCapture(play.url)
while True:
    ret, frame = cap.read()
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    cv2.imshow(window_name, frame)
    transformed = cv2.warpPerspective(frame, homography, (1600, 1600))
    cv2.imshow('trans', transformed)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
