# -*- coding: utf-8 -*-
"""
@Time ： 2021/4/20 9:45
@Auth ： Twinzo1
@File ：airconnect.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.0
@Description: 全球加速签到
"""
import requests
from pyquery import PyQuery as pq
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/78.0.3904.116 Safari/537.36',
}
url_prefix = "http://xn--15qp3au64eprx.com"


# url_prefix = "https://xn--15qp3au64eprx.com"


def login():
    url = url_prefix + "/auth/login"
    data = {
        'email': your_email,
        'passwd': your_password,
    }
    response = requests.post(url, headers=headers, data=data)
    if "登录成功" in response.text.encode().decode("unicode-escape"):
        return response
    else:
        print("登录失败")
        return


def get_cookie(res):
    cookie = requests.utils.dict_from_cookiejar(res.cookies)
    return cookie


def get_user_data():
    url = url_prefix + "/user"
    cookie = get_cookie(login())
    response = requests.get(url, headers=headers, cookies=cookie)
    doc = pq(response.text)
    data_text = doc('div .card-wrap')
    ret = "日志"
    for txt in data_text.items():
        ret = ret + '\n' + str(txt.text())
    return ret


def check_in():
    url = url_prefix + "/user/checkin"
    cookie = get_cookie(login())
    response = requests.post(url, headers=headers, cookies=cookie)
    print(response.text.encode().decode("unicode-escape"))

def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


# "{"msg":"获得了 291 MB流量.","unflowtraffic":109172490240,"traffic":"101.67GB","trafficInfo":{
# "todayUsedTraffic":"8.51MB","lastUsedTraffic":"22.99GB","unUsedTraffic":"78.68GB"},"ret":1}"

if __name__ == "__main__":
    # 填写你的账号密码
    your_email = ""
    your_password = ""
    check_in()

