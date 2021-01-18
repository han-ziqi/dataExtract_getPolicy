# -*- codeing = utf-8 -*-
# @Time : 2021/1/12 3:48 下午
# @Author : Han
# @File : spider.py
# @Software : PyCharm

import json
import bs4
from bs4 import BeautifulSoup
import urllib.request, urllib.error  # 指定url获取网页数据
import xlwt  # 进行Excel操作
import sqlite3  # 进行SQLite数据库操作


def main():
    base_url = "http://sousuo.gov.cn/data?t=zhengcelibrary_or&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=title&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&p="

    # 1、爬取网页
    datalist = getData(base_url)
    # save_path = "政策解读1-1000.xls"
    db_path = "policy_t.db"
    # 3、保存数据
    # saveData(datalist, save_path)
    saveData2DB(datalist, db_path)


# 1、爬取网页
def getData(base_url):
    datalist = []

    for i in range(-1, 0):  # 设置循环，i从0到100，每页10条
        url = base_url + str(i + 1) + str("&n=10&inpro=&bmfl=&dup=&orpro=")
        htmlJson = askURL(url)  # 保存获取到的json对象

        # 2.1 逐一解析数据
        htmldict = json.loads(htmlJson)  # 将json对象转换为python字典
        vO = htmldict.get("searchVO").get('listVO')
        for item in vO:
            data = []  # 新建列表来存放每一条政策内容

            titles = item.get('title')  # 获取标题
            data.append(titles)  # 添加标题

            time = item.get('pubtimeStr')
            data.append(time)  # 添加发表时间

            summary = item.get('summary')
            data.append(summary)  # 添加摘要

            urlDe = item.get('url')
            data.append(urlDe)  # 添加标题

            htmldetail = getDetails(urlDe)  # 获取详情页URL
            f_words = getFormatWord(htmldetail)  # 调用2.4，得到有格式的正文(item1)
            data.append(f_words)  # 添加带格式的内容

            p_words = getPureWord(htmldetail)  # 调用2.5，得到无格式的正文(item2)
            data.append(p_words)  # 添加不带格式的内容

            datalist.append(data)

        # print(datalist)  #预览效果

    return datalist


# 2.2 定义方法：获得政策库文件列表
def askURL(url):
    # 用户代理，表示告诉服务器，我们是什么浏览器，本质是告诉浏览器，我们可以接受什么水平的内容
    head = {
        "User-Agent": "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36"}
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
    head = {
        "User-Agent": "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36"}
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
    for item_1 in soup.find_all('div', class_="pages_content"):  # 提取div标签中class为pages_content的内容
        item_1 = str(item_1)  # 格式化成字符串形式
        return item_1


# 2.5解析获取到详情页，不带格式的data传回2.1
def getPureWord(html_detail):
    soup = BeautifulSoup(html_detail, "html.parser")
    for item_2 in soup.find_all('div', class_="pages_content"):
        item_2 = soup.find_all('p')
        result = [p.get_text() for p in item_2]
        p_word = "".join(result)  # 使用join方法，分隔符为空
    return p_word


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
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            data[index] = "'" + data[index] + "'"  # 作用：把每一个内容都加上单引号
            sql = '''
            insert into policy_t(title,pub_date,summary,url,fdetail,pdetail)
           values(%s)''' % ",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(db_path):
    sql = '''
        create table policy_t
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
