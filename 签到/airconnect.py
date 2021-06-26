# -*- coding: utf-8 -*-
"""
@Time ： 2021/4/20 9:45
@Auth ： Twinzo1
@File ：airconnect.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.1
@Description: 全球加速签到
"""
import requests
import json

import os

# 安装必要的库
count = 2  # 此部分参考了 178.py
while count:
    try:
        from pyquery import PyQuery as pq

        break
    except:
        print('检测到没有 pyquery 库，开始换源进行安装')
        if count == 2:
            pip = 'pip3'
        else:
            pip = 'pip'
        os.system(f'{pip} install pyquery -i https://pypi.tuna.tsinghua.edu.cn/simple')
        count -= 1
        continue


def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


def escape2dict(es_str, escapes='\n'):
    """
    将下面两种形式的字符串分割为字典
    '会员时长\n5 天'
    '可用流量\n37.84 GB\n今日已用: 29.03MB'
    :param es_str: 字符串
    :param escapes: 转义符类型
    :return:
    """
    split_ret = [id.split(':', 1) for id in es_str.split('{}'.format(escapes))]
    ret_dict = {}
    flag = True
    for i, s in enumerate(split_ret):
        if len(s) == 2:
            ret_dict[str(s[0]).strip()] = s[1].strip()
            flag = True
        elif not flag:
            flag = True
        else:
            ret_dict[str(s[0]).strip()] = split_ret[i+1][0].strip()
            flag = False
    return ret_dict


class AirConnect:
    def __init__(self, your_email, your_password):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.116 Safari/537.36',
        }
        self.url_prefix = "http://xn--15qp3au64eprx.com"
        self.email = your_email
        self.password = your_password
        self.cookie = self.get_cookie()
        # self.url_prefix = "https://xn--15qp3au64eprx.com"

    def login(self):
        url = self.url_prefix + "/auth/login"
        data = {
            'email': self.email,
            'passwd': self.password,
        }
        response = requests.post(url, headers=self.headers, data=data)
        if "登录成功" in response.text.encode().decode("unicode-escape"):
            return response
        else:
            print("登录失败")
            return

    def get_cookie(self):
        cookie = requests.utils.dict_from_cookiejar(self.login().cookies)
        return cookie

    def get_user_data(self):
        url = self.url_prefix + "/user"
        response = requests.get(url, headers=self.headers, cookies=self.cookie)
        doc = pq(response.text)
        data_text = doc('div .card-wrap')
        user_name = doc('div .d-sm-none').text().replace("Hi, ", "")
        ret = {"账号名": user_name}
        for txt in data_text.items():
            ret.update(escape2dict(txt.text()))
        return ret

    def check_in(self):
        url = self.url_prefix + "/user/checkin"
        response = requests.post(url, headers=self.headers, cookies=self.cookie)
        msg = json.loads(response.text.encode().decode("unicode-escape"))
        return {"签到": msg['msg']}


def main():
    account = {
        "zzzz": {"email": "",
                  "password": ""},
        "zzss": {"email": "",
                  "password": ""},
    }
    msg_content = ""
    id = 0
    for key in account:
        ac = AirConnect(account[key]['email'], account[key]['password'])
        data_dict = ac.get_user_data()
        data_dict.update(ac.check_in())
        id += 1
        msg_content += "账号" + str(id) + "\n"
        for key in data_dict:
            msg_content += key + ": " + data_dict[key] + "\n"
        msg_content += "\n"
    try:
        import SendMsg

        token = os.getenv('DD_SIGN_IN_BOT_TOKEN')
        secret = os.getenv('DD_SIGN_IN_BOT_SECRET')
        send = SendMsg.SendMsg(token, secret)
        send.msg(title, content)
    finally:
        print(msg_content)


if __name__ == "__main__":
    # 填写你的账号密码
    # your_passwordr_email = ""
    # your_password = ""
    # ac = AirConnect(your_email, your_password)
    # print(ac.check_in())
    main()


