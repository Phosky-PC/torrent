import requests
import random
from retrying import retry
from torent.fake_user_agent import headers
from lxml import etree


# 随机选择请求头 可根据不同需求进行改写
def user_agent():
    UA = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": random.choice(headers)
    }
    return UA


# 返回解码后的 etree 对象
@retry(stop_max_attempt_number=4)
def get_etree_page(url):
    UA = user_agent()
    headers = UA
    try:
        print("parse", url)
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            return etree.HTML(response.content.decode())
    except Exception as e:
        print(e)
        return get_etree_page(url)


# 返回二进制对象
def get_binary_page(url):
    UA = user_agent()
    headers = UA
    try:
        print('Parsing', url)
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(e)
        return None


# 返回未解码的普通文本
def get_normal_page(url):
    UA = user_agent()
    headers = UA
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)
        return None
