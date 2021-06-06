# -*- coding: utf-8 -*-
"""
@Time ： 2021/3/7 22:18
@Auth ： Twinzo1
@File ：mh.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.0
@Description: 韩漫爬取
"""
import os
import re
from time import time
import requests
from pyquery import PyQuery as pq
from threading import Thread


def get_html(url, headers, code="utf-8"):
    """
    获取网页html
    :param url:
    :param headers:
    :param code:
    :return:
    """
    if headers == "":
        headers = {"user-agent": "Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; Nexus 6P Build/OPM7.181205.001) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 "
                                 "UCBrowser/12.11.1.1197 Mobile Safari/537.36"}
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    r.raise_for_status()
    r.encoding = code
    return r.text


def get_dir(html, url_link):
    doc = pq(html)
    dirs = doc('ul li .chapteritem')
    chapter_list = []
    book_name = doc('.normal-top-title').text()
    l_url = url_link
    for tag in dirs.items():
        tmp_dir = tag.text()
        tmp_dir = tmp_dir.replace(book_name, "")
        tmp_dir = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u002d])", "", tmp_dir)
        chapter_list.append([l_url + tag.attr.href, tmp_dir])
    chapter_list.append(book_name)
    return chapter_list


def download_img(path, url):
    if url[1] == "":
        return
    response = requests.get(url[1])
    index = url[1].rfind('.')
    suffix = url[1][index:]
    file_name = url[0] + suffix
    save_name = path + "/" + file_name
    if os.path.isfile(save_name):
        e_file = os.listdir(path + "/")
        if e_file[e_file.index(file_name)] != e_file[-1] or e_file[e_file.index(file_name)] != e_file[-2]:
            return
    print("下载图片：" + save_name)
    with open(save_name, "wb") as f:
        f.write(response.content)


def get_pic(url):
    html = get_html(url[0], "")
    doc = pq(html)
    pics = doc('.view-main-1 .lazy')
    img_url = []
    for i, tag in enumerate(pics.items()):
        img_url.append([str(url[2]) + str(i + 101), tag.attr('data-original')])
    img_url.append(["", ""])
    # 双线程
    for href1, href2 in zip(img_url[::2], img_url[1::2]):
        start1 = time()
        th1 = Thread(target=download_img, args=(url[1], href1))
        th1.start()
        th2 = Thread(target=download_img, args=(url[1], href2))
        th2.start()
        th1.join()
        th2.join()
        end1 = time()
        print('总共耗费了%.2f秒.' % (end1 - start1))


def main(url_num):
    url = "https://www.ikanmh.top/book/" + str(url_num)
    # url = "https://www.xiximh.com/book/" + str(url_num)
    index = url.rfind("book")
    pure_url = url[0:index - 1]
    html = get_html(url, "")
    html_list = get_dir(html, pure_url)

    # 创建目录
    root_dir = "./" + html_list[-1].replace(":", "之").replace("：", "之")
    sub_dir = []

    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)

    for i, li in enumerate(html_list[0:-1]):
        if "-" not in li[1] and not re.findall(r'第\d', li[1]):
            li[1] = "第" + str(i + 1) + "话" + "-" + li[1]
        v = root_dir + "/" + li[1]

        if not os.path.isdir(v):
            os.mkdir(v)
        sub_dir.append(v)

    start_position = ""
    for i, v in enumerate(sub_dir):
        start_position = -1
        if not os.listdir(v):
            le = 1 if i == 0 else i
            start_position = le - 1
            break
    start_position = 0 if start_position == "" else start_position

    for i, li in enumerate(html_list[start_position:-1]):
        # 章节导航位置
        if "-" not in li[1] and not re.findall(r'第\d', li[1]):
            li[1] = "第" + str(i + 1) + "话" + "-" + li[1]
        li[1] = root_dir + "/" + li[1]
        li.append(str(url_num) + str(i + 1))
        get_pic(li)


def th_cycle(th_list):
    for t in th_list:
        t.start()
        # t.join()


if __name__ == "__main__":
    # ikanmh
    # comic_list = [6, 7, 25, 87, 184, 211, 237, 267, 294, 369, 410, 412, 418, 420, 429, 447, 472, 476, 478,
    #               479, 483, 485, 487, 488]
    # xiximh
    comic_list = [25,483,479,472]
    start = time()
    th = []
    for co in comic_list:
        th.append(Thread(target=main, args=(co,)))
    t1 = Thread(target=th_cycle, args=(th[::2],))

    t1.start()
    t2 = Thread(target=th_cycle, args=(th[1::2],))
    t2.start()
    t1.join()
    t2.join()

    end = time()
    print('总共耗费了%.2f秒.' % (end - start))
