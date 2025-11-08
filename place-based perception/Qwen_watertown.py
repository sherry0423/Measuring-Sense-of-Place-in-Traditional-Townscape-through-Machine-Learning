import os
from openai import OpenAI
import csv
import re


# 过滤非文字字符
def filter_non_text(text):
    if isinstance(text, str):
        return ''.join(filter(lambda x: (32 <= ord(x) <= 126) or (0x4E00 <= ord(x) <= 0x9FFF), text))
    return text


client = OpenAI(
    api_key="sk-9d0605bd10104a24bbdaedc8b4f4ef64",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 读取CSV数据
def read_csv_data(file_path):
    encodings = ['utf-8', 'gbk', 'gb2312', 'UTF-8-SIG']
    for encoding in encodings:
        try:
            data = []
            with open(file_path, 'r', encoding=encoding) as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # 检查行是否为空
                        # 过滤评论中的非文字字符
                        comment = filter_non_text(row[0])
                        data.append(comment)
            return data
        except UnicodeDecodeError:
            continue
    print("无法用支持的编码读取文件，请检查文件编码。")
    return []


# 调用qwen-plus API进行情感分析和打分
def analyze_sentiment_and_score(comment):
    try:
        completion = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': f"请判断这条关于杭州吉祥里的评论的积极、消极属性，并给它打分（1-10,1分最消极，10分最积极，打分必须为1-10的区间内的整数）：{comment}"}
            ]
        )
        result = completion.choices[0].message.content
        # 解析分数
        score_match = re.search(r'(\d+)(?:/10)?分?', result)
        if score_match:
            score = int(score_match.group(1))
            return score
        else:
            print(f"未找到有效的分数信息，API响应内容: {completion.model_dump_json()}")
            return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"解析结果出错: {e}，API响应内容: {completion.model_dump_json()}")
        return None


# 提取积极评价的要素词汇
def extract_positive_elements(comment):
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user',
                 'content': f"请提取这条关于新市古镇的积极评价中让用户得出积极评价的要素的词汇（例如“白墙黑瓦”“水泥装饰”“新潮业态”，请注意提取的词汇必须在本条评论的原文中出现，不可修改。每个词之间用逗号间隔，只需要输出词即可，无需输出其他总起或总结的文字）：{comment}"}
            ]
        )
        result = completion.choices[0].message.content
        elements = result.split('，')
        return elements
    except (KeyError, ValueError, IndexError) as e:
        print(f"解析结果出错: {e}，API响应内容: {completion.model_dump_json()}")
        return []


# 主函数
def main():
    file_path = r'E:\Sherry\研究生\4 城市设计分析技术\作业一 水乡论文转化\python根据小红书关键词爬取所有文章数据\杭州吉祥里评价.csv'  # 替换为你的CSV文件路径
    data = read_csv_data(file_path)
    output_data = []
    max_elements = 0
    for comment in data:
        score = analyze_sentiment_and_score(comment)
        elements = []
        if score is not None and score > 0:  # 假设分数大于5为积极评价
            elements = extract_positive_elements(comment)
        output_row = [comment, score] + elements
        output_data.append(output_row)
        max_elements = max(max_elements, len(elements))
        print(f"评论：{comment}")
        print(f"打分：{score}")
        print(f"积极评价要素词汇：{elements}")
        print("-" * 50)

    # 生成表头
    header = ['评论', '打分'] + [f'积极评价要素词汇_{i + 1}' for i in range(max_elements)]

    # 生成新的CSV文件
    output_file_path = 'output_杭州吉祥里UGC.csv'
    with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(header)
        for row in output_data:
            # 补齐每行的列数
            row.extend([''] * (len(header) - len(row)))
            writer.writerow(row)
    print(f"新的CSV文件已生成：{output_file_path}")


if __name__ == "__main__":
    main()
