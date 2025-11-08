from transformers import AutoModel, AutoTokenizer
import torch
import os

# 设置 Hugging Face Hub 的端点为镜像网站
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
print(f"当前使用的 HF_ENDPOINT: {os.getenv('HF_ENDPOINT')}")

model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
cache_dir = r"E:\Sherry\研究生"

# 增加超时时间
timeout = 30

try:
    # 下载模型到本地
    model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir, mirror="https://hf-mirror.com", timeout=timeout)
    # 下载 tokenizer 分词器到本地
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, mirror="https://hf-mirror.com",
                                              timeout=timeout)
    print("模型下载完成")
except Exception as e:
    print(f"下载模型时出现错误: {e}")

# 安装的时候采用cmd，输入
# set HF_ENDPOINT=https://hf-mirror.com
# C:\Users\Administrator\AppData\Local\Programs\Python\Python38\python.exe "E:/Sherry/研究生/4 城市设计分析技术/作业一 水乡论文转化/python根据小红书关键词爬取所有文章数据/词库调用.py"