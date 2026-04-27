import cv2
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from collections import Counter, defaultdict


def preprocess_image(img):
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.uint8)
    img = cv2.GaussianBlur(img, (3, 3), 0)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    v = v.astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    v = clahe.apply(v)

    s = np.clip(s * 0.9, 0, 255).astype(np.uint8)

    hsv = cv2.merge([h, s, v])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)

    img = img.astype(np.float32)
    img = preprocess_input(img)
    return img


yolo_model = YOLO("runs11s_50/detect/train/weights/best.pt")
cls_model = load_model("garbage_vgg16_model.h5")

CLASS_NAMES = {0: "battery", 1: "biological", 2: "cardboard", 3: "clothes", 4: "glass", 5: "metal", 6: "paper", 7: "plastic", 8: "shoes", 9: "trash"}

track_history = defaultdict(list)
final_predictions = {}

MAX_VOTES = 5

def process_video(video_source=0):
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Không thể mở Video/Camera")
        return

    while True:
        ret, frame = cap.isOpened(), cap.read()[1]
        if not ret or frame is None:
            break

        results = yolo_model.track(frame, persist=True, tracker="bytetrack.yaml", conf=0.1, verbose=False)

        if results[0].boxes is not None and results[0].boxes.id is not None:

            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                if track_id not in final_predictions:
                    cropped = frame[y1:y2, x1:x2]

                    if cropped.size > 0:
                        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                        processed_img = preprocess_image(cropped_rgb)
                        input_tensor = np.expand_dims(processed_img, axis=0)

                        preds = cls_model.predict(input_tensor, verbose=0)
                        class_idx = np.argmax(preds[0])

                        track_history[track_id].append(class_idx)

                        if len(track_history[track_id]) >= MAX_VOTES:
                            most_common_class = Counter(track_history[track_id]).most_common(1)[0][0]
                            final_predictions[track_id] = CLASS_NAMES.get(most_common_class, "Unknown")

                            del track_history[track_id]
                        else:
                            temp_label = CLASS_NAMES.get(class_idx, "Unknown")
                            display_text = f"ID:{track_id} {temp_label} (Voting...)"
                            color = (0, 165, 255)

                if track_id in final_predictions:
                    display_text = f"ID:{track_id} {final_predictions[track_id]}"
                    color = (0, 255, 0)
                else:

                    pass

                try:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - 25), (x1 + tw, y1), color, -1)
                    cv2.putText(frame, display_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                except Exception as e:
                    pass

        cv2.imshow("YOLO Tracking + VGG16 Classification", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


process_video(0)