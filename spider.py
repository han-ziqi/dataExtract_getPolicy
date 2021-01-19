# -*- codeing = utf-8 -*-
# @Time : 2021/1/12 3:48 下午
# @Author : Han
# @File : spider.py
# @Software : PyCharm

import re
import random
import time
import numpy as npl
import json
from bs4 import BeautifulSoup
import urllib.request, urllib.error  # 指定url获取网页数据
from urllib.request import urlretrieve
import xlwt  # 进行Excel操作
import sqlite3  # 进行SQLite数据库操作


def main():
    base_url = "http://sousuo.gov.cn/data?t=zhengcelibrary_or&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=title&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&p="
    # 1、爬取网页
    datalist = getData(base_url)
    # save_path = "政策解读1-1000.xls"
    db_path = "policy5000.db"
    # 3、保存数据
    # saveData(datalist, save_path)
    # saveData2DB(datalist, db_path)


# 文件链接的规则
findLink = re.compile(r'<a href="(.*?)" ')  # 创建正则表达式对象，表示规则（字符串的模式）
# 文件图片
findImgSrc = re.compile(r'<img.*src="(.*?)"')
# 详情页前半段URL的提取
findPreUrl = re.compile(r'(.*)content')

# 1、爬取网页
def getData(base_url):
    datalist = []

    for i in range(691, 692):  # 设置循环，i从0到100，每页10条
        url = base_url + str(i + 1) + str("&n=10&inpro=&bmfl=&dup=&orpro=")
        htmlJson = askURL(url)  # 保存获取到的json对象

        # 2.1 逐一解析数据
        htmldict = json.loads(htmlJson)  # 将json对象转换为python字典
        vO = htmldict.get("searchVO").get('listVO')
        for item in vO:
            data = []  # 新建列表来存放每一条政策内容
            file_url = "" # 初始化file_name
            img_add = "" # 初始化img_url

            titles = item.get('title')  # 获取标题
            data.append(titles)  # 添加标题
            print(titles)

            pub_time = item.get('pubtimeStr')
            data.append(pub_time)  # 添加发表时间
            print(pub_time)

            summary = item.get('summary')
            data.append(summary)  # 添加摘要

            urlDe = item.get('url')
            data.append(urlDe)  # 添加标题

            htmldetail = getDetails(urlDe)  # 获取详情页URL

            f_words = getFormatWord(htmldetail)  # 调用2.4，得到有格式的正文(item1)
            data.append(f_words)  # 添加带格式的内容

            p_words = getPureWord(htmldetail)  # 调用2.5，得到无格式的正文(item2)
            data.append(p_words)  # 添加不带格式的内容

            file_name = getFileName(htmldetail)  # 调用2.6，得到文件后半段名字

            pre_url_list = re.findall(findPreUrl,str(urlDe)) # 通过正则表达式提取详情页URL的前半段
            pre_url = "".join(pre_url_list)   # 遍历提取到的数组成字符串，得到URL前半段
            print(type(pre_url))

            if len(file_name) != 0:
                file_url = pre_url + file_name  # 文件完整URL前半段+文件后半段名字
            print(file_url)


            img_add = getImgName(htmldetail,pre_url)  # 调用2.7，得到图片后半段名字
            print(img_add)


            """
            图片(文件)下载,核心方法是 urllib.urlrequest 模块的 urlretrieve()方法
             urlretrieve(url, filename=None, reporthook=None, data=None)
             url: 文件url
             filename: 保存到本地时,使用的文件(路径)名称
             reporthook: 文件传输时的回调函数
             data: post提交到服务器的数据
             该方法返回一个二元元组("本地文件路径",<http.client.HTTPMessage对象>)
            """

            datalist.append(data)

        t = random.uniform(0,0.3)
        time.sleep(t)
        # 仪表盘：
        m = i + 1  # 表示第x个
        n = i + 2  # 到第x个
        print("正在爬取第%d0~%d0条网页，完成后休眠%f秒" % (m, n, t))
        # print(datalist)

    return datalist


