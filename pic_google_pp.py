import time
import asyncio
import random
import json
import datetime
import re, os, traceback
import sys
import requests
from urllib.parse import unquote
from pyppeteer import launch


js1 = '''() =>{
           Object.defineProperties(navigator,{
             webdriver:{
               get: () => false
             }
           })
        }'''

js2 = '''() => {
        alert (
            window.navigator.webdriver
        )
    }'''

js3 = '''() => {
        window.navigator.chrome = {
    runtime: {},
    // etc.
  };
    }'''

js4 = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
        }'''

js5 = '''() =>{
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5,6],
  });
        }'''


async def create_semaphore(task_count):
    semaphore = asyncio.Semaphore(task_count)
    return semaphore


async def create_page(semaphore):
    page = None
    async with semaphore:
        browser = await launch(headless=True,
                               dumpio=True,
                               args=[
                                   # 最大化窗口
                                   "--start-maximized",
                                   # 取消沙盒模式 沙盒模式下权限太小
                                   "--no-sandbox",
                                   # 不显示信息栏  比如 chrome正在受到自动测试软件的控制 ...
                                   "--disable-infobars",
                                   # "--proxy-server=47.52.61.227:8888",
                                   # '--proxy-server={}'.format(proxy_ip),
                                   # log等级设置 在某些不是那么完整的系统里 如果使用默认的日志等级 可能会出现一大堆的warning信息
                                   "--log-level=3",
                                   # 设置UA
                                   "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                   "like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                               ],
                               # 用户数据保存目录 这个最好也自己指定一个目录
                               # 如果不指定的话，chrome会自动新建一个临时目录使用，在浏览器退出的时候会自动删除临时目录
                               # 在删除的时候可能会删除失败（不知道为什么会出现权限问题，我用的windows） 导致浏览器退出失败
                               # 然后chrome进程就会一直没有退出 CPU就会狂飙到99%
                               userDataDir=r'D:\test',
                               # executablePath=r'/opt/google/chrome/google-chrome',
                               # executablePath=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                               )
        try:
            # 使用无痕模式登陆
            browser_context = await browser.createIncognitoBrowserContext()
            page = await browser_context.newPage()
            # page = await browser.newPage()
            width, height = 1920, 1080
            await page.setViewport({
                'width': width,
                'height': height,
            })
            await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                             '{ webdriver:{ get: () => false } }) }')
            await page.evaluate(js1)
            await page.evaluate(js3)
            await page.evaluate(js4)
            await page.evaluate(js5)
        except Exception as e:
            print(e)
        return browser, page


async def request_url(page, url):
    """请求url"""
    try:
        await page.goto(url, timeout=20000, waitUntil='domcontentloaded')
        await asyncio.sleep(0.5)
    except Exception as e:
        print(e)
    finally:
        return page


async def click_right(page):
    try:
        ele = await page.xpath(f'//a[@class="wXeWr islib nfEiy mM5pbd"]')
        for i in ele:
            await i.click(options={
                'button': 'right',
                'clickCount': 1,  # 1 or 2
                # 'delay': 300,  # 毫秒
            })
        # await asyncio.sleep(0.1)
    except Exception as e:
        print(e)
    finally:
        return page

async def save_pics(page, keyword, data_path):
    print(f"开始保存图片地址")
    try:
        pic_url_list = []
        pic_element = await page.xpath("//a[@class='wXeWr islib nfEiy mM5pbd']")
        for i in pic_element:
            url_str = await (await i.getProperty('href')).jsonValue()
            # print(url_str)
            if 'imgurl=' in url_str and url_str not in pic_url_list:
                url_str = re.findall("imgurl=(\S+)&imgrefurl", url_str)[0]
                url_str = unquote(url_str)
                pic_url_list.append(url_str)
        print('&&&', len(pic_url_list), pic_url_list[1])
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_list), "图片链接列表": pic_url_list}
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        with open(data_path+f"pic_google_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
    except Exception as e:
        print(e)
    finally:
        return page


async def normal_login(semaphore, keyword, data_path):
    """正常登录流程"""
    data_path = data_path + keyword + "/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    browser, page = await create_page(semaphore)
    try:
        login_url = f"https://www.google.com/search?&tbm=isch&q={keyword}"
        print(f"开始访问关键词首页{keyword}")
        page = await request_url(page, login_url)
        for i in range(60):  # 下拉次数  10次300张图  15次左右遇到 //input[@value='显示更多搜索结果']
            await page.evaluate('_ => {window.scrollBy(0, window.innerHeight);}')
            await asyncio.sleep(2)
            next_element = await page.xpath("//div[@jsname='i3y3Ic']")
            if next_element:
                signal_str = await (await next_element[0].getProperty("style")).jsonValue()
                signal_str = str(signal_str)
                if "display" in signal_str:
                    print("继续下拉", i)
                else:
                    print("点击显示更多", signal_str)
                    await page.hover("input[type='button']")
                    await asyncio.sleep(0.5)
                    await page.click("input[type='button']")
                    await asyncio.sleep(5)

        page = await click_right(page)
        page = await save_pics(page, keyword, data_path)
        print(f"{keyword}图片保存结束，{datetime.datetime.now()}")

    except Exception as e:
        # print(e)
        traceback.print_exc(e)
    finally:
        await browser.close()


def main(task_count, keyword, data_path):
    """cookie登录主流程"""
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"开始时间为: 《{start_time}》")
    loop = asyncio.get_event_loop()
    # 设置并发数量
    semaphore = asyncio.Semaphore(task_count)
    tasks = [asyncio.ensure_future(normal_login(semaphore=semaphore, keyword=keyword, data_path=data_path))]
    loop.run_until_complete(asyncio.wait(tasks))
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"结束时间为：《{end_time}》")


if __name__ == '__main__':
    # 设置并发数量
    keyword = ["jojo"]
    task_count = 1
    # loop = asyncio.get_event_loop()
    data_path = f"D:/"
    for i in keyword:
        main(task_count, i, data_path)
        # down_load(dir_path, i)



