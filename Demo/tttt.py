import numpy as np

a = [
    [1, 2, 3, 0, 1],
    [4, 5, 6, 1, 2],
    [7, 8, 9, 0, 3],
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 0]
]

npa = np.array(a)
print("Input Array a:\n", npa)

b = [
    [0, 1, 0],
    [1, -1, 1],
    [0, 1, 0]
]

npb = np.array(b)
print("\nKernel b:\n", npb)

input_height, input_width = npa.shape
kernel_height, kernel_width = npb.shape
stride = 1
padding = 0

output_height = (input_height - kernel_height + 2 * padding) // stride + 1
output_width = (input_width - kernel_width + 2 * padding) // stride + 1

output = np.zeros((output_height, output_width))

for i in range(output_height):
    for j in range(output_width):

        roi_start_row = i * stride - padding
        roi_start_col = j * stride - padding
        roi_end_row = roi_start_row + kernel_height
        roi_end_col = roi_start_col + kernel_width

        roi = npa[roi_start_row:roi_end_row, roi_start_col:roi_end_col]


        if roi.shape == npb.shape:
             convolution_result = np.sum(roi * npb)
        else:
            convolution_result = 0

        output[i, j] = convolution_result

print("\nOutput Array (Convolution Result):\n", output)