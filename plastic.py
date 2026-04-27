import cv2
import numpy as np
import matplotlib.pyplot as plt

def pipeline(image_path):
    images = []
    titles = []

    # 1. Read
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    images.append(img_rgb)
    titles.append("Original")

    # 2. Resize
    img_resized = cv2.resize(img, (224, 224))
    images.append(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    titles.append("Resized")

    # 3. Gaussian Blur (nhẹ thôi)
    blur = cv2.GaussianBlur(img_resized, (3,3), 0)
    images.append(cv2.cvtColor(blur, cv2.COLOR_BGR2RGB))
    titles.append("Gaussian")

    # 4. Gray
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    images.append(gray)
    titles.append("Gray")

    # 5. CLAHE (🔥 QUAN TRỌNG)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray_clahe = clahe.apply(gray)
    images.append(gray_clahe)
    titles.append("CLAHE")

    # 6. Canny Edge (thay threshold)
    edges = cv2.Canny(gray_clahe, 50, 150)
    images.append(edges)
    titles.append("Canny")

    # 7. Dilate (nối biên lại)
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    images.append(dilated)
    titles.append("Dilate")

    # 8. Find contour → ROI
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # lấy contour lớn nhất
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        # padding tránh cắt sát quá
        pad = 10
        x = max(x - pad, 0)
        y = max(y - pad, 0)
        w = min(w + 2*pad, 224 - x)
        h = min(h + 2*pad, 224 - y)

        roi = img_resized[y:y+h, x:x+w]
    else:
        roi = img_resized

    images.append(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    titles.append("ROI")

    # 9. Resize lại ROI về chuẩn model
    roi = cv2.resize(roi, (224, 224))
    images.append(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    titles.append("ROI Resize")

    # 10. Normalize (mean-std)
    roi_norm = roi.astype(np.float32)
    roi_norm = (roi_norm - np.mean(roi_norm)) / (np.std(roi_norm) + 1e-7)

    # để visualize lại
    norm_vis = cv2.normalize(roi_norm, None, 0, 255, cv2.NORM_MINMAX)
    images.append(norm_vis.astype(np.uint8))
    titles.append("Normalize")

    # # 11. Augmentation (ví dụ)
    # flip = cv2.flip(roi, 1)
    # images.append(cv2.cvtColor(flip, cv2.COLOR_BGR2RGB))
    # titles.append("Flip")

    # ===== HIỂN THỊ 1 HÀNG =====
    n = len(images)
    rows = 2
    cols = (n + 1) // 2

    plt.figure(figsize=(4*cols, 6))


    for i in range(n):
        plt.subplot(rows, cols, i+1)
        if len(images[i].shape) == 2:
            plt.imshow(images[i], cmap='gray')
        else:
            plt.imshow(images[i])
        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()

    return roi_norm  # dùng cho model



# TEST
pipeline("jj/img.png")