import cv2
import numpy as np
import tkinter as tk

frame = cv2.imread('frame.png')
frame_height, frame_width, _ = frame.shape

max_f = 100

master = tk.Tk()


def callback(val):
    f_x = entry_f_x.get()
    c_x = entry_c_x.get()
    # f_y = entry_f_y.get()
    c_y = entry_c_y.get()
    k_1 = entry_k_1.get()
    k_2 = entry_k_2.get()
    p_1 = entry_p_1.get()
    p_2 = entry_p_2.get()

    camera_matrix = np.array([
        [f_x, 0.0, c_x],
        [0.0, f_x, c_y],
        [0.0, 0.0, 1.0]
    ])
    dist_coeffs = np.array(
        [k_1, k_2, p_1, p_2]
    )

    dim = (frame_width, frame_height)
    new_cam, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, dim, 1, dim)
    mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, new_cam, dim, cv2.CV_32FC1)
    t_frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    cv2.imshow('Undistorted', t_frame)
    return True


tk.Label(master, text='f_x').grid(row=0, column=0)
tk.Label(master, text='c_x').grid(row=0, column=2)
tk.Label(master, text='f_y').grid(row=1, column=0)
tk.Label(master, text='c_y').grid(row=1, column=2)
tk.Label(master, text='k_1').grid(row=2, column=0)
tk.Label(master, text='k_2').grid(row=2, column=2)
tk.Label(master, text='p_1').grid(row=3, column=0)
tk.Label(master, text='p_2').grid(row=3, column=2)
entry_f_x = tk.Scale(master, from_=0, to=max_f, orient=tk.HORIZONTAL, command=callback)
entry_c_x = tk.Scale(master, from_=0, to=frame_width, orient=tk.HORIZONTAL, command=callback)
# entry_f_y = tk.Scale(master, from_=0, to=max_f)
entry_c_y = tk.Scale(master, from_=0, to=frame_height, orient=tk.HORIZONTAL, command=callback)
entry_k_1 = tk.Scale(master, from_=-0.001, to=0.0005, orient=tk.HORIZONTAL, resolution=0.000001, command=callback)
entry_k_2 = tk.Scale(master, from_=-0.000003, to=0.000005, orient=tk.HORIZONTAL, resolution=0.0000001, command=callback)
entry_p_1 = tk.Scale(master, from_=-0.1, to=0.1, orient=tk.HORIZONTAL, resolution=0.001, command=callback)
entry_p_2 = tk.Scale(master, from_=-0.1, to=0.1, orient=tk.HORIZONTAL, resolution=0.001, command=callback)

entry_f_x.grid(row=0, column=1)
entry_c_x.grid(row=0, column=3)
# entry_f_y.grid(row=1, column=1)
entry_c_y.grid(row=1, column=3)
entry_k_1.grid(row=2, column=1)
entry_k_2.grid(row=2, column=3)
entry_p_1.grid(row=3, column=1)
entry_p_2.grid(row=3, column=3)

entry_c_x.set(frame_width / 2)
entry_c_y.set(frame_height / 2)
entry_f_x.set(max_f / 2)

master.mainloop()
