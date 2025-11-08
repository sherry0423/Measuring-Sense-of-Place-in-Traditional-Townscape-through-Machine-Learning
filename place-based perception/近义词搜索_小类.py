# -*- coding: utf-8 -*-
"""
水乡词汇近义词匹配工具（支持外部文件导入）
需安装：pip install pandas sentence-transformers
"""

# ============== 需要用户修改的部分 ==============
# 1. 文件路径配置（根据实际文件类型选择一种）
A_FILE = "水乡词库.csv"  # 修改为 CSV 文件路径
B_FILE = "output_杭州吉祥里词库.csv"
FILE_TYPE = "csv"  # 修改为 csv

# 2. 表格配置（如果使用excel/csv需要设置）
COLUMN_NAME = "原词"  # 词汇所在的列名（excel/csv需要）
# SHEET_NAME 对于 CSV 文件不需要，可删除或注释掉
# SHEET_NAME = "Sheet1"

# 3. 相似度阈值
THRESHOLD = 0.72
# ==============================================

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import os
import time
import chardet


class VocabLoader:
    @staticmethod
    def load_vocab(file_path, file_type):
        """支持多种文件格式的词汇加载"""
        try:
            if file_type == "excel":
                # 手动指定引擎
                df = pd.read_excel(file_path, sheet_name=SHEET_NAME, engine='openpyxl')
                return df[COLUMN_NAME].tolist()
            elif file_type == "csv":
                with open(file_path, 'rb') as f:
                    rawdata = f.read()
                    # 多次尝试检测编码
                    result = chardet.detect(rawdata)
                    encodings_to_try = [result['encoding'], 'gbk', 'utf-8', 'utf-16', 'cp936']
                    for encoding in encodings_to_try:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding)
                            return df[COLUMN_NAME].tolist()
                        except UnicodeDecodeError:
                            continue
                    raise ValueError("无法确定文件编码")
            elif file_type == "txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            else:
                raise ValueError("不支持的文件类型，请选择 excel/csv/txt")
        except Exception as e:
            raise RuntimeError(f"文件读取失败：{str(e)}")


class SynonymDetector:
    def __init__(self, list_a, categories_b, sub_categories_b):
        self.model = SentenceTransformer('E:\\Sherry\\huggingface\\paraphrase-multilingual-MiniLM-L12-v2')
        self.embeddings_a = self.model.encode(list_a, convert_to_tensor=True)
        self.categories_b = categories_b
        self.sub_categories_b = sub_categories_b
        self.list_a = list_a

    def find_match(self, word_b, category, sub_category):
        emb_b = self.model.encode(word_b, convert_to_tensor=True)
        relevant_indices = [i for i, (cat, sub_cat) in enumerate(zip(self.categories_b, self.sub_categories_b))
                            if cat == category and sub_cat == sub_category]
        relevant_embeddings = self.embeddings_a[relevant_indices]
        relevant_words = [self.list_a[i] for i in relevant_indices]
        relevant_categories = [self.categories_b[i] for i in relevant_indices]
        relevant_sub_categories = [self.sub_categories_b[i] for i in relevant_indices]

        cos_scores = util.cos_sim(emb_b, relevant_embeddings)[0]
        max_score = np.max(cos_scores.numpy())
        max_index = np.argmax(cos_scores) if relevant_indices else -1

        if max_score > 0 and max_index >= 0:
            match_word = relevant_words[max_index]
            match_category = relevant_categories[max_index]
            match_sub_category = relevant_sub_categories[max_index]
            formatted_match = f"{match_category}+{match_sub_category}"
        else:
            formatted_match = "无相似词"

        return formatted_match, round(float(max_score), 3)


def main():
    print("正在加载词汇表...")

    # 加载词汇表
    try:
        list_a = VocabLoader.load_vocab(A_FILE, FILE_TYPE)
        list_b = VocabLoader.load_vocab(B_FILE, FILE_TYPE)
    except Exception as e:
        print(f" 错误：{str(e)}")
        return

    print(f"成功加载：\nA表词汇数：{len(list_a)}\nB表词汇数：{len(list_b)}")

    # 假设表B有一个名为“大类”和“小类”的列，这里先模拟加载
    with open(B_FILE, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        encodings_to_try = [result['encoding'], 'gbk', 'utf-8', 'utf-16', 'cp936']
        for encoding in encodings_to_try:
            try:
                df_b = pd.read_csv(B_FILE, encoding=encoding)
                categories_b = df_b["大类"].tolist()
                sub_categories_b = df_b["小类"].tolist()
                break
            except UnicodeDecodeError:
                continue
        else:
            print("无法确定文件编码")
            return

    # 初始化检测器
    detector = SynonymDetector(list_a, categories_b, sub_categories_b)
    results = []

    print("\n🔍 开始匹配分析...")
    start = time.time()

    # 批量处理
    for word, category, sub_category in zip(list_b, categories_b, sub_categories_b):
        match_word, score = detector.find_match(word, category, sub_category)
        results.append({
            "目标词": word,
            "匹配词": match_word,
            "相似度": score,
            "是否匹配": score > THRESHOLD
        })

    # 生成报告
    df_result = pd.DataFrame(results)
    output_file = "吉祥里匹配结果_小类.csv"
    df_result.to_csv(output_file, index=False, encoding='utf_8_sig')

    print(f"""
🎉 分析完成！
⏱ 耗时：{time.time() - start:.1f}秒
📁 结果已保存到：{os.path.abspath(output_file)}
    """)


if __name__ == "__main__":
    main()
