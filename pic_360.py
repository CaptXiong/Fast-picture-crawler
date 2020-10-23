import requests
import json
import time
import random, traceback
import os
from lxml import etree
from copyheaders import headers_raw_to_dict


def get_360_pic(keyword, data_path):
    data_path = data_path + keyword + "/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    to_headers = b"""
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36
        """
    headers = headers_raw_to_dict(to_headers)
    pic_url_set = set()
    first_url_list = [f"http://image.so.com/i?q={keyword}&src=srp&zoom={zoom_type}" for zoom_type in range(1, 4)]
    white_url_list = [url + "&color=white" for url in first_url_list]
    black_url_list = [url + "&color=black" for url in first_url_list]
    first_url_list = first_url_list + white_url_list + black_url_list
    try:
        for first_url in first_url_list:
            # print(proxies)
            first_webdata = requests.get(first_url, headers=headers, proxies=proxies).text
            first_datas = etree.HTML(first_webdata)
            xpath_datas = json.loads(first_datas.xpath("//script[@id='initData']/text()")[0])
            for data in xpath_datas["list"]:
                pic_url_set.add(data["img"])
            time.sleep(random.randint(5, 10) / 10)
    except Exception as e:
        print(e)
    for i in range(1, 80):
        print(f"第{i}页,有{len(pic_url_set)}张图")
        # url_list = [f"http://image.so.com/j?q={keyword}&src=srp=srp&correct={keyword}&pn=60" \
        #       f"&ch=&sn={50+60*i}&ran=0&ras=6&cn=0&gn=0&kn=50"]
        url_list = [f"https://image.so.com/j?q={keyword}&pd=1&pn=60&correct={keyword}" \
              f"&adstar=0&tab=all&sid=2e488cafefd0f95cc08342c9a979c788&ras=0&cn=0&gn=0&kn=50&crn=0&bxn=0&cuben=0&src=srp&zoom={zoom_type}&sn={50+60*i}&pn=60" for zoom_type in range(1, 4)]
        white_url = [f"https://image.so.com/j?q={keyword}&pd=1&pn=60&correct={keyword}" \
              f"&adstar=0&tab=all&sid=2e488cafefd0f95cc08342c9a979c788&ras=0&cn=0&gn=0&kn=50&crn=0&bxn=0&cuben=0&src=srp&zoom={zoom_type}&color=white&sn={50+60*i}&pn=60" for zoom_type in range(1, 4)]
        black_url = [f"https://image.so.com/j?q={keyword}&pd=1&pn=60&correct={keyword}" \
                     f"&adstar=0&tab=all&sid=2e488cafefd0f95cc08342c9a979c788&ras=0&cn=0&gn=0&kn=50&crn=0&bxn=0&cuben=0&src=srp&zoom={zoom_type}&color=black_url&sn={50 + 60 * i}&pn=60" for zoom_type in range(1, 4)]
        url_list = url_list + white_url +black_url
        def url_process(url, proxies):
            url_set = set()
            web_data = requests.get(url, headers=headers).text
            if "您的电脑或所在局域网络对本站有异常访问" in web_data:
                raise InterruptedError("访问异常")
            datas = json.loads(web_data)
            for data in datas["list"]:
                url_set.add(data["img"])
            return url_set
        for url in url_list:
            try:
                pic_url_set = pic_url_set | url_process(url)
            except InterruptedError:
                print("您的电脑或所在局域网络对本站有异常访问")

                pic_url_set = pic_url_set | url_process(url)
            except TimeoutError:
                print('换代理ip')
                pic_url_set = pic_url_set | url_process(url)
            except Exception as e:
                traceback.print_exc()
            time.sleep(random.randint(20, 25)/10)
            pic_dict = {"关键词": keyword, "图片数量": len(pic_url_set), "图片链接列表": list(pic_url_set)}
            with open(data_path+f"pic_360_{keyword}.txt", "w", encoding='utf-8') as f:
                f.write(json.dumps(pic_dict, ensure_ascii=False))


if __name__ == "__main__":
    keyword = "jojo"
    data_path = r"D:/"
    keyword_list = ["jojo"]
    for keyword in keyword_list:
        print(keyword)
        get_360_pic(keyword, data_path)
