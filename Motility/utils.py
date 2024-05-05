import cv2
import numpy as np







def return_first_NaN_index(list):  # returns -1 if no NAN was present
    for idx in range(len(list)):
        if np.isnan(list[idx]) == True:
            return idx
    return -1


def runtime_optimization(number_of_sperms, Opt_flag):
    pass


def get_grayscale_frames_from_paths(list_of_paths):
    frames = []
    for i in list_of_paths:
        img = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        frames.append(img)
    return frames


def get_BGR_frames_from_paths(list_of_paths):
    frames = []
    for i in list_of_paths:
        img = cv2.imread(i)
        # cv2.imshow('h', img)
        # cv2.waitKey(0)
        frames.append(img)
    return frames


def write_a_frame(frame, number, path):  # todo
    # template: image_1.jpg
    path = path + "image_" + str(number) + ".jpg"
    cv2.imwrite(path, frame)


def get_avg_frame(frames, step_size=1):
    selected_frames = []
    for i in range(0, 60, step_size):
        selected_frames.append(frames[i])

    print('Length of selected frames for averaging = ', len(selected_frames))
    avg_img = np.mean(selected_frames, axis=0)
    avg_img = avg_img.astype(np.uint8)
    return avg_img


def imadjust(src, tol=1, vin=[0, 255], vout=(0, 255)):
    # src : input one-layer image (numpy array)
    # tol : tolerance, from 0 to 100.
    # vin  : src image bounds
    # vout : dst image bounds
    # return : output img

    dst = src.copy()
    tol = max(0, min(100, tol))

    if tol > 0:
        # Compute in and out limits
        # Histogram
        hist = np.zeros(256, dtype=np.int)
        for r in range(src.shape[0]):
            for c in range(src.shape[1]):
                hist[src[r, c]] += 1
        # Cumulative histogram
        cum = hist.copy()
        for i in range(1, len(hist)):
            cum[i] = cum[i - 1] + hist[i]

        # Compute bounds
        total = src.shape[0] * src.shape[1]
        low_bound = total * tol / 100
        upp_bound = total * (100 - tol) / 100
        vin[0] = bisect.bisect_left(cum, low_bound)
        vin[1] = bisect.bisect_left(cum, upp_bound)

    # Stretching
    scale = (vout[1] - vout[0]) / (vin[1] - vin[0])
    for r in range(dst.shape[0]):
        for c in range(dst.shape[1]):
            vs = max(src[r, c] - vin[0], 0)
            vd = min(int(vs * scale + 0.5) + vout[0], vout[1])
            dst[r, c] = vd
    return dst



