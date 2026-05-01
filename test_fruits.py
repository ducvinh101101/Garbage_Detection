import cv2
import numpy as np
import matplotlib.pyplot as plt
import joblib
import json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array


def predict_single_image(img_path, dl_model_path, extractor_path, svm_path, classes_path):
    print("Đang tải các mô hình...")
    model_dl = load_model(dl_model_path)
    extractor = load_model(extractor_path)
    model_svm = joblib.load(svm_path)

    with open(classes_path, "r") as f:
        class_names = json.load(f)

    print(f"Đang xử lý ảnh: {img_path}")
    original_img = cv2.imread(img_path)
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    dl_pred_probs = model_dl.predict(img_array, verbose=0)
    dl_pred_idx = np.argmax(dl_pred_probs, axis=1)[0]
    dl_pred_class = class_names[dl_pred_idx]
    dl_confidence = dl_pred_probs[0][dl_pred_idx] * 100

    features = extractor.predict(img_array, verbose=0)
    svm_pred_idx = model_svm.predict(features)[0]
    svm_pred_class = class_names[svm_pred_idx]

    plt.figure(figsize=(6, 6))
    plt.imshow(original_img)
    plt.axis("off")

    title = (f"Softmax Pred: {dl_pred_class} ({dl_confidence:.2f}%)\n"
             f"SVM Pred: {svm_pred_class}")
    plt.title(title, fontsize=14, color='blue', fontweight='bold')
    plt.show()

    print("-" * 50)
    print("KẾT QUẢ DỰ ĐOÁN:")
    print(f"1. Mô hình Deep Learning (Softmax): {dl_pred_class} - Độ tự tin: {dl_confidence:.2f}%")
    print(f"2. Mô hình kết hợp (MobileNet + SVM): {svm_pred_class}")
    print("-" * 50)


test_image_path = "fruits/test/img_2.png"

predict_single_image(
    img_path=test_image_path,
    dl_model_path="fruits/mobilenet_softmax_model.h5",
    extractor_path="fruits/mobilenet_feature_extractor.h5",
    svm_path="fruits/svm_classifier.pkl",
    classes_path="fruits/class_names.json"
)