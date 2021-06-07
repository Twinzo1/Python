# -*- coding: utf-8 -*-
"""
@Time ： 2021/6/3 0:34
@Auth ： Twinzo1
@File ：jd_cart.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import requests
import json
from requests_toolbelt.utils import dump


def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


cookie_str = ""
headers = {
    "referer": "https://cart.jd.com/cart_index/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/78.0.3904.116 Safari/537.36",

}

cookie = str2dict(cookie_str)


def getCurrentCart():
    url = "https://api.m.jd.com/api?functionId=pcCart_jc_getCurrentCart&appid=JDC_mall_cart"
    response = requests.post(url, cookies=cookie, headers=headers)
    response.encoding = response.apparent_encoding
    CurrentCart = json.loads(response.text)
    vendors = CurrentCart['resultData']['cartInfo']['vendors']
    print(vendors[1])


def cartRemove():
    cart_will_remove = {}
    url = "https://api.m.jd.com/api"
    
    # 商品名
    Name = cart_will_remove['sorted'][0]['item']['items'][0]['item']['skuUuid']
    
    Id = cart_will_remove['sorted'][0]['item']['Id']
    Num = cart_will_remove['sorted'][0]['item']['Num']
    skuUuid = cart_will_remove['sorted'][0]['item']['items'][0]['item']['skuUuid']
    useUuid = cart_will_remove['sorted'][0]['item']['items'][0]['item']['useUuid']

    body_content = {"operations": [{"TheSkus": [{"Id": Id, "num": Num, "skuUuid": skuUuid, "useUuid": useUuid}]}]}
    formData = {
        "functionId": "pcCart_jc_cartRemove",
        "appid": "JDC_mall_cart",
        'body': json.dumps(body_content)
    }

    headers = {
        "referer": "https://cart.jd.com/cart_index/",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/78.0.3904.116 Safari/537.36",
    }
    print(formData)
    response = requests.post(url, cookies=cookie, headers=headers, data=formData)
    response.encoding = response.apparent_encoding

    data = dump.dump_all(response)
    print(data.decode('utf-8'))
    print(response.text)


cartRemove()
