import re
import time
import random
import requests
import datetime

from redis import StrictRedis


redis_conn = StrictRedis(host="114.116.244.131",
                         port=8379,
                         db=0,
                         password="yuanbao@2019")


def is_ipv4(address):
    ipv4_regex = re.compile(
        r"^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\."
        r"(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\:([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])$" ,
        re.IGNORECASE)
    return True if ipv4_regex.match(address) else False


def get_proxies_mongodb():
    print("开始获取新Ip", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    web_datas = requests.get("http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=b7920f5c96014fd78071"
                             "182c26c2f3ec&count=5&expiryDate=0&format=2&newLine=2").text
    ip_list = web_datas.split("\r\n")
    for ip in ip_list:
        if is_ipv4(ip):
            ip = f"http://{ip}"
            if judge_proxies(ip):
                redis_conn.sadd("proxies", str(ip))


def judge_proxies(proxies):
    url = "http://www.baidu.com"
    proxies_dict = {'http': proxies}
    try:
        response = requests.get(url, proxies=proxies_dict, timeout=2)
    except Exception as e:
        print("验证超时，删除无用IP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        delete_proxies_ip(proxies)
        return False
    else:
        code = response.status_code
        if 200 <= code < 300:
            print("IP验证成功", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return proxies
        else:
            print(f"response状态码为{code}, 删除无用IP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            delete_proxies_ip(proxies)
            return False


def judge_qichacha_proxies(proxies):
    url = "https://www.qcc.com/firm_9cce0780ab7644008b73bc2120479d31.html"
    headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.qcc.com',
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36',
        }
    proxies_dict = {'https': proxies.replace("http", 'https')}
    try:
        response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=5)
    except Exception as e:
        print("企查查验证超时，删除无用IP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        delete_qichacha_ip(proxies)
        return False
    else:
        code = response.status_code
        if 200 <= code < 300:
            if re.search("010-60606666", response.text):
                print("企查查IP验证成功", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                return proxies
            else:
                print(f"获取电话拾事变，删除无用IP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                delete_qichacha_ip(proxies)
                return False
        else:
            print(f"企查查response状态码为{code}, 删除无用IP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            delete_qichacha_ip(proxies)
            return False


def delete_proxies_ip(ip):
    redis_conn.srem('proxies', ip)
    print("删除成功")
    return True


def delete_qichacha_ip(ip):
    redis_conn.srem('proxies_qichacha', ip)
    print("企查查代理删除成功", ip)
    return True


def get_proxies_out(proxies='proxies'):
    for i in range(10):
        try:
            ips = list(redis_conn.smembers(proxies))
            ip = random.choice(ips)
            ip = {"https": ip.decode()}
            # print(ip)
            return ip
        except:
            continue


def update_proxies_ip_pool():
    print("检验通用ip有效性", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ip_list = list(redis_conn.smembers('proxies'))
    print(len(ip_list))
    for ip in ip_list:
        try:
            ip = ip.decode()
            # print(str(ip))
            judge_proxies(str(ip))
        except Exception as e:
            print(e)


def update_qichacha_ip_pool():
    print("检验企查查ip有效性", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ip_list = list(redis_conn.smembers('proxies_qichacha'))
    print(len(ip_list))
    for ip in ip_list:
        try:
            ip = ip.decode()
            # print(str(ip))
            judge_qichacha_proxies(str(ip))
        except Exception as e:
            print(e)


def proxies_to_qichacha_pool():
    print("导入有效企查查ip", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ip_list = list(redis_conn.smembers('proxies'))
    print(len(ip_list))
    for ip in ip_list:
        try:
            ip = ip.decode()
            # print(str(ip))
            if judge_qichacha_proxies(str(ip)):
                redis_conn.sadd("proxies_qichacha", str(ip))
        except Exception as e:
            print(e)


def get_vps_proxy(redis_key, vps_server_name):
    proxy_str = redis_conn.hget(redis_key, vps_server_name)
    proxy_ip = proxy_str.decode()
    proxy_ip = {"http": proxy_ip}
    print("vps代理ip为:", proxy_ip)
    return proxy_ip


def get_https_proxy(redis_key, vps_server_name):
    proxy_str = redis_conn.hget(redis_key, vps_server_name)
    proxy_ip = proxy_str.decode()
    proxy_ip = {"https": proxy_ip.replace("http", "https")}
    print("https代理ip为:", proxy_ip)
    return proxy_ip


if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    # 每隔两分钟执行一次 job_func 方法
    scheduler.add_job(get_proxies_mongodb, 'interval', seconds=10)
    scheduler.add_job(update_qichacha_ip_pool, 'interval', seconds=5)
    scheduler.add_job(update_proxies_ip_pool, 'interval', seconds=5)
    scheduler.add_job(proxies_to_qichacha_pool, 'interval', seconds=5)
    # 在 2017-12-13 14:00:01 ~ 2017-12-13 14:00:10 之间, 每隔两分钟执行一次 job_func 方法
    # scheduler.add_job(job_func, 'interval', minutes=2, start_date='2017-12-13 14:00:01', end_date='2017-12-13 14:00:10')

    scheduler.start()

    while 1:
        time.sleep(10)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # get_vps_proxy("vps_proxy", "vps_1")

