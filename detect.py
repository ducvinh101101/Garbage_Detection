import cv2
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from collections import Counter, defaultdict

from agent_core import run_agent_pipeline

# --- AI AGENT MOCK SETUP ---
# Trong thực tế, bạn sẽ dùng LangChain để khởi tạo Agent tại đây
def call_ai_agent(image_crop):
    """
    Hàm này đại diện cho AI Agent. Các bước nó sẽ làm:
    1. Phân loại chi tiết loại nhựa (GPT-4V / Mô hình phân loại nhựa riêng).
    2. Gọi RAG để lấy thông tin tái chế.
    3. Trả về câu trả lời cho Chatbot.
    """
    print("\n[AI AGENT] Đang phân tích hình ảnh cận cảnh...")

    # 1. Vision Tool (Giả lập GPT-4V hoặc model ResNet của bạn)
    # plastic_type = call_vision_model(image_crop)
    plastic_type = "PET (Nhựa số 1)"  # Giả lập kết quả
    print(f"[AI AGENT] Đã nhận diện được loại nhựa: {plastic_type}")

    # 2. RAG Tool (Giả lập truy vấn Vector DB)
    # rag_info = query_vector_db(f"Cách tái chế và địa điểm thu gom {plastic_type}")
    rag_info = f"Nhựa {plastic_type} có thể tái chế. Hãy rửa sạch và mang đến trạm thu gom GreenLife số 123 đường ABC."

    # 3. Output ra Chatbot
    response = f"Chatbot: Tôi thấy đây là {plastic_type}. {rag_info}"
    print(response)
    print("--------------------------------------------------\n")
    return response


# --- VISION PIPELINE ---
def preprocess_image(img):
    # Giữ nguyên code tiền xử lý cực tốt của bạn
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
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    img = img.astype(np.float32)
    img = preprocess_input(img)
    return img


def main():
    yolo_model = YOLO("runs11s_50/detect/train/weights/best.pt")
    cls_model = load_model("garbage_vgg16_model.h5")
    CLASS_NAMES = {0: "battery", 1: "biological", 2: "cardboard", 3: "clothes", 4: "glass", 5: "metal", 6: "paper",
                   7: "plastic", 8: "shoes", 9: "trash"}

    track_history = defaultdict(list)
    final_predictions = {}
    MAX_VOTES = 5

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở Video/Camera")
        return

    print("Hệ thống đã sẵn sàng. Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        results = yolo_model.track(frame, persist=True, tracker="bytetrack.yaml", conf=0.1, verbose=False)

        plastic_detected_crop = None  # Biến lưu ảnh nhựa để chuẩn bị chụp

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            # Lấy danh sách ID hiện tại để dọn dẹp các ID đã biến mất
            current_ids = set(track_ids)
            keys_to_delete = [k for k in final_predictions.keys() if k not in current_ids]
            for k in keys_to_delete:
                del final_predictions[k]

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                cropped = frame[y1:y2, x1:x2]

                if track_id not in final_predictions:
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
                    predicted_class = final_predictions[track_id]
                    display_text = f"ID:{track_id} {predicted_class}"
                    color = (0, 255, 0)

                    # LOGIC TRIGGER KHI PHÁT HIỆN NHỰA
                    if predicted_class == "plastic":
                        color = (0, 0, 255)  # Đổi sang màu Đỏ để gây chú ý
                        display_text += " -> Nhan 'C' de chup!"
                        plastic_detected_crop = cropped.copy()  # Lưu lại khung hình chứa đồ nhựa
                else:
                    pass

                # Vẽ Box
                try:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - 25), (x1 + tw, y1), color, -1)
                    cv2.putText(frame, display_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                except Exception as e:
                    pass

        cv2.imshow("Trash Detection & AI Agent Trigger", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        # KHI NGƯỜI DÙNG BẤM 'C' VÀ CÓ NHỰA TRÊN MÀN HÌNH
        elif key == ord('c') and plastic_detected_crop is not None:
            cv2.putText(frame, "Đang gui cho AI Agent...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            cv2.imshow("Trash Detection & AI Agent Trigger", frame)
            cv2.waitKey(1)  # Force update UI

            # Kích hoạt Agent xử lý ảnh này
            call_ai_agent(plastic_detected_crop)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()