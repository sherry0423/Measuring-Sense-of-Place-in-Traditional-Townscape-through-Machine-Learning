
import os
import cv2
import numpy as np

input_folder = "jixiangli_street_view/jixiangli_street_view_linshui_cropped"
output_folder = "jixiangli_street_view/jixiangli_street_view_linshui_cropped_enhanced"
os.makedirs(output_folder, exist_ok=True)

def trans_img(image):

    resized_image = cv2.resize(image, (80, 80))

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2LAB)
    lab_image[:, :, 0] = clahe.apply(lab_image[:, :, 0])
    enhanced_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)

    return enhanced_image

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.jpg'):
        image_path = os.path.join(input_folder, filename)
        print(f"正在处理：{filename}")


        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f" 读取失败: {image_path}")
            continue

        processed_image = trans_img(image)

        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, processed_image)

print(f" 处理完成！所有增强的 JPG 图片已保存至 `{output_folder}`")
