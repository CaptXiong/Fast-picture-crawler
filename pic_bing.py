import requests
import time,datetime
import json
import random
import re, os
import traceback
from urllib.parse import unquote
from lxml import etree
from copyheaders import headers_raw_to_dict


def get_bing_pic(keyword, data_path):
    data_path = data_path + keyword + "/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    pic_url_set = set()
    to_headers = b"""
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9

    accept-language: zh-CN,zh;q=0.9,en;q=0.8
    cache-control: max-age=0
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36
    """
    headers = headers_raw_to_dict(to_headers)
    first_url = f"https://cn.bing.com/images/search?q={keyword}"
    try:
        response = requests.get(first_url, headers=headers, verify=False, timeout=(5, 5))
        first_webdata = response.content
        first_webdata = str(first_webdata.strip(), encoding="utf-8")
        first_datas = etree.HTML(first_webdata)
        xpath_datas = first_datas.xpath("//a[@class='iusc']/@href")
        for data in xpath_datas:
            img_url = "https://cn.bing.com" + data
            pic_url_set.add(img_url)
        # print('首页', pic_url_list)
    except Exception as e:
        print(e, traceback.print_exc())

    url_list = [f"https://cn.bing.com/images/async?q={keyword}&first={int(38 + (i - 1) * 35)}&count=35&relp=35&cw=1119&ch=920&scenario=ImageBasicHover&datsrc=I&layout=RowBased_Landscape&mmasync=1&dgState=x*828_y*1350_h*181_c*3_i*211_r*49&IG=759CCA8CB46F4CB5B5EF345AB570E81A&SFX={i}&iid=images.5523" for i in range(1, 42)]
    medium_url = [f"https://cn.bing.com/images/async?q={keyword}&first={int(38 + (i - 1) * 35)}&count=35&relp=35&qft=+filterui%3aimagesize-medium&cw=1119&ch=920&scenario=ImageBasicHover&datsrc=I&layout=RowBased_Landscape&mmasync=1&dgState=x*828_y*1350_h*181_c*3_i*211_r*49&IG=759CCA8CB46F4CB5B5EF345AB570E81A&SFX={i}&iid=images.5523" for i in range(1, 42)]
    large_url = [f"https://cn.bing.com/images/async?q={keyword}&first={int(38 + (i - 1) * 35)}&count=35&relp=35&qft=+filterui%3aimagesize-large&cw=1119&ch=920&scenario=ImageBasicHover&datsrc=I&layout=RowBased_Landscape&mmasync=1&dgState=x*828_y*1350_h*181_c*3_i*211_r*49&IG=759CCA8CB46F4CB5B5EF345AB570E81A&SFX={i}&iid=images.5523" for i in range(1, 42)]
    url_list = url_list + medium_url + large_url
    undownload_url_set = set()
    number = 1
    for url in url_list:
        print(f'第{number}个网址必应爬取, 共有{len(pic_url_set)}张图,{datetime.datetime.now()}')
        try:
            web_data = requests.get(url, headers=headers, verify=False, timeout=(5, 5)).text
        except Exception as e:
            print(e, '访问出错')
            undownload_url_set.add(url)
        datas = etree.HTML(web_data)
        xpath_datas = datas.xpath("//a[@class='iusc']/@href")
        for pic_url in xpath_datas:
            img_url = "https://cn.bing.com" + pic_url
            pic_url_set.add(img_url)
        time.sleep(random.randint(5, 10) / 10)
        pic_url_list = [unquote(re.findall('mediaurl=(\S+)&exph', i)[0]) for i in pic_url_set]
        # print(pic_url_list)
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_list), "图片链接列表": pic_url_list}
        with open(data_path + f"pic_bing_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
        number += 1
    while undownload_url_set:
        print(f'开始补完计划，第{number}个网址必应爬取, 共有{len(pic_url_set)}张图,{datetime.datetime.now()}')
        try:
            url = undownload_url_set.pop()
            web_data = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=(5, 5)).text
        except Exception as e:
            print(e, '访问出错')
        datas = etree.HTML(web_data)
        xpath_datas = datas.xpath("//a[@class='iusc']/@href")
        for pic_url in xpath_datas:
            img_url = "https://cn.bing.com" + pic_url
            pic_url_set.add(img_url)
        time.sleep(random.randint(5, 10) / 10)
        pic_url_list = [unquote(re.findall('mediaurl=(\S+)&exph', i)[0]) for i in pic_url_set]
        # print(pic_url_list)
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_list), "图片链接列表": pic_url_list}
        with open(data_path + f"pic_bing_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
        number += 1


def down_load(dir_path, keyword):
    image_str = []
    with open(f"pic_bing_{keyword}.txt", "r", encoding='utf-8') as f:
        for line in f:
            image_str.append(line)
    image_dict = json.loads(image_str[0])
    image_list = image_dict.get("图片链接列表")
    num = 1
    for image_url in image_list:
        print(f'开始第{num}张图片下载')
        file_path = dir_path + f"/bing_{num}.jpg"
        with open(file_path, 'wb') as handle:
            response = requests.get(url=image_url, timeout=(5, 5))
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        num += 1


if __name__ == '__main__':
    keyword = "jojo"
    keyword_list = ["jojo"]
    dir_path = r"D:/"
    for keyword in keyword_list:
        print(keyword)
        get_bing_pic(keyword, dir_path)
    # down_load(dir_path, keyword)
