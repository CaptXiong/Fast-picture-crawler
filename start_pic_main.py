# -*- coding: utf-8',
import datetime
import asyncio
import os
from pic_360 import get_360_pic
from pic_bing import get_bing_pic
from pic_sogou import get_sogou_pic
from pic_google_pp import normal_login as google_main
from pic_baidu import normal_login as baidu_main
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multi_download import main as download_main


def pp_main(task_count, keyword, data_path):
    """cookie登录主流程"""
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"开始时间为: 《{start_time}》")
    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(4)
    loop.set_default_executor(executor)
    # 设置并发数量
    semaphore = asyncio.Semaphore(task_count)
    task1 = [asyncio.ensure_future(baidu_main(semaphore=semaphore, keyword=keyword, data_path=data_path))]
    task2 = [asyncio.ensure_future(google_main(semaphore=semaphore, keyword=keyword, data_path=data_path))]
    tasks = task1 + task2
    loop.run_until_complete(asyncio.wait(tasks))
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"结束时间为：《{end_time}》")


def start_main(keyword, data_path):
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.submit(get_sogou_pic, keyword, data_path)
        executor.submit(get_bing_pic, keyword, data_path)
        executor.submit(get_360_pic, keyword, data_path)


if __name__ == '__main__':
    keyword_list = ['高速公路裂缝','高速公路落石','高速公路滑坡','高速公路泥石流']  # '公交车车祸','汽车车祸','客车车祸','轿车车祸','货车车祸','卡车车祸','自行车车祸','摩托车车祸','高速公路车祸','追尾','交通事故','隧道烟雾','公交车起火','汽车起火','客车起火','轿车起火','货车起火','卡车起火','自行车起火','摩托车起火','路面积水','路面结冰','路面积雪','路面大雾','路面坑槽','路面裂缝','路面落石','路面滑坡','路面泥石流','高速公路积水','高速公路结冰','高速公路积雪','高速公路大雾','高速公路坑槽',
    # keyword_list = ['路面破损']
    data_path = r"D:/车祸图片/新关键词2/"
    for keyword in keyword_list:
        pp_main(1, keyword, data_path)
        start_main(keyword, data_path)
        # 开始下载图片
        download_main(data_path, keyword)