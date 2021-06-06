# -*- coding: utf-8 -*-
"""
@Time ： 2021/6/4 21:43
@Auth ： Twinzo1
@File ：bdwenku.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.0
@Description: 百度文库爬取
"""

import requests
import json
from pyquery import PyQuery as pq
import re


def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


def get_html():
    """
    获取网页html
    :param url:
    :param headers:
    :param code:
    :return:
    """
    wenku_url = bidu_url
    headers = {"user-agent": "LogStatistic"}
    if not cookie_str or len(cookie_str.strip()) == 0:
        res = requests.get(wenku_url, headers=headers)
    else:
        cookie = str2dict(cookie_str)
        res = requests.get(wenku_url, cookies=cookie, headers=headers)
    res.encoding = res.apparent_encoding
    doc = pq(res.text)
    return doc


def get_Title():
    title = get_html()('title')
    return title.text().replace(" - 百度文库", "")


def get_page_url():
    """
    用于获取每一页的url
    :return:
    """
    content = get_html()('script')
    url_co_dict = {}
    for url_info in content.items():
        if "var pageData" in url_info.text():
            url_li = re.findall(r"=(.+);.?window.pageData", url_info.text())
            url_co_dict = json.loads(url_li[0])

    url_dict_li = json.loads(url_co_dict['readerInfo2019']['htmlUrls'])['json']
    return url_dict_li


def format_dict_str(dict_str):
    """
    用于格式化不符合格式的字典字符串，如{"key":"value "EEE""},将之格式化为{"key":"value \"EEE\""}
    :param dict_str:
    :return:
    """
    fstSplit = re.split(':', dict_str)
    colon_str = []
    for sp1 in fstSplit:
        secSplit = re.split(",", sp1)
        comma_str = []
        for sp2 in secSplit:
            if sp2.count('"') == 2 or sp2.count('"') == 0:
                comma_str.append(sp2)
                continue
            if sp2.count('"')-2 != sp2.count(r'\"'):
                splitBack = sp2.replace(r'"', r'\"')
                if sp2.count('"') % 2 != 0:
                    # 替换最后一个\"
                    sp2 = splitBack[::-1].replace('"\\', '"', 1)[::-1]
                    comma_str.append(sp2)
                    continue
                splitBack1 = splitBack.replace(r'\"', '"', 1)
                # 替换最后一个\"
                sp2 = splitBack1[::-1].replace('"\\', '"', 1)[::-1]
            comma_str.append(sp2)
        sp1 = ",".join(comma_str)
        colon_str.append(sp1)
    return ":".join(colon_str)


def get_page_content(page_url):
    """
    获取每一页的内容
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.116 Safari/537.36"
    }
    if not cookie_str or len(cookie_str.strip()) == 0:
        res = requests.get(page_url, headers=headers)
    else:
        cookie = str2dict(cookie_str)
        res = requests.get(page_url, cookies=cookie, headers=headers)
    res.encoding = res.apparent_encoding
    res_txt = res.text
    res_cn = res_txt.encode('utf-8').decode('unicode_escape', 'ignore')
    res_cn_li = re.findall(r"\((.+)\)", res_cn)

    res_cn_dict = json.loads(format_dict_str(res_cn_li[0]))
    res_co_li = res_cn_dict['body']
    res_li = []

    for co_dict in res_co_li:
        res_li.append([co_dict['c'], co_dict['p']['y']])

    res_co_li = []
    
    # 使用坐标定位
    for i, val in enumerate(res_li):
        if i == 0:
            res_co_li.append(val[0])
        else:
            if str(val[1]) == str(res_li[i-1][1]):
                res_co_li[-1] = str(res_co_li[-1]) + str(val[0])
            else:
                res_co_li.append(val[0])

    return res_co_li


def main():
    url_info_dict_li = get_page_url()
    title = get_Title()
    for url_info in url_info_dict_li:
        print("开始下载第{}页数据" .format(url_info['pageIndex']))

        page_content = get_page_content(url_info['pageLoadUrl'])

        # 写入文本
        if url_info == url_info_dict_li[0]:
            with open("./" + title + ".txt", 'w+', encoding='utf-8') as f:
                print("开始下载第{}页数据" .format(url_info['pageIndex']))
                for content_li in page_content:
                    f.write(str(content_li) + "\n")
                f.close()
        else:
            with open("./" + title + ".txt", 'a+', encoding='utf-8') as f:
                print("开始下载第{}页数据" .format(url_info['pageIndex']))
                for content_li in page_content:
                    f.write(str(content_li) + "\n")
                f.close()


if __name__ == '__main__':
    # 填写你的cookie，不填只能爬取部分
    cookie_str = ""
    # 百度文库url
    bidu_url = "https://wenku.baidu.com/view/0959513c6fdb6f1aff00bed5b9f3f90f76c64dc8.html"
    main()

