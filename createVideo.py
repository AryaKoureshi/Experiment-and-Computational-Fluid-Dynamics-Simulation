import cv2
import os
import numpy as np

image_folder = './images/'

output_video_name = 'output_video.mp4'

first_image = cv2.imread(os.path.join(image_folder, os.listdir(image_folder)[0]))
height, width, layers = first_image.shape

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video_name, fourcc, 16, (width, height))

filenumbers = np.linspace(100, 47700, 477)
for fnum in filenumbers:
    if fnum <1000:
        fileName = 'SYS-0'
    else:
        fileName = 'SYS-'
    img = cv2.imread(os.path.join(image_folder, fileName+str(int(fnum))+".png"))
    video.write(img)

video.release()

print("Video created successfully.")
