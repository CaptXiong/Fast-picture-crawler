import time
import asyncio
import random
import json
import datetime
import os
import requests

from pyppeteer import launch

"""需确保create_page中的本地地址有文件夹，翻页数量可自定义，翻页设置在normal_login下"""
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

pic_url_set = set()


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


async def login(page,keyword):
    try:
        await page.hover('#kw')
        await asyncio.sleep(0.5)
        await page.click('#kw')
        await asyncio.sleep(1)
        await page.type('#kw', keyword, {"delay": random.randint(32, 48)})
        await asyncio.sleep(0.5)
        await page.keyboard.press('Enter')
        await asyncio.sleep(2)
        return page
    except Exception as e:
        print(e)


async def filter_page(page, num):
    try:
        await page.hover("#sizeFilter")
        await asyncio.sleep(0.5)
        await page.click(f"li[val='{num}']")
        await asyncio.sleep(1)
        return page
    except Exception as e:
        print(e)


async def save_pics(page, keyword, dir_path):
    print(f"开始保存图片地址")
    try:
        pic_element = await page.xpath("//ul/li//img")
        for i in pic_element:
            url_str = await (await i.getProperty('src')).jsonValue()
            # print(url_str)
            if url_str not in pic_url_set and ".jpg" in url_str:
                pic_url_set.add(url_str)
        # print('&&&', len(pic_url_set))
        pic_dict = {"关键词": keyword, "图片数量": len(pic_url_set), "图片链接列表": list(pic_url_set)}
        # if num > 3:
        with open(dir_path+f"pic_baidu_{keyword}.txt", "w", encoding='utf-8') as f:
            f.write(json.dumps(pic_dict, ensure_ascii=False))
    except Exception as e:
        print(e)
    finally:
        return page


async def normal_login(semaphore, keyword, data_path):
    """此处设置翻页"""
    data_path = data_path + keyword + "/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    browser, page = await create_page(semaphore)
    try:
        login_url = f"https://image.baidu.com/"
        print(f"开始访问关键词首页")
        page = await request_url(page, login_url)
        page = await login(page, keyword)
        for size_num in [2, 3, 9]:
            page = await filter_page(page, size_num)
            page = await save_pics(page, keyword, data_path)
            for i in range(81):  # 翻页数设置
                await page.evaluate('_ => {window.scrollBy(0, window.innerHeight);}')
                page = await save_pics(page, keyword, data_path)
                print(f"第{i}页,有{len(pic_url_set)}张图")
                await asyncio.sleep(0.5)
    except Exception as e:
        print(e)
    finally:
        await browser.close()


def main(task_count, keyword, data_path):
    """cookie登录主流程"""
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"开始时间为: 《{start_time}》,{keyword}")
    loop = asyncio.get_event_loop()
    # 设置并发数量
    semaphore = asyncio.Semaphore(task_count)
    tasks = [asyncio.ensure_future(normal_login(semaphore=semaphore, keyword=keyword, data_path=data_path))]
    loop.run_until_complete(asyncio.wait(tasks))
    # loop.close()
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"结束时间为：《{end_time}》")


def down_load(dir_path, keyword):
    image_str = []
    with open(f"pic_baidu_{keyword}.txt", "r", encoding='utf-8') as f:
        for line in f:
            image_str.append(line)
    image_dict = json.loads(image_str[0])
    image_list = image_dict.get("图片链接列表")
    num = 1
    for image_url in image_list:
        print(f'开始第{num}张图片下载')
        file_path = dir_path + f"pic/baidu_{num}.jpg"
        with open(file_path, 'wb') as handle:
            response = requests.get(url=image_url)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        num += 1


if __name__ == '__main__':
    # 设置并发数量
    keyword = "jojo"
    keyword_list = ["jojo"]
    data_path = r"D:/"
    num = 81
    task_count = 1
    for keyword in keyword_list:
        main(task_count, keyword, data_path)
    # down_load(dir_path, keyword)


