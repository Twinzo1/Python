# -*- coding: utf-8 -*-
"""
@Time ： 2021/3/12 0:21
@Auth ： Twinzo1
@File ：comic18.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.0
@Description: 韩漫爬取，目前只是爬取目录
"""
import os
import re

import  requests
from pyquery import PyQuery as pq

def get_html(url, headers=1, code="utf-8"):
    """
    获取网页html
    :param url:
    :param headers:
    :param code:
    :return:
    """
    if headers == 1:
        # 电脑
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/78.0.3904.116 Safari/537.36"}
        # 手机浏览器
        # headers = {"user-agent": "Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; Nexus 6P Build/OPM7.181205.001) "
        #                          "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 "
        #                          "UCBrowser/12.11.1.1197 Mobile Safari/537.36"}
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    r.raise_for_status()
    r.encoding = code
    return r.text


def get_comic_nums(html):
    """
    获取韩漫总数
    :param html:
    :return:
    """
    doc = pq(html)
    dirs = doc('.text-white')
    ret = 720
    for d in dirs.items():
        if "A漫" in str(d):
            ret = int(d.text()) + 1
    return ret


def get_comic_id(html):
    """
    获取全部韩漫的id，名字
    :param html:
    :return:
    """
    doc = pq(html)
    ids = doc('.text-white')
    titles = doc('.video-title')
    links = doc('div .well a')
    # print(links)
    comic_title = []
    comic_id = []
    comic_link = []
    for ci in ids.items():
        comic_id.append(ci.text())
    for tl in titles.items():
        comic_title.append(tl.text())
    for ln in links.items():
        if re.findall(r'album/\d', ln.attr('href')):
            comic_link.append(ln.attr('href'))
    comic_info = []
    for cod, cot, col in zip(comic_id[3:], comic_title, comic_link):
        comic_info.append([cod,cot,col])
    return comic_info

def get_all_id(url):
    html = get_html(url)
    whole_num = get_comic_nums(html)
    all_korea_comic = []
    for n in range(1, whole_num//80+2):
        page_url = url + "?page=" + str(n)
        print(page_url)
        print(n)
        all_korea_comic.extend(get_comic_id(get_html(page_url)))
    print(len(all_korea_comic))
    with open("./hanman", "w", encoding="utf-8") as fk:
        for co in all_korea_comic:
            fk.write(str(co) + "\n")
    fk.close()


def get_dir(html):
    """
    获取每一本书的目录
    :param html:
    :return:
    """
    doc = pq(html)
    ids = doc('a')
    chapter_link = []
    for id in ids.items():
        if id('li'):
            if id.attr('href') not in chapter_link:
                chapter_link.append(id.attr('href'))

    print(chapter_link)
    print(len(chapter_link))


def get_pic(html):
    """
    获取每一章节的图片链接
    :param html:
    :return:
    """

    doc = pq(html)
    pics = doc('div img')
    for pic in pics.items():
        tmp_data = pic.attr('data-original')
        if tmp_data is not None and "media/photos" in tmp_data:
            print(tmp_data)
    # print(pics)


def main(url):
    html = get_html(url)

    get_comic_id(html)
    get_dir(html)


def download_img(path, url):
    if url == "":
        return
    response = requests.get(url)
    # index = url.rfind(':')
    # suffix = url[index:]
    # file_name = url + suffix
    # save_name = path + "/" + file_name
    # save_name = "./456.jpg"
    print("下载图片：" + save_name)
    if os.path.isfile(save_name):
        return
    with open(save_name, "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    # 分流
    url_list = []
    url = "https://18comic.vip/albums/hanman"
    # url = "https://18comic.vip/album/224358/"
    # url = "https://18comic.vip/photo/241013?"
    get_all_id(url)
    # download_img("./",url)
