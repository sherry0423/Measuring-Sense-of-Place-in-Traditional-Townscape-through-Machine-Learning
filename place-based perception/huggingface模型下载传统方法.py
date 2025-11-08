from transformers import AutoModel, AutoTokenizer
import torch

model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
cache_dir = r"E:\Sherry\研究生\4 城市设计分析技术\作业一 水乡论文转化\python根据小红书关键词爬取所有文章数据"
# 下载模型到本地
model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
# 下载tokenizer分词器到本地
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
print("模型下载完成")