
import os
import cv2
import numpy as np
import pandas as pd
# from keras.utils import img_to_array
from tensorflow.keras.utils import img_to_array
import tensorflow as tf
from config import config
from Build_model import Build_model


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
config1 = tf.compat.v1.ConfigProto()
config1.gpu_options.allow_growth = True
tf.compat.v1.Session(config=config1)


class ImageClassifier:
    def __init__(self, model_path, input_folder, output_excel):
        self.model_path = model_path
        self.input_folder = input_folder
        self.output_excel = output_excel
        self.model = None
        self.classes = self.load_classes()


        if not os.path.exists(self.output_excel):
            df = pd.DataFrame(columns=["Image Name", "Predicted Label", "Prob_W"])
            df.to_excel(self.output_excel, index=False)

    def load_classes(self):
        """加载类别索引"""
        with open('train_class_idx.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]

    def load_model(self):
        """加载模型"""
        print("Loading model...")
        self.model = Build_model(config).build_mymodel()
        self.model.load_weights(self.model_path)
        print("Model loaded successfully!")

    def preprocess_image(self, img_path):
        """预处理图片"""
        image = cv2.imread(img_path)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        thre_img = cv2.threshold(gray_img, 200, 255, cv2.THRESH_TRUNC)[1]
        mask = np.where(thre_img > 190)
        image[mask] = 255

        img1, img2 = image.copy(), image.copy()
        mask1 = np.where(np.logical_or(thre_img < 130, thre_img > 190))
        mask2 = np.where(thre_img > 180)
        img1[mask1], img2[mask2] = 255, 255

        img1 = cv2.resize(img1, (config.normal_size, config.normal_size))
        img2 = cv2.resize(img2, (config.normal_size, config.normal_size))

        img1 = img_to_array(img1) / 255.0
        img2 = img_to_array(img2) / 255.0

        return np.expand_dims(img1, axis=0), np.expand_dims(img2, axis=0)

    def predict_image(self, img_path):

        img1, img2 = self.preprocess_image(img_path)
        pred = self.model.predict([img2, img1])[0]

        predicted_class_idx = np.argmax(pred)
        predicted_label = self.classes[predicted_class_idx]
        confidence = max(pred)

        if predicted_label == "jiangnan_water_towns":
            prob_w = confidence
        else:
            prob_w = 1 - confidence

        return predicted_label, prob_w

    def process_images(self):

        img_files = [f for f in os.listdir(self.input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]


        if os.path.exists(self.output_excel):
            df_existing = pd.read_excel(self.output_excel)
            processed_images = set(df_existing["Image Name"])
        else:
            df_existing = pd.DataFrame(columns=["Image Name", "Predicted Label", "Prob_W"])
            processed_images = set()

        for img_name in img_files:

            if img_name in processed_images:
                print(f"Skipping {img_name}, already processed.")
                continue

            img_path = os.path.join(self.input_folder, img_name)
            try:
                predicted_label, prob_w = self.predict_image(img_path)
                print(f"Processed {img_name}: {predicted_label}, Prob_W={prob_w:.4f}")


                new_data = pd.DataFrame([[img_name, predicted_label, prob_w]],
                                        columns=["Image Name", "Predicted Label", "Prob_W"])
                df_existing = pd.concat([df_existing, new_data], ignore_index=True)
                df_existing.to_excel(self.output_excel, index=False)  # 立即保存

            except Exception as e:
                print(f"Error processing {img_name}: {e}")

        print(f"Classification results saved to {self.output_excel}")



if __name__ == "__main__":
    model_path = "model/ResNet-34/ResNet-34.h5"
    input_folder = "shuixiangjianyan_CRWHD_2"
    output_excel = "水乡检验样本_classification_results.xlsx"

    classifier = ImageClassifier(model_path, input_folder, output_excel)
    classifier.load_model()
    classifier.process_images()

