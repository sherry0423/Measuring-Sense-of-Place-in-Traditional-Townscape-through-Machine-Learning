import re
import time
import requests
import execjs
import json
import csv


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "dnt": "1",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie": "abRequestId=fc6c8276-8255-5cc5-8382-4a654352a744; a1=19642891d2ez67x1ptocitni9l3sox7zv5i7k2y8i50000369810; webId=3e17e947508f0c77bc54915b6abb2853; gid=yjK4JYjJ0KhKyjK4JYjyf2JvJduKWCyU9lS33Y39I3j1qW28MlCWuT888qKjYy88DiSfYJd4; web_session=0400698c49c609184443690f3e3a4b57d54684; xsecappid=xhs-pc-web; webBuild=4.67.0; acw_tc=0a4a6be217489590679777768edc9375d51e844e2753b4310182f667f5d465; websectiga=9730ffafd96f2d09dc024760e253af6ab1feb0002827740b95a255ddf6847fc8; sec_poison_id=3a7ddcde-a9fd-4e9e-a836-73fde78917c9; unread={%22ub%22:%22683dbb7c0000000022028b26%22%2C%22ue%22:%22683da11d0000000023010e75%22%2C%22uc%22:25}; loadts=1748959102617}",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

xhs_sign_obj = execjs.compile(open('xhs.js', encoding='utf-8').read())

note_count = 0

# 向csv文件写入表头  笔记数据csv文件
header = ["笔记标题", "笔记链接", "用户ID", "用户名", "头像链接", "IP属地", "笔记发布时间",
          "笔记收藏数量", "笔记评论数量", "笔记点赞数量", "笔记转发数量", "笔记内容"]


f = open(f"曹杨新村.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.DictWriter(f, header)
writer.writeheader()


# 时间戳转换成日期
def get_time(ctime):
    timeArray = time.localtime(int(ctime / 1000))
    otherStyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherStyleTime)


# 保存笔记数据
def sava_data(note_data, note_id, xsec_token):
    try:
        ip_location = note_data['note_card']['ip_location']
    except:
        ip_location = '未知'

    data_dict = {
        "笔记标题": note_data['note_card']['title'].strip(),
        "笔记链接": "https://www.xiaohongshu.com/explore/" + note_id + f"?xsec_token={xsec_token}&xsec_source=pc_feed",
        "用户ID": note_data['note_card']['user']['user_id'].strip(),
        "用户名": note_data['note_card']['user']['nickname'].strip(),
        "头像链接": note_data['note_card']['user']['avatar'].strip(),
        "IP属地": ip_location,
        "笔记发布时间": get_time(note_data['note_card']['time']),
        "笔记收藏数量": note_data['note_card']['interact_info']['collected_count'],
        "笔记评论数量": note_data['note_card']['interact_info']['comment_count'],
        "笔记点赞数量": note_data['note_card']['interact_info']['liked_count'],
        "笔记转发数量": note_data['note_card']['interact_info']['share_count'],
        "笔记内容": note_data['note_card']['desc'].strip().replace('\n', '')
    }

    # 笔记数量+1
    global note_count
    note_count += 1

    print(f"当前笔记数量: {note_count}\n",
          f"笔记标题：{data_dict['笔记标题']}\n",
          f"笔记链接：{data_dict['笔记链接']}\n",
          f"用户ID：{data_dict['用户ID']}\n",
          f"用户名：{data_dict['用户名']}\n",
          f"头像链接：{data_dict['头像链接']}\n",
          f"IP属地：{data_dict['IP属地']}\n",
          f"笔记发布时间：{data_dict['笔记发布时间']}\n",
          f"笔记收藏数量：{data_dict['笔记收藏数量']}\n",
          f"笔记评论数量：{data_dict['笔记评论数量']}\n",
          f"笔记点赞数量：{data_dict['笔记点赞数量']}\n",
          f"笔记转发数量：{data_dict['笔记转发数量']}\n",
          f"笔记内容：{data_dict['笔记内容']}\n"
          )
    writer.writerow(data_dict)


def get_note_info(note_id, xsec_token):
    note_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'

    data = {
        "source_note_id": note_id,
        "image_scenes": ["jpg", "webp", "avif"],
        "extra": {"need_body_topic": "1"},
        "xsec_token": xsec_token,
        "xsec_source": "pc_search"

    }

    sign_header = xhs_sign_obj.call('sign', '/api/sns/web/v1/feed', data, headers.get('cookie', ''))
    headers.update(sign_header)

    data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    response = requests.post(note_url, headers=headers, data=data.encode('utf-8'))
    json_data = response.json()

    try:
        note_data = json_data['data']['items'][0]
    except:
        print(f'笔记 {note_id} 不允许查看')
        return
    sava_data(note_data, note_id, xsec_token)


def keyword_search(keyword):
    api = '/api/sns/web/v1/search/notes'
    search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    page_count = 20  # 爬取的页数, 一页有 20 条笔记 最多只能爬取220条笔记
    for page in range(1, page_count):
        # 排序方式 general: 综合排序 popularity_descending: 热门排序 time_descending: 最新排序
        params = {
            "ext_flags": [],
            "image_formats": ["jpg", "webp", "avif"],
            "keyword": keyword,
            "note_type": 0,
            "page": page,
            "page_size": 20,
            'search_id': xhs_sign_obj.call('searchId'),
            "sort": "general"
        }

        sign_header = xhs_sign_obj.call('sign', api, params, headers.get('cookie', ''))
        headers.update(sign_header)

        data = json.dumps(params, separators=(',', ':'), ensure_ascii=False)

        response = requests.post(search_url, headers=headers, data=data.encode('utf-8'))

        json_data = response.json()

        try:
            notes = json_data['data']['items']
        except:
            print('================爬取完毕================'.format(page))
            break

        for note in notes:
            note_id = note['id']
            xsec_token = note['xsec_token']
            if len(note_id) != 24:
                continue

            get_note_info(note_id, xsec_token)


def main():
    keyword = '曹杨新村体验'  # 搜索的关键词



    keyword_search(keyword)


if __name__ == "__main__":
    main()





