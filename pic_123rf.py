import requests
import json, os
import time,datetime
import random
from lxml import html, etree
import multi_download


def get_pic(keyword):
    """本网站仅限英文关键词查询"""
    pic_url_set = set()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/51.0.2704.103 Safari/537.36",
               "content-type": "text/html; charset=utf-8",
               }
    first_url = f"https://www.123rf.com/stock-photo/{'_'.join(keyword.split(' '))}.html?oriSearch=" \
                f"{'+'.join(keyword.split(' '))}&sti=%7Cnbj2ejxvp09bhvvozs&imgtype=1"
    print(first_url)
    # 开始爬取后面的页面
    re = requests.get(first_url, headers=headers)
    datas = etree.HTML(re.text)
    total_page = datas.xpath("//span[@class='padding-mini horizontal-right']//text()")
    if total_page:
        total_page = int(total_page[0].strip())
    first_img_list = datas.xpath("//div[@id='main_container_mosaic']/div/a/div/img/@src")
    for img_url in first_img_list:
        pic_url_set.add(img_url)
    print(f"开始访问关键词为{keyword}的123rf页面,共有{total_page}页")
    for i in range(2, total_page+1):
        try:
            print(f"第{i}页,累计有{len(pic_url_set)}张图,共有{total_page}页")
            url = f"https://www.123rf.com/stock-photo/{'_'.join(keyword.split(' '))}.html?oriSearch=" \
                f"{'+'.join(keyword.split(' '))}&start={i*110}&sti=%7Cnbj2ejxvp09bhvvozs&imgtype=1"
            web_data = requests.get(url, headers=headers, timeout=(10, 15))
            if web_data.status_code == 200:
                datas = etree.HTML(web_data.text)
                img_list = datas.xpath("//div[@id='main_container_mosaic']/div/a/div/img/@src")
                for img_url in img_list:
                    pic_url_set.add(img_url)
                # print(len(pic_url_set), pic_url_set)
            else:
                print(f"返回状态异常：{web_data.status_code}")
        except Exception as e:
            print(e)
        time.sleep(random.randint(3, 10)/10)
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_set), "图片链接列表": list(pic_url_set)}
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        with open(data_path+f"pic_123rf2_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
    print(f"图片保存完毕，共{len(pic_url_set)}张，{datetime.datetime.now()}")


if __name__ == '__main__':
    data_path = r"D:/"
    keyword_list = ["traffic crashes"]
    # for i in keyword_list:
    #     get_pic(i)
    multi_download.main(data_path)

