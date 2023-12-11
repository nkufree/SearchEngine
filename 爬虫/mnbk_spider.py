from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import quote,unquote
import requests
import re
import time
import os
import csv
import json
import pickle
import random
maxSpiderTime = 100000
service = Service("G:\Python\edgedriver_win64\msedgedriver.exe")
options = webdriver.EdgeOptions()
options.add_argument("headless")
driver = webdriver.Edge(service=service,options=options)
driver.set_page_load_timeout(3)
driver.set_script_timeout(3)

request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
    "Connection": "keep-alive",
}
# url = "https://mzh.moegirl.org.cn/index.php?title=Special%3ARandom&utm_source=moe_homeland"
# "https://mzh.moegirl.org.cn/index.php?utm_medium=simple_list&title=Template%3AACG%E7%A4%BE%E5%9B%A2&utm_source=moe_homeland",
url = ["https://mzh.moegirl.org.cn/index.php?utm_medium=simple_list&title=Template%3AGalgame%E5%85%AC%E5%8F%B8&utm_source=moe_homeland","https://mzh.moegirl.org.cn/index.php?utm_medium=simple_list&title=Template%3A%E5%8A%A8%E7%94%BB%E5%85%AC%E5%8F%B8&utm_source=moe_homeland"]
url_info = {}
urls_not_found = set()
urls_company = set()
urls_falid = set()
urls_pages = set()
sleepTime = 0
# 第一次爬取：爬取GalGame、ACG和动画公司信息
def first_spider():
    for i in url:
        try:
            getPage = False
            while not getPage:
                try:
                    driver.get(url=i)
                except:
                    time.sleep(sleepTime)
                link_elements = driver.find_elements(By.TAG_NAME,"a")
                if len(link_elements) != 0:
                    getPage = True
            for link in link_elements:
                link_href = link.get_attribute("href")
                if link_href == None or link_href == '':
                    continue
                one_url = unquote(link_href)
                if one_url[0] == '/':
                    one_url = "https://mzh.moegirl.org.cn" + one_url
                try:
                    resp = requests.get(url=one_url,headers=request_headers)
                except:
                    continue
                if not resp.status_code == 200:
                    urls_not_found.add(one_url)
                    continue
                urls_company.add(one_url)
                if one_url in url_info.keys():
                    url_info[one_url]["anchor_text"].add(link.text.strip())
                else:
                    url_info[one_url] = {}
                    url_info[one_url]["url"] = one_url
                    url_info[one_url]["anchor_text"] = set()
                    url_info[one_url]["title"] = ""
                    url_info[one_url]["page"] = 0
        except:
            continue

# 第二次爬虫：获取各个公司作品的url，爬取公司的页面
def second_spider(urls, add_link=True, store_link=False):
    sleepTime = 0
    for i in urls:
        try:
            try:
                driver.get(url=i)
            except:
                time.sleep(sleepTime)
                if i not in url_info.keys():
                    url_info[i] = {}
                    url_info[i]["url"] = i
                    url_info[i]["anchor_text"] = set()
                    url_info[i]["title"] = ""
                    url_info[i]["page"] = 0
                # 获取标题信息
                url_info[i]["title"] = driver.find_element(By.TAG_NAME,"h1").text
                # 获取页面内容并写入文件
                try:
                    content = driver.find_element(By.CSS_SELECTOR,'#mw-body')
                    sleepTime = 0
                except:
                    urls_falid.add(i)
                    sleepTime += 1
                    continue
                timeNow = int(time.mktime(time.localtime(time.time())))
                with open('spider_pages/' + str(timeNow), 'w', encoding='utf-8') as f:
                    f.write(content.text)
                url_info[i]["page"] = timeNow
                if store_link:
                    with open("spider_pages/" + str(timeNow) + "_to_link", 'w', encoding='utf-8') as f:
                        for link in driver.find_elements(By.TAG_NAME,"a"):
                            try:
                                link_href = link.get_attribute("href")
                            except:
                                continue
                            if link_href == None or link_href == '':
                                continue
                            one_url = unquote(link_href)
                            f.write(one_url)
                            f.write('\n')
                if not add_link:
                    continue
                for link in driver.find_elements(By.TAG_NAME,"a"):
                    link_href = link.get_attribute("href")
                    if link_href == None or link_href == '':
                        continue
                    one_url = unquote(link_href)
                    if one_url[0] == '/':
                        one_url = "https://mzh.moegirl.org.cn" + one_url
                    # 如果是无法获取或者公司的链接，则continue
                    if one_url in urls_not_found or one_url in urls_company:
                        continue
                    urls_pages.add(one_url)
                    if one_url in url_info.keys():
                        url_info[one_url]["anchor_text"].add(link.text.strip())
                    else:
                        url_info[one_url] = {}
                        url_info[one_url]["url"] = one_url
                        url_info[one_url]["anchor_text"] = set()
                        url_info[one_url]["title"] = ""
                        url_info[one_url]["page"] = 0
        except:
            continue


