import cv2
import numpy as np
import tkinter as tk


def undistort_img(camera_matrix, dist_coeffs, input_img):
    h, w, _ = input_img.shape
    dim = (w, h)
    new_cam, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, dim, 0.15, dim)
    map_x, map_y = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, new_cam, dim, cv2.CV_32FC1)
    return cv2.remap(input_img, map_x, map_y, cv2.INTER_LINEAR)


def callback(val):
    f_x = entry_f_x.get()
    c_x = entry_c_x.get()
    # f_y = entry_f_y.get()
    c_y = entry_c_y.get()
    k_1 = entry_k_1.get()
    k_2 = entry_k_2.get()
    p_1 = entry_p_1.get()
    p_2 = entry_p_2.get()

    f_y = img_height / img_width * f_x

    camera_matrix = np.array([
        [f_x, 0.0, c_x],
        [0.0, f_y, c_y],
        [0.0, 0.0, 1.0]
    ])
    dist_coeffs = np.array(
        [k_1, k_2, p_1, p_2]
    )
    print(camera_matrix, dist_coeffs)

    t_frame = undistort_img(camera_matrix, dist_coeffs, img)
    cv2.imshow('Undistorted', t_frame)
    return True


if __name__ == '__main__':
    img = cv2.imread('frame.png')
    img_height, img_width, _ = img.shape

    max_f = 200

    master = tk.Tk()
    master.geometry('600x180')
    master.title("Distortion Parameters")
    tk.Grid.rowconfigure(master, 0, weight=1)
    tk.Grid.columnconfigure(master, 0, weight=1)

    frame = tk.Frame(master)
    frame.grid(row=0, column=0, sticky=tk.NSEW)

    tk.Label(frame, text='f_x').grid(row=0, column=0)
    tk.Label(frame, text='c_x').grid(row=0, column=2)
    tk.Label(frame, text='f_y').grid(row=1, column=0)
    tk.Label(frame, text='c_y').grid(row=1, column=2)
    tk.Label(frame, text='k_1').grid(row=2, column=0)
    tk.Label(frame, text='k_2').grid(row=2, column=2)
    tk.Label(frame, text='p_1').grid(row=3, column=0)
    tk.Label(frame, text='p_2').grid(row=3, column=2)
    entry_f_x = tk.Scale(frame, from_=10, to=max_f, orient=tk.HORIZONTAL, command=callback)
    entry_c_x = tk.Scale(frame, from_=0, to=img_width, orient=tk.HORIZONTAL, command=callback)
    # entry_f_y = tk.Scale(frame, from_=0, to=max_f)
    entry_c_y = tk.Scale(frame, from_=0, to=img_height, orient=tk.HORIZONTAL, command=callback)
    entry_k_1 = tk.Scale(frame, from_=-5e-3, to=5e-3, orient=tk.HORIZONTAL, resolution=1e-8, command=callback)
    entry_k_2 = tk.Scale(frame, from_=-3e-6, to=3e-6, orient=tk.HORIZONTAL, resolution=1e-9, command=callback)
    entry_p_1 = tk.Scale(frame, from_=-0.1, to=0.1, orient=tk.HORIZONTAL, resolution=0.001, command=callback)
    entry_p_2 = tk.Scale(frame, from_=-0.1, to=0.1, orient=tk.HORIZONTAL, resolution=0.001, command=callback)

    for row in range(4):
        tk.Grid.rowconfigure(frame, row, weight=1)
        for col in (0, 2):
            tk.Grid.columnconfigure(frame, col, weight=1)
            tk.Grid.columnconfigure(frame, col + 1, weight=2)

    entry_f_x.grid(row=0, column=1, sticky=tk.EW)
    entry_c_x.grid(row=0, column=3, sticky=tk.EW)
    # entry_f_y.grid(row=1, column=1, sticky=tk.EW)
    entry_c_y.grid(row=1, column=3, sticky=tk.EW)
    entry_k_1.grid(row=2, column=1, sticky=tk.EW)
    entry_k_2.grid(row=2, column=3, sticky=tk.EW)
    entry_p_1.grid(row=3, column=1, sticky=tk.EW)
    entry_p_2.grid(row=3, column=3, sticky=tk.EW)

    entry_c_x.set(img_width / 2)
    entry_c_y.set(img_height / 2)
    entry_f_x.set(max_f / 2)

    master.mainloop()
