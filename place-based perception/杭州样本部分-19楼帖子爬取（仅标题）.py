import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.19lou.com/search/thread?keyword=%E6%9D%AD%E5%B7%9E%E5%90%89%E7%A5%A5%E9%87%8C"
headers = {
    "Cookie": "f100big=u83; _DM_SID_=f2203cbd6172fac64c5b94f3a001b3ab; _DM_S_=ac5cae3289941e60112e21cd9602ce4c; reg_source=baidu.com; reg_kw=; reg_first=https%253A//www.19lou.com/; JSESSIONID=59A0C4914969BFA4102B150F04EEBFE5; f39big=ip138; Hm_lvt_5185a335802fb72073721d2bb161cd94=1745635321; HMACCOUNT=575B9BF7E3A4F8C6; fr_adv=; _Z3nY0d4C_=37XgPK9h; pm_count=%7B%7D; dayCount=%5B%5D; f100big_read=bq134; fr_adv_last=search_button_click_%u676D%u5DDE%u5409%u7965%u91CC; reg_step=9; screen=1156; _dm_tagnames=%5B%7B%22k%22%3A%22%E6%9D%AD%E5%B7%9E%E5%90%89%E7%A5%A5%E9%87%8C%22%2C%22c%22%3A5%7D%2C%7B%22k%22%3A%22%E6%9D%AD%E5%B7%9E%E5%90%89%E7%A5%A5%E9%87%8C%E5%86%B7%E6%B8%85%22%2C%22c%22%3A1%7D%2C%7B%22k%22%3A%22%E5%A4%96%E6%8B%8D%E6%B4%BB%E5%8A%A8%22%2C%22c%22%3A1%7D%2C%7B%22k%22%3A%22%E4%BA%BA%E6%96%87%E7%89%87%22%2C%22c%22%3A1%7D%5D; Hm_lpvt_5185a335802fb72073721d2bb161cd94=1745635710",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
}
data = []

for i in range(1, 100):
    response = requests.get(url + str(i), headers=headers)
    html = response.text

    # 解析HTML
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find("ul", class_="detailtz").find_all("li")

    # 提取信息
    for item in items:
        title = item.find("p", class_="title").text.strip()
        author = item.find("p", class_="author")
        date = author.find("span").text.strip()
        author = author.find("a").text.strip()
        data.append({"title": title, "author": author, "date": date})

# 数据存储
import pandas as pd

df = pd.DataFrame(data)
df.to_csv("杭州吉祥里_19楼.csv", index=False)

"""
import requests
from bs4 import BeautifulSoup

def get_notes():
    url = ""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 使用CSS选择器找到笔记内容的元素
    notes = soup.select(".note-content")

    # 打印并返回笔记内容
    for note in notes:
        print(note.text)
    return notes

def save_notes(notes):
    with open("notes.txt", "w", encoding="utf-8") as file:
        for note in notes:
            file.write(note.text + "\n")

notes = get_notes()
save_notes(notes)
"""

"""
import requests

url = "https://www.xiaohongshu.com/search_result?keyword=%25E6%25A1%25A5%25E8%25A5%25BF%25E5%258E%2586%25E5%258F%25B2%25E8%25A1%2597%25E5%258C%25BA&source=web_explore_feed"  # 将xxxx替换为原贴的ID或URL
response = requests.get(url)

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

# 提取标题
title = soup.find("h1", class_="title").text

# 提取内容
content = soup.find("div", class_="content").text

# 提取作者
author = soup.find("span", class_="author-name").text

# 提取发布时间
time = soup.find("span", class_="time").text

filename = "original_post.txt"

with open(filename, "w", encoding="utf-8") as file:
    file.write(f"标题：{title}\n")
    file.write(f"作者：{author}\n")
    file.write(f"发布时间：{time}\n")
    file.write("\n")
    file.write(content)
"""
