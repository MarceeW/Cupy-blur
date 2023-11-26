import math
import time

import PIL.ImageShow
from PIL import Image
import numpy as np
from numba import cuda

render_time = None

__im_array = None
__thread_count = 0
__block_count = 0


@cuda.jit()
def __blur_gpu(img, radius):
    y, x = cuda.grid(2)

    if y < img.shape[0] and x < img.shape[1]:
        y, x = cuda.grid(2)

        sum_r = 0
        sum_g = 0
        sum_b = 0

        xfrom = x - radius if x - radius >= 0 else 0
        yfrom = y - radius if y - radius >= 0 else 0

        xto = x + radius if x + radius <= img.shape[1] else img.shape[1]
        yto = y + radius if y + radius <= img.shape[0] else img.shape[0]

        area = 0

        cuda.syncthreads()

        for i in range(xfrom, xto):
            for j in range(yfrom, yto):
                area += 1
                sum_r += img[j, i, 0]
                sum_g += img[j, i, 1]
                sum_b += img[j, i, 2]

        avg_r = sum_r / area
        avg_g = sum_g / area
        avg_b = sum_b / area
        avg_a = 255

        img[y, x, 0] = avg_r
        img[y, x, 1] = avg_g
        img[y, x, 2] = avg_b

        if img.shape[2] > 3:
            img[y, x, 3] = avg_a


def __blur_cpu(img, radius):
    for x in range(img.shape[1]):
        for y in range(img.shape[0]):

            sum_r = 0
            sum_g = 0
            sum_b = 0

            xfrom = x - radius if x - radius >= 0 else 0
            yfrom = y - radius if y - radius >= 0 else 0

            xto = x + radius if x + radius <= img.shape[1] else img.shape[1]
            yto = y + radius if y + radius <= img.shape[0] else img.shape[0]

            area = 0

            for i in range(xfrom, xto):
                for j in range(yfrom, yto):
                    area += 1
                    sum_r += img[j, i, 0]
                    sum_g += img[j, i, 1]
                    sum_b += img[j, i, 2]

            avg_r = sum_r / area
            avg_g = sum_g / area
            avg_b = sum_b / area
            avg_a = 255

            img[y, x, 0] = avg_r
            img[y, x, 1] = avg_g
            img[y, x, 2] = avg_b

            if img.shape[2] > 3:
                img[y, x, 3] = avg_a


def blur(tpb, image, device, radius):
    global __im_array, __thread_count, __block_count, render_time

    __TPB = tpb

    __im_array = np.array(image)

    __thread_count = (__TPB, __TPB)
    __block_count = (math.ceil(__im_array.shape[0] / __thread_count[0]),
                     math.ceil(__im_array.shape[1] / __thread_count[1]))

    last_time = time.time()
    if device == "cpu":
        __blur_cpu(__im_array, radius)
    else:
        __blur_gpu[__block_count, __thread_count](__im_array, radius)

    render_time = round(time.time() - last_time, 3)
    return Image.fromarray(__im_array)
