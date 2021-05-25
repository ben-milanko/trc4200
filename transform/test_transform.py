import cv2
import numpy as np
import pafy

from undistort import undistort_img
from util import read_config_entry

CAM_NAME = 'pizzeria'

cam_config = read_config_entry(CAM_NAME)

url = cam_config['url']
vid = pafy.new(url)
play = vid.getbest()

stream_window_name = 'Stream'
reference_window_name = 'Reference'

clicked_pts_stream = []
clicked_pts_reference = []

homography = np.array(cam_config['transform'])


def add_coords(a, b):
    x1, y1 = a
    x2, y2 = b
    return x1 + x2, y1 + y2


def on_click_stream(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pts = np.array([(x, y), (1851, 425.5), (1645, 565), (1630.5, 466), (683, 491)], dtype="float32")
        pts = np.array([pts])
        t = cv2.perspectiveTransform(pts, homography)[0]
        print(pts, '\n', t)


cv2.namedWindow(stream_window_name, cv2.WINDOW_NORMAL)
cv2.setMouseCallback(stream_window_name, on_click_stream)

# open reference image
aerial_image = cv2.imread('aerial.png')
target_width = 1280
scale = 1280 / aerial_image.shape[1]
scaled_shape = (int(aerial_image.shape[1] * scale),
                int(aerial_image.shape[0] * scale))
print(scaled_shape)
aerial_image = cv2.resize(aerial_image, scaled_shape)

cap = cv2.VideoCapture(play.url)
while True:
    ret, frame = cap.read()

    if corrections := cam_config['correction']:
        camera_matrix = np.array(corrections['camMatrix'])
        distortion_coeffs = np.array(corrections['distCoeffs'])
        frame = undistort_img(camera_matrix, distortion_coeffs, frame)

    cv2.resizeWindow(stream_window_name, 1280, 720)
    cv2.imshow(stream_window_name, frame)

    transformed = cv2.warpPerspective(frame, homography, scaled_shape)
    transformed = cv2.addWeighted(transformed, 0.5, aerial_image, 0.5, 0.0)
    cv2.imshow('trans', transformed)

    key_val = cv2.waitKey(20)
    if key_val & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
