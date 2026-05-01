from tensorflow.keras.models import load_model
import numpy as np
import cv2
import json
import matplotlib.pyplot as plt

# load model
model = load_model("vgg16_custom/fruits.keras")

# load class names
with open("vgg16_custom/class_indices.json", "r") as f:
    class_indices = json.load(f)

idx_to_class = {v: k for k, v in class_indices.items()}

# load image
img_path = "test/img_8.png"
img = cv2.imread(img_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img_resized = cv2.resize(img, (224, 224))
img_norm = img_resized / 255.0
img_input = np.expand_dims(img_norm, axis=0)

# predict
pred = model.predict(img_input)
pred_class = np.argmax(pred)
confidence = np.max(pred)

pred_label = idx_to_class[pred_class]

# show
plt.imshow(img)
plt.title(f"{pred_label} ({confidence:.2f})")
plt.axis("off")
plt.show()