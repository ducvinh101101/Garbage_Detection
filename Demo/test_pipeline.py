import cv2
import numpy as np
from agent_core import run_agent_pipeline

print("Tạo ảnh dummy...")
# Create a dummy image representing a cropped plastic bottle (224x224 RGB)
dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
# give it some color
dummy_img[:, :, 1] = 255 # Green image

print("Chạy pipeline...")
run_agent_pipeline(dummy_img)
print("Xong!")