# 2.1 创建列表：搜集到常用headers，随机选择以应对403封禁
my_headers = [
    "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36",
    "Mozilla / 5.0(Macintosh;Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
]


# 2.2 定义方法：获得政策库文件列表
def askURL(url):
    # 用户代理，表示告诉服务器，我们是什么浏览器，本质是告诉浏览器，我们可以接受什么水平的内容
    head = {"User-Agent": random.choice(my_headers)}
    request = urllib.request.Request(url, headers=head)
    html_list = ""
    try:
        response = urllib.request.urlopen(request)
        html_list = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html_list


# 2.3 定义方法：读取datalist里url，进入详情页获取详情页面
def getDetails(url_De):
    head = {"User-Agent": random.choice(my_headers)}
    request = urllib.request.Request(url_De, headers=head)
    html_detail = ""
    try:
        response = urllib.request.urlopen(request)
        html_detail = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html_detail


# 2.4 解析获取到详情页，带格式的data传回2.1
def getFormatWord(html_detail):
    soup = BeautifulSoup(html_detail, "html.parser")  # 解析页面
    for item_4 in soup.find_all('div', class_="pages_content"):  # 提取div标签中class为pages_content的内容
        item_4 = str(item_4)  # 格式化成字符串形式
        return item_4


# 2.5解析获取到详情页，不带格式的data传回2.1
def getPureWord(html_detail):
    soup = BeautifulSoup(html_detail, "html.parser")
    for item_5 in soup.find_all('div', class_="pages_content"):
        item_5 = soup.find_all('p')
        result = [p.get_text() for p in item_5]
        p_word = "".join(result)  # 使用join方法，分隔符为空
    return p_word


# 2.6解析获取到的详情页，把文件名传回2.1
def getFileName(html_detail):
    soup = BeautifulSoup(html_detail, "html.parser")
    for item_6 in soup.find_all('div', class_="pages_content"):
        file_link = re.findall(findLink, str(item_6))
        f_link = "".join(file_link)
    return f_link


# 2.7解析获取到的详情页，把图片地址传回2.1，图片可能有多个，因此直接在此方法里拼接完整URL，再返回2.1
def getImgName(html_detail,pre_url):
    soup = BeautifulSoup(html_detail, "html.parser")
    for item_7 in soup.find_all('div', class_="pages_content"):
        img_link_list = re.findall(findImgSrc, str(item_7))
        if len(img_link_list) != 0:
            img_link = ",".join(img_link_list)
            img_url = pre_url + img_link
        else:
            img_url=""
    return img_url


'''
# 3、保存数据
def saveData(datalist,sava_path):
    print("开始储存数据")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet("政策解读1",cell_overwrite_ok=True)  # 创建工作表
    col = ("政策标题", "政策发布时间", "政策摘要","政策链接","解读正文(带格式)","解读正文(不带格式)")
    for i in range(0, 6):
        sheet.write(0, i, col[i]) #列名
    for i in range(0, 1000):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,6):
            sheet.write(i+1,j,data[j])  #数据

    book.save(sava_path)
'''


# 4、保存数据到数据库
def saveData2DB(datalist, db_path):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    print("连接数据库成功，开始保存")
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            data[index] = "'''" + data[index] + "'''"  # 作用：把每一个内容都加上单引号
            sql = '''
            insert into policy5000(title,pub_date,summary,url,fdetail,pdetail)
            values(%s)''' % ",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    print("保存成功")
    conn.close()


def init_db(db_path):
    sql = '''
        create table policy5000
        (
          id integer primary key autoincrement,
          title varchar,
          pub_date varchar ,
          summary varchar,
          url varchar,
          fdetail varchar ,
          pdetail varchar 
        )'''

    # 创建数据表
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":  # 当程序执行时# 调用函数
    main()

    print("爬取完毕")
