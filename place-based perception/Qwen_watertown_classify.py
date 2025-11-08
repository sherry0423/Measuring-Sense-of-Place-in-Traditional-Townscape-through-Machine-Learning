import os
import csv
from openai import OpenAI

# 配置OpenAI客户端
client = OpenAI(
    api_key="sk-b859f6b526d94317a8bec8982606c7ba",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 分类规则
classification_rules = """
（1）剔除信息。
1、景区资质。例如：4A景区、开放式景区、永久免费。
2、景点名称。例如：觉海寺院，刘王庙戏台（具体地名）。
（2）公共设施。
1、建筑功能。例如：茶馆。
2、建筑空间。例如：临水茶座
3、配套设施。例如：乌篷船
（3）文化风貌。
1、自然景观。例如：水网密布、古运河、流水
2、建筑风貌。例如：古镇原貌、明清古建筑、白墙黑瓦、古色古香、青砖
3、特色文化。例如：道教文化
4、特色美食。例如：茶糕、梅花糕、新市茶糕、麦芽圆子、细沙羊尾。
5、古镇美誉。例如：浙北小上海，江南百老汇。
（4）行为活动。
1、行为活动。例如：小船游览、手摇船、古韵游船、浪漫夜游、运河旅拍。
（5）评价感受。
1、开发评价。例如：商业化程度不高、商业化水平不高。
2、氛围感受。例如：烟火气、慢生活。
3、情感共鸣。例如：童年的梦、江南梦。
"""


def classify_word(word):
    """
    调用通义千问 - max API对词汇进行分类
    """
    instruction = f'你是一个词汇分类助手。以下是分类规则：{classification_rules}。请仅用“(数字)数字”的格式对词汇“{word}”进行分类，第一个数字代表大类，第二个数字代表小类，不要包含任何解释内容。请注意，输出的结果只可能是以下组合中的一个：(1)1、(1)2、(2)1、(2)2、(2)3、(3)1、(3)2、(3)3、(3)4、(3)5、(4)1、(5)1、(5)2、(5)3'
    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {'role': 'system', 'content': instruction}
        ]
    )
    result = completion.choices[0].message.content
    result = result.strip()
    if result.startswith('(') and ')' in result and len(result.split(')')) == 2:
        major, minor = result.strip('()').split(')')
        if major.isdigit() and minor.isdigit():
            major, minor = int(major), int(minor)
            if 1 <= major <= 5 and (major != 4 or minor == 1):
                return result
    raise ValueError(f"模型输出格式错误: {result}")


def read_and_classify_csv(input_file, output_file):
    encodings = ['utf-8', 'gbk', 'gb2312']
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as infile, open(output_file, 'w', newline='',
                                                                          encoding='utf-8') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                # 写入表头
                writer.writerow(['原词', '分类结果'])
                for row in reader:
                    for word in row:
                        if word:
                            try:
                                classification = classify_word(word)
                                writer.writerow([word, classification])
                            except Exception as e:
                                print(f"对词汇 {word} 分类时出错：{e}")
            print(f"成功使用 {encoding} 编码读取文件。")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("无法使用提供的编码读取文件，请检查文件编码。")


if __name__ == "__main__":
    input_csv_file = 'test_singleword.csv'
    output_csv_file = 'output_test4.csv'
    read_and_classify_csv(input_csv_file, output_csv_file)
    print("分类完成，结果已保存到 output_test4.csv 文件中。")

