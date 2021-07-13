# -*- coding: utf-8 -*-
"""
@Time ： 2021/6/4 21:43
@Auth ： Twinzo1
@File ：bdwenku.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V2.21
@Description: 百度文库爬取
"""

import requests
import json
import re
from pyquery import PyQuery as pq
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_LINE_SPACING


def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    ret_dict = dict([item.split("=", 1) for item in json_str.split(";")])
    return ret_dict


def format_dict_str(dict_str):
    """
    用于格式化不符合格式的字典字符串，如{"key":"value "EEE""},将之格式化为{"key":"value \"EEE\""}
    :param dict_str:
    :return:
    """
    first_split = re.split(':', dict_str)
    colon_str = []
    for sp1 in first_split:
        second_split = re.split(",", sp1)
        comma_str = []
        for sp2 in second_split:
            if sp2.count('"') == 2 or sp2.count('"') == 0:
                comma_str.append(sp2)
                continue
            if sp2.count('"') - 2 != sp2.count(r'\"'):
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


class BDWenKu:
    def __init__(self, bd_url, bd_cookie=""):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/78.0.3904.116 Safari/537.36 "
        }
        self.cookie = str2dict(bd_cookie) if bd_cookie != "" else ""
        self.url = bd_url
        self.pq_html = self.get_html()
        self.title = self.get_title()

    def get_html(self):
        """
        获取网页html
        :param url:
        :param headers:
        :param code:
        :return:
        """
        headers = {"user-agent": "LogStatistic"}
        res = self.with_cookie(self.url, headers)
        doc = pq(res.text)
        return doc

    def get_title(self):
        title = self.pq_html('title')
        return title.text().replace(" - 百度文库", "")

    def with_cookie(self, url, headers=""):
        headers = self.headers if headers == "" else headers
        if not self.cookie or len(str(self.cookie).strip()) == 0:
            res = requests.get(url, headers=headers)
        else:
            res = requests.get(url, cookies=self.cookie, headers=headers)
        res.encoding = res.apparent_encoding
        return res

    def get_page_url(self):
        """
        用于获取每一页的url
        :return:
        """
        content = self.pq_html('script')
        for url_info in content.items():
            if "var pageData" in url_info.text():
                url_list = re.findall(r"=(.+);.?window.pageData", url_info.text())
                content_have_url_dict = json.loads(url_list[0])
                break

        url_dict_list = json.loads(content_have_url_dict['readerInfo']['htmlUrls'])['json']
        return url_dict_list

    def get_page_content(self, page_url):
        """
        获取每一页的内容
        :return:
        """
        res = self.with_cookie(page_url)
        # 乱码变中文
        res_cn = res.text.encode('utf-8').decode('unicode_escape', 'ignore')
        res_cn_list = re.findall(r"\((.+)\)", res_cn)

        res_cn_dict = json.loads(format_dict_str(res_cn_list[0]))
        res_content_list = res_cn_dict['body']
        res_list = []

        for co_dict in res_content_list:
            res_list.append([co_dict['c'], co_dict['p']['y']])

        res_content_list = []

        for i, val in enumerate(res_list):
            if i != 0 and str(val[1]) == str(res_list[i - 1][1]):
                res_content_list[-1] = str(res_content_list[-1]) + str(val[0])
            else:
                res_content_list.append(val[0])

        return res_content_list

    def download(self, doc_type="txt"):
        if doc_type == "word":
            self.download_in_docx()
        else:
            self.download_in_txt()

    def download_in_txt(self):
        url_info_dict_list = self.get_page_url()
        for url_info_dict in url_info_dict_list:
            page_content = self.get_page_content(url_info_dict['pageLoadUrl'])

            # 写入文本
            print("开始下载第{}页数据".format(url_info_dict['pageIndex']))
            if url_info_dict == url_info_dict_list[0]:
                open_model = 'w+'
            else:
                open_model = 'a+'
            with open("./" + self.title + ".txt", open_model, encoding='utf-8') as f:
                for content_li in page_content:
                    f.write(str(content_li) + "\n")
            f.close()

    def download_in_docx(self):
        # 创建文档对象
        document = Document()

        # 设置文档标题，中文要用unicode字符串
        # document.add_heading(self.title, 0)
        url_info_dict_list = self.get_page_url()
        for url_info_dict in url_info_dict_list:
            page_content = self.get_page_content(url_info_dict['pageLoadUrl'])
            print("开始下载第{}页数据".format(url_info_dict['pageIndex']))
            for content_li in page_content:
                # 添加无序列表
                paragraph = document.add_paragraph(str(content_li))
                paragraph_format = paragraph.paragraph_format
                paragraph_format.space_before = Pt(0)
                paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
                paragraph_format.line_spacing = Pt(13)
        document.save("./" + self.title + ".docx")


if __name__ == '__main__':
    # 填写你的cookie，不填只能爬取部分
    cookie_str = "“
    # # 百度文库url
    bidu_url = "https://wenku.baidu.com/link?url=Uc1oG393S7TgZzVBlFuN5HiZXy8YRbH4ttS02yNC9OrPwSk6wUr-y5Cd-XACf7EnsWCL67V90VhYFsRGXSbHzCo4bUp4_YXsR5ThiYbIP8J96Athv4gRu1kJsqjAeZCE"
    # main()
    bidu = BDWenKu(bidu_url, cookie_str)
    bidu.download()
