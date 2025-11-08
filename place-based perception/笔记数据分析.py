import re
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC', 'STFangsong']


from collections import Counter

# 加载停用词表
stopwords_file = 'stopwords.txt'
with open(stopwords_file, "r", encoding='utf-8') as words:
    stopwords = [i.strip() for i in words]


def segment_text(texts):
    segmented_texts = []
    for text in texts:
        if len(text) == 0:
            continue

        seg_list = ' '.join(jieba.lcut(text, cut_all=True))
        segmented_texts.append(seg_list)
    return segmented_texts


# 绘制词云图
def generate_wordcloud(text):
    # windows 电脑 选择这一行代码
    wordcloud = WordCloud(width=1000,
                          height=700,
                          background_color='white',  # 背景颜色
                          font_path='simhei.ttf',  # 字体
                          scale=15,  # 间隔
                          contour_width=5,  # 整个内容显示的宽度
                          contour_color='red',  # 内容显示的颜色 红色边境
                          ).generate(text)
    # mac 电脑 选择这一行代码
    # wordcloud = WordCloud(width=1000,
    #                       height=700,
    #                       background_color='white',  # 背景颜色
    #                       font_path='/System/Library/Fonts/Hiragino Sans GB.ttc',  # 字体
    #                       scale=15,  # 间隔
    #                       contour_width=5,  # 整个内容显示的宽度
    #                       contour_color='red',  # 内容显示的颜色 红色边境
    #                       ).generate(text)

    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


def clean_text(text):
    text = str(text)
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"\[\S+\]", "", text)  # 去除表情符号
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)  # 去除网址

    # 去除停用词
    for word in stopwords:
        text = text.replace(word, '')

    text = re.sub(r"\s+", " ", text)  # 合并正文中过多的空格

    # 去除停用词
    for word in stopwords:
        text = text.replace(word, '')

    text = re.sub(r"\s+", " ", text)  # 合并正文中过多的空格
    text = text.strip().replace(' ', '')  # 去除空格
    return text.strip()


def plot_word_frequency(text):
    word_list = jieba.cut(text)
    word_list = [word for word in word_list if word.strip()]
    word_counter = Counter(word_list)
    word_freq = word_counter.most_common(20)  # 取出现频率最高的前20个词语及其频次
    words, freqs = zip(*word_freq)

    plt.figure(figsize=(10, 8))
    plt.bar(words, freqs)
    plt.xticks(rotation=45)
    plt.xlabel('词语')
    plt.ylabel('频次')
    plt.title('笔记内容词语频次图')
    plt.show()


data = pd.read_csv('话题笔记数据.csv')

xhs_content = data['笔记内容']

xhs_content = xhs_content.drop_duplicates()
print(xhs_content.head())

# 数据清洗
xhs_content = xhs_content.apply(clean_text)

# 对微博内容进行分词
segment_content = segment_text(xhs_content)

# 绘制词云图
content_text = ' '.join(segment_content)
generate_wordcloud(content_text)

# 绘制总的词频图
total_text = ' '.join(xhs_content)
plot_word_frequency(total_text)

ip_location = data['IP属地']

# 绘制饼状图
pie_labels = ip_location.value_counts()[:10].index
plt.pie(ip_location.value_counts()[:10].values,
        labels=pie_labels, autopct='%1.2f%%', shadow=True)
plt.title("话题中IP属地的占比")
plt.show()

count = data[['笔记收藏数量', '笔记评论数量', '笔记点赞数量']]
print(count.describe().astype(int))


def convert_number(num_str):
    if isinstance(num_str, str):
        if '千' in num_str:
            return int(float(num_str.replace('千', '')) * 1000)
        elif '万' in num_str:
            return int(float(num_str.replace('万', '')) * 10000)
    return int(num_str)

# 应用转换函数到每一列
for col in count.columns:
    count.loc[:, col] = count.loc[:, col].apply(convert_number)

# 绘制柱状图
numeric_columns = count.select_dtypes(include=[int, float]).columns
count[numeric_columns].sum(axis=0).plot(kind='bar')
plt.xticks(rotation=0)
plt.title("话题中笔记收藏数量、评论数量、点赞数量总数")
plt.show()
