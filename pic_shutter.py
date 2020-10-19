import requests
import json, os
import time,datetime
import random
from lxml import html, etree
import multi_download


def get_pic(keyword):
    pic_url_set = set()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/51.0.2704.103 Safari/537.36",
               "content-type": "text/html; charset=utf-8",
               }
    first_url = f"https://www.shutterstock.com/search/{keyword}?image_type=photo"

    re = requests.get(first_url, headers=headers)
    datas = etree.HTML(re.text)
    total_page = datas.xpath("//div[@class='b_aE_c6506']//text()")
    if total_page:
        total_page = int(total_page[0].replace("of", "").replace(",", "").strip())
    first_img_list = datas.xpath("//div[@id='content']//div[contains(@class,'z_g_63ded')]//a/@href")
    for i in first_img_list:
        new_i = i.replace(i.split("-")[-2], "260nw")
        img_url = "https://image.shutterstock.com" + new_i + ".jpg"
        pic_url_set.add(img_url)
    print(f"开始访问关键词为{keyword}的butter页面,共有{total_page}页")
    for i in range(3476, total_page+1):
        try:
            print(f"第{i}页,累计有{len(pic_url_set)}张图,共有{total_page}页")
            url = f"https://www.shutterstock.com/search/{keyword}?image_type=photo&page={i}"
            web_data = requests.get(url, headers=headers, timeout=(10, 15))
            if web_data.status_code == 200:
                datas = etree.HTML(web_data.text)
                # print(datas, type(datas))
                img_list = datas.xpath("//div[@id='content']//div[contains(@class,'z_g_63ded')]//a/@href")
                for i in img_list:
                    new_i = i.replace(i.split("-")[-2], "260nw")
                    img_url = "https://image.shutterstock.com" + new_i + ".jpg"
                    pic_url_set.add(img_url)
                # print(len(pic_url_set), pic_url_set)
            else:
                print(f"返回状态异常：{web_data.status_code}")
        except Exception as e:
            print(e)
        time.sleep(random.randint(1, 10)/10)
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_set), "图片链接列表": list(pic_url_set)}
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        with open(data_path+f"pic_shutter4_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
    print(f"图片保存完毕，共{len(pic_url_set)}张，{datetime.datetime.now()}")


if __name__ == '__main__':
    keyword = "jojo"
    data_path = r"D:/"
    keyword_list = ["jojo"]
    for keyword in keyword_list:
        multi_download.main(data_path, keyword)
