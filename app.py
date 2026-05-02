from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import joblib
import json
import base64
import os
import tempfile
from io import BytesIO
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

app = Flask(__name__)
CORS(app)


models = {}

def load_models():
    global models
    print("Đang tải các mô hình...")
    models["dl_model"] = load_model("fruits/mobilenet_softmax_model.h5")
    models["extractor"] = load_model("fruits/mobilenet_feature_extractor.h5")
    models["svm"] = joblib.load("fruits/svm_classifier.pkl")
    with open("fruits/class_names.json", "r") as f:
        models["class_names"] = json.load(f)
    print("Tải mô hình thành công!")


def preprocess_image(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img_array = img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "models_loaded": bool(models)})


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Không có file ảnh được gửi lên"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Tên file rỗng"}), 400

    image_bytes = file.read()

    try:
        img_array = preprocess_image(image_bytes)
    except Exception as e:
        return jsonify({"error": f"Không thể xử lý ảnh: {str(e)}"}), 400

    dl_pred_probs = models["dl_model"].predict(img_array, verbose=0)
    dl_pred_idx = int(np.argmax(dl_pred_probs, axis=1)[0])
    dl_pred_class = models["class_names"][dl_pred_idx]
    dl_confidence = float(dl_pred_probs[0][dl_pred_idx]) * 100

    top3_idx = np.argsort(dl_pred_probs[0])[::-1][:3]
    top3 = [
        {
            "label": models["class_names"][int(i)],
            "confidence": round(float(dl_pred_probs[0][i]) * 100, 2)
        }
        for i in top3_idx
    ]

    features = models["extractor"].predict(img_array, verbose=0)
    svm_pred_idx = int(models["svm"].predict(features)[0])
    svm_pred_class = models["class_names"][svm_pred_idx]

    img_b64 = image_to_base64(image_bytes)
    mime = file.content_type or "image/jpeg"

    return jsonify({
        "image_base64": img_b64,
        "image_mime": mime,
        "dl_prediction": {
            "class": dl_pred_class,
            "confidence": round(dl_confidence, 2),
            "top3": top3
        },
        "svm_prediction": {
            "class": svm_pred_class
        },
        "agreement": dl_pred_class == svm_pred_class
    })


if __name__ == "__main__":
    load_models()
    app.run(host="0.0.0.0", port=5000, debug=False)
