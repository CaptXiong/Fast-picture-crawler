import requests
import json
import time
import random
import os


def get_sogou_pic(keyword, data_path):
    data_path = data_path + keyword + "/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    pic_url_set = set()
    for i in range(1, 80):
        try:
            print(f"第{i}页,有{len(pic_url_set)}张图")
            # url = "http://pic.sogou.com/pics?query={}&policyType=1&mode=1&start={}&reqType=ajax&reqFrom=result&tn=0".format(keyword, 48*i)
            url_list = [f"https://pic.sogou.com/api/pic/searchList?tagQSign=&forbidqc=&entityid=&query={keyword}&mode={t}&st=&start={100*i}&xml_len=100" for t in range(1, 5)]
            for url in url_list:
                web_data = requests.get(url).text
                datas = json.loads(web_data)
                # print(datas)
                for data in datas["items"]:
                    pic_url_set.add(data["picUrl"])
        except Exception as e:
            print(e)
        time.sleep(random.randint(1, 10)/10)
    # print(pic_url_list)
    pic_dict = {"关键词": keyword, "图片数量": len(pic_url_set), "图片链接列表": list(pic_url_set)}
    with open(data_path+f"pic_sogou_{keyword}.txt", "w", encoding='utf-8') as f:
        f.write(json.dumps(pic_dict, ensure_ascii=False))

def down_load(dir_path, keyword_list):
    image_set = set()
    for keyword in keyword_list:
        image_str = []
        with open(dir_path+f"pic_sogou_{keyword}.txt", "r", encoding='utf-8') as f:
            for line in f:
                image_str.append(line)
        image_dict = json.loads(image_str[0])
        image_list = image_dict.get("图片链接列表")
        image_set = image_set | set(image_list)
        print(len(image_set), keyword)
    num = 1
    # print(f'开始第{num}张图片下载,共有{len(image_set)}')
    un_download_set = set()
    for image_url in image_set:
        try:
            print(f'开始第{num}张图片下载,共有{len(image_set)}')
            file_path = dir_path + f"pic/sogou_{num}.jpg"
            with open(file_path, 'wb') as handle:
                response = requests.get(url=image_url)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        except Exception as e:
            un_download_set.add(image_url)
            print(e, un_download_set)
        finally:
            num += 1

if __name__ == '__main__':
    keyword = "jojo"
    data_path = r"D:/"
    keyword_list = ["jojo"]
    for i in keyword_list:
        get_sogou_pic(i, data_path)
    # down_load(data_path, keyword_list)
