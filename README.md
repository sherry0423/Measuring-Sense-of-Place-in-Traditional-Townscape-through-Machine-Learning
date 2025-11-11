# Measuring-Sense-of-Place-in-Traditional-Townscape-through-Machine-Learning
We develop a series of Python-based tools for extracting spatial, visual, and semantic features, detailed in our paper “Measuring Sense of Place in Traditional Townscape through Machine Learning: An AI-Enhanced Method for Water-Town Heritage”. 

It integrates three main modules:
- Spatial (street–water morphology): CRWHD generation, ResNet-34 training & prediction
- Visual (façade materials): PSPNet segmentation, transfer learning classifier, JS divergence similarity
- Semantic (place-based perception): UGC crawling, LLM-based extraction, synonym matching
## Repository Structure
```
repo-root/
├─ spatial/                          # Road-water morphology
│  ├─ CRHD_TEST.py                   # Generate CRWHD diagrams from OSM
│  ├─ grid processing.py             # Create 900m grid centers (Shanghai, Suzhou)
│  ├─ train_model.py                 # Train ResNet-34 classifier
│  ├─ predict.py                     # Prediction pipeline
│  ├─ road classification.py         # Batch classification → Excel output
│  └─ suzhou_900m_Grid_Centers.csv   # Sample grid dataset
│
├─ visual/                           # Façade material analysis
│  ├─ cropping rectangular units.py  # Tile-based cropping (80×80)
│  ├─ normalization.py               # CLAHE enhancement & normalization
│  ├─ Extract_Segment_psnet_ade.py   # PSPNet ADE20K segmentation
│  ├─ transfer learning.py           # Fine-tune material classifier (ResNet-50)
│  ├─ material prediction.py         # Inference & JS divergence similarity
│  ├─ fine_tuned_model.h5            # Example trained weights
│  └─ lable.csv                      # ADE20K label mapping
│
├─ semantic/                         # Place-based perception
│  ├─ huggingface模型下载传统方法.py      # HF model download (standard)
│  ├─ huggingface模型下载镜像方法.py      # HF model download (mirror in CN)
│  ├─ Qwen_watertown.py              # UGC sentiment analysis & element extraction
│  ├─ Qwen_watertown_classify.py     # UGC element classification
│  ├─ 笔记数据分析.py                     # Word segmentation, wordcloud, stats
│  ├─ 杭州样本部分-19楼帖子爬取（仅标题）.py  # 19lou web crawler
│  ├─ 小红书关键词（本次使用）.py             # Xiaohongshu crawler
│  ├─ 近义词搜索.py                       # Synonym search (major category)
│  ├─ 近义词搜索_小类.py                   # Synonym search (major+sub category)
│  └─ 自动换行.py                         # Text preprocessing utility
│
├─ configs/                          # (add YAML/JSON configs here)
├─ models/                           # (ignored) trained weights
├─ data/                             # (ignored) raw/processed datasets
├─ figures/                          # (optional) generated plots
├─ requirements.txt
├─ LICENSE
└─ README.md
```
## Installation
We recommend conda to manage separate environments (TensorFlow/Keras vs PyTorch/Transformers vs MXNet).
```
# Create env for spatial/visual (TF/Keras)
conda create -n sop-tf python=3.9 -y
conda activate sop-tf
pip install -r requirements.txt

# Create env for semantic (PyTorch+Transformers)
conda create -n sop-nlp python=3.9 -y
conda activate sop-nlp
pip install torch transformers sentence-transformers pandas scikit-learn
```
**requirements.txt (core)**
```
osmnx
geopandas
shapely
networkx
matplotlib
opencv-python
numpy
pandas
tensorflow==2.10.*
keras==2.10.*
scikit-learn
mxnet
gluoncv
tqdm
openpyxl
jieba
wordcloud
beautifulsoup4
requests
sentence-transformers
transformers
```
## Project Cooperator
Thanks `https://github.com/jingmenglei` for implementing the **street pattern** and **material recognition** module!
