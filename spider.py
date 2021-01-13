#-*- codeing = utf-8 -*-
#@Time : 2021/1/12 3:48 下午
#@Author : Han
#@File : spider.py
#@Software : PyCharm

import json
import re  # 正则表达式进行文字匹配
import urllib.request, urllib.error  # 指定url获取网页数据
import xlwt  # 进行Excel操作
import sqlite3 # 进行SQlite数据库操作




def main():
    baseurl = "http://sousuo.gov.cn/data?t=zhengcelibrary_or&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=title&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&p="

    # 1、爬取网页
    datalist = getData(baseurl)
    savepath = "政策解读.xls"
    # dbpath = "movie.db"
    # 3、保存数据
    saveData(datalist, savepath)
    # saveData2DB(datalist, dbpath)

# findTitle = re.compile(r"title:""(\d+)")

# 1、爬取网页
def getData(baseurl):
    datalist = []

    for i in range(-1, 9):  # 设置循环，i从0到100，每页10条
        url = baseurl + str(i + 1) + str("&n=10&inpro=&bmfl=&dup=&orpro=")
        htmlJson = askURL(url)  # 保存获取到的json对象
        # print(htmlJson)
        # print("__________-------------------------")



# 2、逐一解析数据
        htmldict = json.loads(htmlJson) #将json对象转换为python字典
        v0 = htmldict.get("searchVO").get('listVO')
        for item in v0:
            data = []  # 新建列表来存放一条政策内容

            titles = item.get('title')
            data.append(titles)

            time = item.get('pubtimeStr')
            data.append(time)

            summary =item.get('summary')
            data.append(summary)

            url = item.get('url')
            data.append(url)

            datalist.append(data)
        print(datalist)





    return datalist

# 得到指定一个URL的网页内容
def askURL(url):
    # 用户代理，表示告诉服务器，我们是什么浏览器，本质是告诉浏览器，我们可以接受什么水平的内容
    head = { "User-Agent": "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36"}
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html



# 3、保存数据
def saveData(datalist,savapath):
    print("开始储存数据")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet("政策解读",cell_overwrite_ok=True)  # 创建工作表
    col = ("政策标题", "政策发布时间", "政策摘要","政策链接")
    for i in range(0, 4):
        sheet.write(0, i, col[i]) #列名
    for i in range(0, 100):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,4):
            sheet.write(i+1,j,data[j])  #数据

    book.save(savapath)


'''
# 4、保存数据到数据库
def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index ==4 or index ==5:             #分数、评价人数不用加引号
                continue
            data[index] = '"'+data[index]+'"'  #作用：把每一个内容都加上双引号
'''
        # sql = '''
        # insert into movie250(
        # info_link,pic_link,cname,ename,score,rated,introduction,info)
        # values(%s)'''%",".join(data)
'''
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):
    # sql = '''
    #     create table movie250
    #     (
    #       id integer primary key autoincrement,
    #       info_link text,
    #       pic_link text,
    #       cname varchar,
    #       ename varchar,
    #       score numeric ,
    #       rated numeric ,
    #       introduction text,
    #       info text
    #     )'''
'''
    #创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
'''
if __name__ == "__main__":  # 当程序执行时# 调用函数
    main()
    print("爬取完毕")