import re
# 加上action=raw，爬取源文件
def second_spider_raw(urls, add_link=True, store_link=False, over_write = False):
    sleepTime = 0
    for i in urls:
        try:
            split_url = re.split('[#?&]', i)
            resp = requests.get(url=split_url[0] + "?action=raw",headers=request_headers)
            content = resp.text
            sleepTime = 0
        except:
            urls_falid.add(i)
            sleepTime += 1
            continue
        if resp.status_code != 200:
            continue
        if not over_write:
            if i in url_info.keys() and url_info[i]["page"] != 0:
                continue
        try:
            try:
                driver.get(url=i)
            except:
                time.sleep(sleepTime)
                if i not in url_info.keys():
                    url_info[i] = {}
                    url_info[i]["url"] = i
                    url_info[i]["anchor_text"] = set()
                    url_info[i]["title"] = ""
                    url_info[i]["page"] = 0
                # 获取标题信息
                url_info[i]["title"] = driver.find_element(By.TAG_NAME,"h1").text
                timeNow = int(time.mktime(time.localtime(time.time())))
                with open('spider_pages/' + str(timeNow), 'w', encoding='utf-8') as f:
                    f.write(content)
                url_info[i]["page"] = timeNow
                if store_link:
                    with open("spider_pages/" + str(timeNow) + "_to_link", 'w', encoding='utf-8') as f:
                        for link in driver.find_elements(By.TAG_NAME,"a"):
                            try:
                                link_href = link.get_attribute("href")
                            except:
                                continue
                            if link_href == None or link_href == '':
                                continue
                            one_url = unquote(link_href)
                            res = re.split('[#?&]', one_url)
                            f.write(res[0])
                            f.write('\n')
                if not add_link:
                    continue
                for link in driver.find_elements(By.TAG_NAME,"a"):
                    link_href = link.get_attribute("href")
                    if link_href == None or link_href == '':
                        continue
                    one_url = unquote(link_href)
                    if one_url[0] == '/':
                        one_url = "https://mzh.moegirl.org.cn" + one_url
                    res = re.split('[#?&]', one_url)
                    one_url = res[0]
                    # 如果是无法获取或者公司的链接，则continue
                    if one_url in urls_not_found or one_url in urls_company:
                        continue
                    urls_pages.add(one_url)
                    if one_url in url_info.keys():
                        url_info[one_url]["anchor_text"].add(link.text.strip())
                    else:
                        url_info[one_url] = {}
                        url_info[one_url]["url"] = one_url
                        url_info[one_url]["anchor_text"] = set()
                        url_info[one_url]["title"] = ""
                        url_info[one_url]["page"] = 0
        except:
            continue

# 随机页面爬虫
def random_spider():
    f = open('url_page.csv','a+',encoding='utf-8', newline="")
    csv_writer = csv.writer(f)
    # csv_writer.writerow(["url", "page"])
    for i in url:
        try:
            driver.get(url=url)
        except:
            1
        time.sleep(sleepTime)
        try:
            content = driver.find_element(By.CSS_SELECTOR,'#mw-body')
            sleepTime = 0
        except:
            sleepTime += 1
            continue
        timeNow = int(time.mktime(time.localtime(time.time())))
        csv_writer.writerow([unquote(driver.current_url), timeNow])
        f.flush()
        with open('pages/' + str(timeNow), 'w', encoding='utf-8') as ff:
            ff.write(content.text)
    f.close()

if __name__ == '__main__':
    # first_spider()
    with open("page_info.json", "r", encoding='utf-8') as f:
        url_info = json.load(f)
        for key,value in url_info.items():
            url_info[key]["anchor_text"] = set(value["anchor_text"])
    
    with open("urls_company.pk","rb") as f:
        urls_company = pickle.load(f)
    
    with open("urls_not_found.pk", "rb") as f:
        urls_not_found = pickle.load(f)
    
    with open("urls_pages.pk", "rb") as f:
        urls_pages = pickle.load(f)
    
    # second_spider(urls_company)
    # second_spider(urls_falid)
    testpage = random.choice(list(urls_pages))
    second_spider_raw(["https://mzh.moegirl.org.cn/YUZU_SOFT"], add_link=True, store_link=True)
    
    with open("page_info.json", "w", encoding='utf-8') as f:
        for key,value in url_info.items():
            url_info[key]["anchor_text"] = list(value["anchor_text"])
        json.dump(url_info, f, indent=4, ensure_ascii=False)
        for key,value in url_info.items():
            url_info[key]["anchor_text"] = set(value["anchor_text"])
    
    with open("urls_pages.pk", "wb") as f:
        pickle.dump(urls_pages, f)
    # with open("page_info.txt", "w") as f:
    #     json.dump(url_info, f)
    # with open("page_info.txt", "r") as f:
    #     url_info = json.load(f)
    # second_spider(urls_pages, False)
    