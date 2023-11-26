import time

from PIL import Image
import numpy as np
from numba import cuda

render_time = None

__TPB = 32
__im_array = None


def set_image(image):
    global __im_array
    __im_array = np.array(image)


@cuda.jit()
def __blur_gpu(img, output, radius):
    y, x = cuda.grid(2)

    if y < img.shape[0] and x < img.shape[1]:
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

        output[y, x, 0] = avg_r
        output[y, x, 1] = avg_g
        output[y, x, 2] = avg_b

        if img.shape[2] > 3:
            output[y, x, 3] = avg_a


def blur(radius):
    global __im_array, render_time

    if __im_array is None:
        print("Call 'set_image(image)' before calling blur!")
        return

    d_im_array = cuda.to_device(__im_array)
    d_output_array = cuda.to_device(np.zeros_like(__im_array))

    threads_per_block = (__TPB, __TPB)
    blocks_per_grid = ((__im_array.shape[0] + threads_per_block[0] - 1) // threads_per_block[0],
                       (__im_array.shape[1] + threads_per_block[1] - 1) // threads_per_block[1])

    last_time = time.time()

    __blur_gpu[blocks_per_grid, threads_per_block](d_im_array, d_output_array, radius)

    cuda.synchronize()
    render_time = round(time.time() - last_time, 3)

    return Image.fromarray(d_output_array.copy_to_host())
