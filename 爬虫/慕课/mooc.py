# -*- coding: utf-8 -*-
"""
@Time ： 2021/4/20 13:56
@Auth ： Twinzo1
@File ：mooc.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
@Version: V1.0
@Description: 慕课课件爬取
"""
import sqlite3
import requests
import os
import json
from pyquery import PyQuery as pq
from tqdm import tqdm
import time

def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


def My_mkdir(dirs):
    """
    判断目录是否存在，否则建立目录，不支持递归
    :param dirs:
    :return:
    """
    if not os.path.isdir(dirs):
        print("创建目录"+dirs)
        os.mkdir(dirs)


class IMOOC(object):
    def __init__(self, cookie_str):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.116 Safari/537.36',
        }
        self.cookie = str2dict(cookie_str)
        self.url_prefix = "https://mooc1-1.chaoxing.com"
        self.login_url = "http://i.mooc.chaoxing.com/space/index"

    def download_file(self, path, info_dict):
        """
        下载文件
        :param path: 文件保存路径
        :param info_dict: 字典包含 文件的url，名称
        :return:
        """
        response = requests.get(info_dict['download'], cookies=self.cookie, headers=self.headers)
        save_name = path + "/" + info_dict['filename']
        # 有pdf则下载pdf文件
        if info_dict.get('pdf'):
            response = requests.get(info_dict['pdf'], cookies=self.cookie, headers=self.headers)
            save_name = save_name.replace('pptx', 'pdf')
        print("下载文件：" + save_name)
        # 判断文件是否存在
        if os.path.isfile(save_name):
            print(save_name+"已存在")
        with open(save_name, "wb") as f:
            f.write(response.content)

    def get_course_url(self):
        """
        获取“我学的课”真实url
        :return: url
        """
        response = requests.get(self.login_url, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        return doc('iframe').attr('src')

    def get_course(self):
        """
        获取“我学的课”课程列表
        :return: 课程信息及链接，字典形式
        """
        urls = self.get_course_url()
        response = requests.get(urls, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        class_all = doc('div .Mconright.httpsClass')
        course_dict = {}
        for cls in class_all.items():
            cls_info = []
            for tl in cls('p').items():
                if tl.attr('title') is not None:
                    cls_info.append(tl.attr("title").replace('\xa0', ' '))
            if not cls_info:
                cls_info = cls.text().split('\n')[1:]
                cls_info.extend(["", ""])
            course_dict[cls("a").attr('title')] = {'任课老师': cls_info[0], '学校': cls_info[1], '班级': cls_info[2],
                                                   '课程链接': self.url_prefix + cls("a").attr('href')}
        return course_dict

    def get_class(self, url):
        """
        获取课程章节列表及链接
        :return: 返回课程章节名称及链接，字典形式
        """
        urls = url
        response = requests.get(urls, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        cls_epi = doc('.timeline a')
        class_dict = {}
        tmp_list = []
        for cls in cls_epi.items():
            if "javascript:void" in cls.attr('href'):
                if tmp_list:
                    class_dict[tmp_list[0]] = dict(tmp_list[1:])
                tmp_list = [cls.text()]
            else:
                if cls.text():
                    tmp_list.append([cls.text(), self.url_prefix + cls.attr('href')])
        if class_dict.get(tmp_list[0]) is None:
            class_dict[tmp_list[0]] = dict(tmp_list[1:])

        return class_dict

    def get_cls_iframe_url(self, url):
        """
        获取课件框架的真实url
        :return: url，字符串
        """
        # urls = get_class()
        urls = url
        response = requests.get(urls, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        script_str = doc('script')
        url_info = ""
        for ss in script_str.items():
            if "personid" in ss.attr('src'):
                url_info = ss.attr('src').split('&')
                break

        courseId = [id.split('=')[1] for id in url_info if "courseId" in id][0]
        clazzid = [id.split('=')[1] for id in url_info if "classId" in id][0]
        chapterId = [id.split('=')[1] for id in url_info if "chapterId" in id][0]
        num = "0"
        # personid = [id.split('=')[1] for id in url_info[0].split('?') if "personid" in id][0]

        html_str = doc.text()
        lid = html_str.rfind('document.getElementById("iframe").src')
        tmp_src = html_str[lid:]
        tmp_lid = tmp_src.find('=')
        rid = tmp_src.find(';')
        knowledge_url = self.url_prefix + tmp_src[tmp_lid + 1:rid][1:-1]
        knowledge_url = knowledge_url.replace('"+clazzid+"', clazzid).replace('"+chapterId+"', chapterId).replace(
            '"+courseId+"', courseId).replace('"+num+"', num)
        return knowledge_url

    def get_file_url(self, url):
        """
        获取课件信息的url
        :return: url
        """
        urls = self.get_cls_iframe_url(url)
        # urls = "https://mooc1-1.chaoxing.com/knowledge/cards?clazzid=37159847&courseid=216717297&knowledgeid=399749990&num=0&ut=s&cpi=148807753&v=20160407-1"
        response = requests.get(urls, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        courseware_list = []
        for info in doc('iframe').items():
            data = info.attr('data').replace('&quot;', '').encode().decode("unicode-escape")
            data_json = json.loads(data)
            courseware_list.append(
                {'file_url': self.url_prefix + "/ananas/status/" + data_json['objectid'] + "?flag=normal",
                 'file_name': data_json['name']})
        return courseware_list

    def get_file(self, url_info):
        """
        获取课件的url及其它信息
        :return: url
        """
        # url = get_file_url()
        urls = url_info['file_url']
        response = requests.get(urls, cookies=self.cookie, headers=self.headers)
        doc = pq(response.text)
        str_info = doc('p').text()
        dict_info = json.loads(str_info)
        dict_info['filename'] = url_info['file_name']
        return dict_info


def main(abs_path="./"):
#     course_list = get_course()
    
#     for key in course_list.keys():
#         course = key
#         root_path = abs_path + course
#         cls_list = get_class(course_list[course]['课程链接'])
#         My_mkdir(root_path)
#         for cos in cls_list.keys():
#             course_name_path = root_path + "/" + cos
#             My_mkdir(course_name_path)
#             for chap in cls_list[cos].keys():
#                 chapter_name_path = course_name_path + "/" + chap
#                 My_mkdir(chapter_name_path)
#                 try:
#                     for u in get_file_url(cls_list[cos][chap]):
#                         if not os.listdir(chapter_name_path):
#                             download_file(chapter_name_path, get_file(u))
#                 except:
#                     pass
    course = '投资学'
    root_path = abs_path + course
    mooc_course = IMOOC(cookie)

    course_list = mooc_course.get_course()
    cls_list = mooc_course.get_class(course_list[course]['课程链接'])
    My_mkdir(root_path)
    for cos in cls_list.keys():
        course_name_path = root_path + "/" + cos
        My_mkdir(course_name_path)
        for chap in cls_list[cos].keys():
            chapter_name_path = course_name_path + "/" + chap
            My_mkdir(chapter_name_path)
            try:
                for u in mooc_course.get_file_url(cls_list[cos][chap]):
                    if not os.listdir(chapter_name_path):
                        mooc_course.download_file(chapter_name_path, mooc_course.get_file(u))
            except:
                pass

if __name__ == "__main__":
    # 填写cookie
    cookie = ""
    main()
