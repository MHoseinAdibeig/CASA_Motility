import cv2
import numpy as np

class imclearborder:

    def imclearborder(self, Ibw):
        Ibw = np.array(Ibw, np.uint8)
        Ibw *= 255
        h, w = Ibw.shape[:2]
        for row in range(h):
            if Ibw[row, 0] == 255:
                cv2.floodFill(Ibw, None, (0, row), 0)
            if Ibw[row, w - 1] == 255:
                cv2.floodFill(Ibw, None, (w - 1, row), 0)

        for col in range(w):
            if Ibw[0, col] == 255:
                cv2.floodFill(Ibw, None, (col, 0), 0)
            if Ibw[h - 1, col] == 255:
                cv2.floodFill(Ibw, None, (col, h - 1), 0)
        Iclearborder = Ibw
        return Iclearborder