
import os
import cv2
import numpy as np


input_folder = "jixiangli_street_view/linshui"
output_folder = "jixiangli_street_view/jixiangli_street_view_linshui_cropped"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.jpg'):
        image_path = os.path.join(input_folder, filename)
        print(f"正在处理：{filename}")


        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f" 读取失败: {image_path}")
            continue

        h, w = image.shape[:2]


        if image.shape[-1] == 4:
            alpha_channel = image[:, :, 3]
            mask = alpha_channel > 0
            if np.count_nonzero(mask) == 0:
                print(f" {filename} 全部透明，跳过")
                continue


            binary = np.zeros((h, w), dtype=np.uint8)
            binary[mask] = 255

        else:

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)


        _, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)


        for i, stat in enumerate(stats):
            if stat[4] < 10000:
                labels[labels == i] = 0

        result = np.uint8(labels > 0) * 255


        window_size = (80, 80)
        threshold = 0.1
        rectangles = []
        centers = []


        for y in range(0, h, window_size[0]):
            for x in range(0, w, window_size[1]):
                window = binary[y:y + window_size[0], x:x + window_size[1]]
                white_pixels = np.count_nonzero(window == 255)
                ratio = white_pixels / (window_size[0] * window_size[1])

                if ratio >= threshold:
                    crop = image[y:y + window_size[0], x:x + window_size[1]]


                    if np.all(crop[:, :, :3] == 255):
                        continue

                    rectangles.append((x, y, x + window_size[1], y + window_size[0]))
                    center_x = (x + x + window_size[1]) // 2
                    center_y = (y + y + window_size[0]) // 2
                    centers.append((center_x, center_y))


        if len(rectangles) <= 10:
            for new_size in [80, 60]:
                window_size = (new_size, new_size)
                rectangles = []
                centers = []

                for y in range(0, h, window_size[0]):
                    for x in range(0, w, window_size[1]):
                        window = binary[y:y + window_size[0], x:x + window_size[1]]
                        white_pixels = np.count_nonzero(window == 255)
                        ratio = white_pixels / (window_size[0] * window_size[1])

                        if ratio >= threshold:
                            crop = image[y:y + window_size[0], x:x + window_size[1]]

                            # **跳过全白图像**
                            if np.all(crop[:, :, :3] == 255):
                                continue

                            rectangles.append((x, y, x + window_size[1], y + window_size[0]))
                            center_x = (x + x + window_size[1]) // 2
                            center_y = (y + y + window_size[0]) // 2
                            centers.append((center_x, center_y))

                if len(rectangles) > 10:
                    break

        # ** 裁剪 & 保存**
        for i, rect in enumerate(rectangles):
            x1, y1, x2, y2 = rect
            length = x2 - x1
            center_x, center_y = centers[i]
            cropped = image[y1:y2, x1:x2]


            new_filename = f'cropped{i}_{length}_{center_x}_{center_y}_{filename}'
            output_path = os.path.join(output_folder, new_filename)
            cv2.imwrite(output_path, cropped)

        print(f" {filename} 处理完成，生成 {len(rectangles)} 个裁剪区域")

