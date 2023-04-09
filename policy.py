# -*- coding = utf-8 -*-
# @Time : 2021/1/25 5:31 下午
# @Author : Han
# @File : policy.py
# @Software : PyCharm

import re
import random
import time
import json
from bs4 import BeautifulSoup
import socket
import urllib.request
import urllib.error  # 指定url获取网页数据
import sqlite3  # 进行SQLite数据库操作


# 详情来源提取
findSource = re.compile(r'来源：(.*?)</span>')
# 文件地址提取
findFileLink = re.compile(r'<a href="(.*?)" ')  # 创建正则表达式对象，表示规则（字符串的模式）
# 文件名称提取
findFileName = re.compile(r'files/(.*)')
# 图片地址提取
findImgLink = re.compile(r'<img.*src="(.*?)"')
# 图片名称提取
findImgName = re.compile(r'images/(.*)')
# 详情页前半段URL的提取
findPreUrl = re.compile(r'(.*)content')


def main():
    base_url = "http://sousuo.gov.cn/data?t=zhengcelibrary_or&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=title&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&p="
    datalist = getData(base_url)  # 1、爬取网页
    db_path = "policy.db"
    saveData2DB(datalist, db_path)  # 3、保存数据


# 1、爬取网页
def getData(base_url):
    datalist = []

    for i in range(-1, 698):  # 设置循环，i从0到100，每页10条
        url = base_url + str(i + 1) + str("&n=10&inpro=&bmfl=&dup=&orpro=")
        htmlJson = askURL(url)  # 保存获取到的json对象
        m = i + 1  # 表示第x个
        n = i + 2  # 到第x个

        # 2.1 逐一解析数据
        html = json.loads(htmlJson)  # 将json对象转换为python字典
        vO = html.get("searchVO").get('listVO')
        for item in vO:
            data = []  # 新建列表来存放每一条政策内容
            file_url = ""  # 初始化file_name
            img_add = ""  # 初始化img_url
            titles = item.get('title')  # 获取标题
            data.append(titles)  # 添加标题
            pub_time = item.get('pubtimeStr')
            data.append(pub_time)  # 添加发表时间
            summary = item.get('summary')
            data.append(summary)  # 添加摘要
            urlDe = item.get('url')
            data.append(urlDe)  # 添加详情页URL
            htmldetail = askURL(urlDe)  # 获取详情页URL
            if htmldetail == "":
                print("第%d0~%d0条网页有问题，跳过" % (m, n))
                continue
            soup = BeautifulSoup(htmldetail, "html.parser")  # 直接调用bs4解析页面，避免后面用方法调用四次
            source_page = soup.find_all('div', class_="pages-date")
            source = getSource(source_page)  # 调用2.1，得到政策来源
            data.append(source)

            for item_1 in soup.find_all('div', class_="pages_content"):
                f_words = str(item_1)
                data.append(f_words)  # 添加带格式的内容
                p_words = getPureWord(item_1)  # 调用2.2，得到无格式的正文(item2)
                data.append(p_words)  # 添加不带格式的内容
                file_link = getFileLink(item_1)  # 调用2.3，得到文件后半段名字

                # 实现文件的下载，保存格式为发布日期+标题+后半段文件名
                if len(file_link) != 0:
                    file_name = getFileName(item_1)  # 调用2.4 得到文件去掉路径的名字
                    pre_url_list = re.findall(findPreUrl, str(urlDe))  # 通过正则表达式提取详情页URL的前半段
                    pre_url = "".join(pre_url_list)  # 遍历提取到的数组成字符串，得到URL前半段
                    file_url = pre_url + file_link  # 文件完整URL前半段+文件后半段名字
                    # 开始下载
                    download_file_name = titles + file_name
                    try:
                        socket.setdefaulttimeout(5)  # 设置下载文件超时时间
                        urllib.request.urlretrieve(url=file_url,
                                                   filename="/Users/han/Documents/Python/GovPolicy/Downloads/files/" + pub_time + download_file_name)
                    except urllib.error.HTTPError:
                        print("日期为" + pub_time + "的" + titles + "下载失败")
                        continue
                    except socket.timeout:
                        print("日期为" + pub_time + "的" + titles + "下载超时")
                        continue

                else:
                    pre_url_list = re.findall(findPreUrl, str(urlDe))  # 通过正则表达式提取详情页URL的前半段
                    pre_url = "".join(pre_url_list)  # 遍历提取到的数组成字符串，得到URL前半段
                    download_file_name = ""

                data.append(download_file_name)  # 添加进数据库

                # 实现图片的下载，保存格式为第X张+YYYY.MM.DD+标题+后半段文件名
                img_link_list = getImgUrl(item_1, pre_url)  # 调用2.4，得到图片链接的列表
                if len(img_link_list) != 0:
                    img_name_1 = getImgName(item_1, titles)  # 调用2.9，得到图片第一张的名字
                    img_link = " ".join(img_link_list)
                    for index, item_img in enumerate(img_link_list):
                        try:
                            socket.setdefaulttimeout(5)  # 设置下载文件超时时间
                            urllib.request.urlretrieve(url=item_img,
                                                       filename="/Users/han/Documents/Python/GovPolicy/Downloads/images/" + "第%s张" % str(
                                                           index + 1) + pub_time + img_name_1)
                        except urllib.error.HTTPError:
                            print("日期为" + pub_time + "的" + titles + "下载失败")
                            continue
                        except socket.timeout:
                            print("日期为" + pub_time + "的" + titles + "下载超时")
                            continue

                else:
                    img_link = ""
                data.append(img_link)
                datalist.append(data)

        # 设置休眠，每爬10条休息1，10秒随机时间
        t = random.uniform(1, 10)
        time.sleep(t)
        # 仪表盘：
        print("Extracting information from the %d0~%d0th site，then sleep %f seconds" % (m, n, t))

    return datalist


