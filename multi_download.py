import json
import requests
import os, datetime
import math, time, random
from multiprocessing import Pool, Process
from copyheaders import headers_raw_to_dict


to_headers = b"""
    user-agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36
    """
headers = headers_raw_to_dict(to_headers)

def get_url_set(dir_path):
    image_set = set()
    file_name_list = os.listdir(dir_path)
    for file_name in file_name_list:
        # if file_name.split('_')[-1].replace(".txt", "").strip() in keyword_list:
        #     print('@@@', file_name)
        image_str = []
        with open(dir_path+file_name, "r", encoding='utf-8') as f:
            for line in f:
                image_str.append(line)
        image_dict = json.loads(image_str[0])
        image_list = image_dict.get("图片链接列表")
        # print('$$$', len(image_list))
        image_set = image_set | set(image_list)
        print(len(image_set), file_name)
    print("已获取所有下载链接")
    return image_set


def single_download(file_path, image_url):

    with open(file_path, 'wb') as handle:
        response = requests.get(url=image_url, headers=headers, timeout=(8, 8))
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)


def download(dir_path, image_set, pid_num, keyword):
    num = 1
    undownload_set = set()
    if not os.path.exists(dir_path + "pic"):
        os.mkdir(dir_path + "pic")
    for image_url in image_set:
        try:
            print(f'开始第{num}张图片下载,共有{len(image_set)}, 进程编号:{pid_num}')
            file_path = dir_path + f"pic/{keyword}_{pid_num}_{num}.jpg"
            single_download(file_path, image_url)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            undownload_set.add(image_url)
            print(e, '未爬取集合个数：',len(undownload_set))
        finally:
            num += 1
    while undownload_set:
        print(f'开始补完计划，第{num}张图片下载,共有{len(undownload_set)}, 进程编号:{pid_num}')
        image_url = undownload_set.pop()
        try:
            file_path = dir_path + f"pic/{keyword}_{pid_num}_{num}.jpg"
            single_download(file_path, image_url)
            time.sleep(random.uniform(0.8, 1.1))
        except Exception as e:
            print(e)
        finally:
            num += 1


def list_split(items, n):
    total_num = len(items)
    result = []
    for time, i in enumerate(range(0, total_num, math.floor(total_num/n))):
        if time == n-1:
            result.append(items[i:total_num])
            return result
        else:
            result.append(items[i:i + math.floor(total_num / n)])


def multi_start(dir_path, image_set, keyword):
    pool_num = 4
    p = Pool(pool_num)
    image_list = list(image_set)
    total_list = list_split(image_list, pool_num)
    for i in range(pool_num):
        print('multi:', len(total_list[i]))
        p.apply_async(func=download, args=(dir_path, set(total_list[i]), i, keyword,))
    p.close()
    p.join()
    print('end', datetime.datetime.now())


def main(data_path, keyword):
    try:
        path = data_path + keyword + "/"
        if not os.path.exists(path):
            raise ValueError("没有读取到关键词目录")
        total_set = get_url_set(path)
        multi_start(path, total_set, keyword)
        print(path, '$$$')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    data_path = r"D:/"

    main(data_path, keyword="jojo")


