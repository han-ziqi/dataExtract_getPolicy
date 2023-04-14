## README

I developed this data extraction program that is designed to extract valuable information from [a policy announcement website](http://sousuo.gov.cn/s.htm?t=zhengcelibrary&q=). This program is capable of navigating each sub-item and saving the extracted data. In just one complete run, it can save up to 7,000 pieces of data, and it takes only about 85 minutes to complete (based on early 2021 statistics). The program utilizes **Python**,and **SQLite database management system** to automate the data extraction process.

When running, a [SQLite](https://sqlite.org/index.html) database will be created and the content will be stored by id, article title, post date, abstract, url, body, attachments. If the text contains any attachments, the program will also download the attachments automatically.

#### Here is a demo when running

![demo](https://github.com/han-ziqi/getPolicy/raw/master/demo/demo%20for%20policy.png)

---



## How to run policy.py

**The program can be run directly after cloning to local (early 2021) **

This program has been developed for the [specific site](http://sousuo.gov.cn/s.htm?t=zhengcelibrary&q=).  If you change to another site, there is no guarantee that the subsequent analysis and saving functions will work properly.

If you wish to change to another site for extraction, please follow:

1. Replace the parameter of **base_url** in line 33
2. Change the range of **range()** on line 43, and -1 is the first page by default
3. The save to database section starting at line 229 **requires major changes** because errors can occur when the stored data does not match the database structure, so it is advisable to observe the extracted content before making specific changes.

