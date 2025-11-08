import os
import cv2
import numpy as np
import pandas as pd
import base64
from keras.models import load_model
from scipy.spatial.distance import jensenshannon
from tensorflow.keras.applications.resnet50 import preprocess_input

model = load_model('fine_tuned_model.h5')

classes = ['B', 'C', 'O', 'T', 'W']

input_folder = "panlongtiandi_street_view/panlongtiandi_street_view_linshui_cropped_enhanced"
output_csv = "panlongtiandi_street_view/panlongtiandi_street_view_linshui_classification_results.csv"
output_html = "panlongtiandi_street_view/panlongtiandi_street_view_linshui_classification_results.html"

image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.jpg')]
print(f" 发现 {len(image_files)} 张 JPG 图片，开始筛选并分类...")


def is_mostly_white(image, threshold=0.5):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_pixels = np.sum(gray >= 245)
    total_pixels = gray.size
    white_ratio = white_pixels / total_pixels
    return white_ratio > threshold


def encode_image_to_base64(image_path):

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f'<img src="data:image/png;base64,{encoded_string}" width="100">'


def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f" 读取失败: {image_path}")
        return None, None

    if img.shape[-1] == 4:
        alpha_channel = img[:, :, 3]
        mask = alpha_channel > 0
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img[~mask] = (255, 255, 255)

    if is_mostly_white(img, threshold=0.5):
        print(f" 跳过：{image_path} - 过多白色像素")
        return None, None

    img_resized = cv2.resize(img, (224, 224))
    img_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_resized = img_resized / 255.0

    img_preview = encode_image_to_base64(image_path)

    return img_resized, img_preview


results = []
batch_images = []
valid_image_files = []
image_previews = []

for i, file in enumerate(image_files):
    image_path = os.path.join(input_folder, file)

    img, img_preview = preprocess_image(image_path)
    if img is None:
        continue

    batch_images.append(img)
    valid_image_files.append(file)
    image_previews.append(img_preview)


    if len(batch_images) >= 32 or i == len(image_files) - 1:
        batch_images = np.array(batch_images)
        preds = model.predict(batch_images)
        labels = np.argmax(preds, axis=1)

        for j, img_file in enumerate(batch_images):
            filename = valid_image_files[j]
            predicted_label = classes[labels[j]]
            preview = image_previews[j]
            results.append([filename, predicted_label, preview] + list(preds[j]))

        batch_images = []
        valid_image_files = []
        image_previews = []

df = pd.DataFrame(results, columns=['filename', 'predicted_label', 'image_preview'] + classes)
df.to_csv(output_csv, index=False)
print(f" 分类结果已保存到 {output_csv}")

df.to_html(output_html, escape=False)  # 允许 HTML 标签生效
print(f" HTML 文件已生成，可在浏览器中打开 {output_html}")


classified_csv = "panlongtiandi_street_view/panlongtiandi_street_view_linshui_classification_results.csv"
reference_csv = "material_ratios_by_original_image.csv"
material_classes = ['B', 'C', 'O', 'T', 'W']

df = pd.read_csv(classified_csv)
df["original_image"] = df["filename"].apply(lambda x: x.split('_')[-1])
grouped = df.groupby("original_image")[material_classes].mean().reset_index()

reference_df = pd.read_csv(reference_csv)

def compute_js_score(row, reference_vector):
    input_vec = row[material_classes].values.astype(np.float64)
    reference_vector = reference_vector.astype(np.float64)

    input_vec /= input_vec.sum()
    reference_vector /= reference_vector.sum()

    return 1 - jensenshannon(input_vec, reference_vector)

scores = []
for _, row in grouped.iterrows():
    similarities = [
        compute_js_score(row, ref_row[material_classes].values)
        for _, ref_row in reference_df.iterrows()
    ]
    avg_score = sum(sorted(similarities, reverse=True)[:5]) / 5
    scores.append(avg_score)

grouped["material_similarity_score"] = scores
grouped.to_csv("panlongtiandi_street_view/panlongtiandi_street_view_linshui_material_similarity_scored_2.csv", index=False)
print(" 打分已完成")
