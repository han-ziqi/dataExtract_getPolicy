#-*- codeing = utf-8 -*-
#@Time : 2021/1/12 4:13 下午
#@Author : Han
#@File : testUrllib.py
#@Software : PyCharm

import urllib.request
# response = urllib.request.urlopen("http://sousuo.gov.cn/s.htm?q=&t=zhengcelibrary")
# print(response.read().decode("utf-8"))
'''
url = "http://sousuo.gov.cn/data?t=zhengcelibrary_or&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=title&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&p=0&n=10&inpro=&bmfl=&dup=&orpro="
headers = { "User-Agent": "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36"}
req = urllib.request.Request(url= url, headers=headers)
response = urllib.request.urlopen(req)
print(response.read().decode("utf-8"))
'''
url = "http://www.gov.cn/zhengce/2021-01/12/content_5579195.htm"
headers = { "User-Agent": "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_2) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 87.0.4280.88Safari / 537.36"}
req = urllib.request.Request(url= url, headers=headers)
response = urllib.request.urlopen(req)
print(response.read().decode("utf-8"))