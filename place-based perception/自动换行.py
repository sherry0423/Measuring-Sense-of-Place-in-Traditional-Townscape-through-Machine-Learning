encodings = ['utf-8', 'gbk', 'gb2312']

for encoding in encodings:
    try:
        # 使用当前编码读取文件
        with open('杭州吉祥里word.txt', 'r', encoding=encoding) as f:
            content = f.read()

        # 替换逗号为换行符
        new_content = content.replace(',', '\n')

        # 将修改后的内容写回文件
        with open('杭州吉祥里word_enter.txt', 'w', encoding=encoding) as f:
            f.write(new_content)

        print(f"使用 {encoding} 编码处理成功。")
        break
    except UnicodeDecodeError:
        continue
else:
    print("无法找到合适的编码处理文件。")