# 2 请求获取网页的方法。创建列表：搜集到常用headers，随机选择以应对403封禁
def askURL(url):
    errorpages = []
    my_headers = [
        "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36",
        "Mozilla / 5.0(Macintosh;Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"]
    # 用户代理，表示告诉服务器，我们是什么浏览器，本质是告诉浏览器，我们可以接受什么水平的内容
    head = {"User-Agent": random.choice(my_headers)}
    request = urllib.request.Request(url, headers=head)
    try:
        response = urllib.request.urlopen(request, timeout=5)
        html_list = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        else:
            print("Time out")
        errorpages.append(url)
        print("-----WARNING A ERROR PAGE-----")
        print(errorpages)
        html_list = ""

    return html_list


# 2.1解析获取到的详情页，拿到政策来源返回1.
def getSource(source_page):
    source_list = re.findall(findSource, str(source_page))
    source = "来源：" + "".join(source_list)
    return source


# 2.2解析获取到详情页，不带格式的data传回1.
def getPureWord(item_1):
    pure_word = item_1.find_all('p')
    result = [p.get_text() for p in pure_word]
    p_word = "".join(result)  # 使用join方法，分隔符为空
    return p_word


# 2.3解析获取到的详情页，把文件地址传回1.
def getFileLink(item_1):
    file_link = re.findall(findFileLink, str(item_1))
    f_link = "".join(file_link)
    suffix = ("doc", "pdf")
    if f_link.endswith(suffix):
        return f_link
    else:
        return ""


# 2.4解析获取到的详情页，把文件名传回2.1
def getFileName(item_1):
    file_link = re.findall(findFileLink, str(item_1))
    f_link = "".join(file_link)
    file_name = re.findall(findFileName, f_link)
    f_name = "".join(file_name)
    return f_name


# 2.5解析获取到的详情页，把图片地址传回2.1，图片可能有多个，因此直接在此方法里拼接完整URL，再返回2.1
def getImgUrl(item_1, pre_url):
    img_link_list = re.findall(findImgLink, str(item_1))
    img_url_list = [pre_url + str(i) for i in img_link_list]
    img_url = "".join(img_link_list)
    suffix = "jpg"
    if img_url.endswith(suffix):
        return img_url_list
    else:
        return []


# 2.6解析获取到的详情页，把图片名字传回2.1，图片可能有多个，但是只需要第一张图片完整名字即可，后面在下载的时候循环添加名字就行
def getImgName(item_1, titles):
    img_link = re.findall(findImgLink, str(item_1))
    if len(img_link) != 0:
        img_link_1 = img_link[0]
        img_last_name_1_list = re.findall(findImgName, img_link_1)
        img_last_name_1 = "".join(img_last_name_1_list)
        img_name_1 = titles + img_last_name_1
    else:
        img_name_1 = ""
    return img_name_1


# 3、保存数据到数据库
def saveData2DB(datalist, db_path):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    print("连接数据库成功，开始保存")
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            if index == 5 or index == 6:  # 带格式的详情和不带格式的详情加三引号，防止文本中出现单双都用导致保存失败
                data[index] = "'''" + data[index] + "'''"
            else:
                data[index] = "'" + data[index] + "'"  # 其他单引号即可
            sql = '''
            insert into policy(title,pub_date,summary,url,source,fdetail,pdetail,havefile,haveimg)
            values(%s)''' % ",".join(data)
            try:
                cur.execute(sql)
                conn.commit()
            except sqlite3.OperationalError:
                continue

    cur.close()
    print("保存成功")
    conn.close()


def init_db(db_path):
    sql = '''
        create table policy
        (
          id integer primary key autoincrement,
          title varchar,
          pub_date varchar ,
          summary varchar,
          url varchar,
          source varchar ,
          fdetail varchar ,
          pdetail varchar ,
          havefile varchar,
          haveimg varchar 
        )'''

    # 创建数据表
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":  # 当程序执行时# 调用函数
    main()

    print("Extraction Finished")
