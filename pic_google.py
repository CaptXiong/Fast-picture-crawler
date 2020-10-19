import requests
import urllib3
import chardet
import time
import random
import re
import json
from lxml import etree
from copyheaders import headers_raw_to_dict


def get_pic(keyword):
    pic_url_list = []
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             "Chrome/67.0.3396.87 Safari/537.36"}
    first_url = f"https://www.google.com/search?&tbm=isch&q={keyword}"
    # try:
    #     first_webdata = requests.get(first_url, headers=headers).text
    #     url_list = re.findall("http(\S+).jpg", first_webdata)
    #     url_list = ["http://"+i.replace("s://", "").replace("://", "")+".jpg" for i in url_list]
    #     pic_url_list += url_list
    # except Exception as e:
    #     print(e)
    for i in range(5, 6):
        try:
            url = f"https://www.google.com/search?q={keyword}&tbm=isch&ei=UUsNX9g_kbvAA-eeqJAN&start={i*20}&sa=N"
            post_data = {
                "f.req": f'''[[["HoAMBc","[null,null,[{i},null,450,1,1136,[[\\"afoGhI8s2Mo5mM\\",259,194,16875390]],[],[],null,null,null,533,104,[]],null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,[\\"{keyword}\\"]]",null,"generic"]]]''',
                "at": "ABrGKkQG7-biHRiEhI_oXQdNS6VP:1594696749986"
            }
            web_data = requests.get(url, headers=headers).text
            datas = etree.HTML(web_data)
            xpath_datas = datas.xpath("//table[@class='GpQGbf']//td/a//img/@src")
            for url in xpath_datas:

                pic_url_list.append(url)
        except Exception as e:
            print(e)
        time.sleep(random.randint(1, 10)/10)
    print(pic_url_list)
    pic_dict = {"关键词": keyword, "图片数量": len(pic_url_list), "图片链接列表": pic_url_list}
    with open(f"pic_google_{keyword}.txt", "w", encoding='utf-8') as f:
        f.write(json.dumps(pic_dict, ensure_ascii=False))


if __name__ == '__main__':
    keyword = "jojo"
    get_pic(keyword)