import cv2
import numpy as np
import pafy

from undistort import undistort_img
from util import read_config_entry, write_config_entry

CAM_NAME = 'pizzeria'

cam_config = read_config_entry(CAM_NAME)

url = cam_config['url']
vid = pafy.new(url)
play = vid.getbest()

stream_window_name = 'Stream'
reference_window_name = 'Reference'

clicked_pts_stream = []
clicked_pts_reference = []


def add_coords(a, b):
    x1, y1 = a
    x2, y2 = b
    return x1 + x2, y1 + y2


def on_click_ref(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_pts_reference.append((x, y))


def on_click_stream(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_pts_stream.append((x, y))


def draw_points(input_frame, pts):
    output_frame = input_frame
    clr = (0, 255, 0)
    for index, pt in enumerate(pts):
        cv2.drawMarker(output_frame, pt, clr, markerType=cv2.MARKER_TILTED_CROSS, markerSize=15, thickness=3)
        cv2.putText(output_frame, str(index), add_coords(pt, (8, -12)), cv2.FONT_HERSHEY_DUPLEX, 1, clr, 1,
                    cv2.LINE_AA)
    return output_frame


cv2.namedWindow(stream_window_name, cv2.WINDOW_NORMAL)
cv2.namedWindow(reference_window_name, cv2.WINDOW_NORMAL)
cv2.setMouseCallback(stream_window_name, on_click_stream)
cv2.setMouseCallback(reference_window_name, on_click_ref)

# open reference image
aerial_image = cv2.imread('aerial.png')
target_width = 1280
scale = 1280 / aerial_image.shape[1]
scaled_shape = (int(aerial_image.shape[1] * scale),
                int(aerial_image.shape[0] * scale))
print(scaled_shape)
aerial_image = cv2.resize(aerial_image, scaled_shape)

cap = cv2.VideoCapture(play.url)

homography = np.array(cam_config['transform']) if cam_config['transform'] else None
while True:
    ret, frame = cap.read()

    if corrections := cam_config['correction']:
        camera_matrix = np.array(corrections['camMatrix'])
        distortion_coeffs = np.array(corrections['distCoeffs'])
        frame = undistort_img(camera_matrix, distortion_coeffs, frame)

    cv2.resizeWindow(stream_window_name, 1280, 720)
    cv2.imshow(stream_window_name, draw_points(frame, clicked_pts_stream))

    cv2.imshow(reference_window_name, draw_points(aerial_image, clicked_pts_reference))

    # recompute homography
    pts_len = min(len(clicked_pts_reference), len(clicked_pts_stream))
    if pts_len >= 4:
        src_pts = np.array(clicked_pts_stream[:pts_len])
        dst_pts = np.array(clicked_pts_reference[:pts_len])
        homography, mask = cv2.findHomography(src_pts, dst_pts)
    if homography is not None:
        transformed = cv2.warpPerspective(frame, homography, scaled_shape)
        transformed = cv2.addWeighted(transformed, 0.5, aerial_image, 0.5, 0.0)
        cv2.imshow('trans', transformed)

    key_val = cv2.waitKey(20)
    if key_val & 0xFF == ord('r'):
        clicked_pts_stream.clear()
        clicked_pts_reference.clear()
    elif key_val & 0xFF == ord('q'):
        break

if homography is not None:
    write_config_entry(CAM_NAME, transform=homography.tolist())

cap.release()
cv2.destroyAllWindows()
