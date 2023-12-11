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

request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
    "Connection": "keep-alive",
}
# url = "https://mzh.moegirl.org.cn/index.php?title=Special%3ARandom&utm_source=moe_homeland"
url = ["https://mzh.moegirl.org.cn/index.php?utm_medium=simple_list&title=Template%3AGalgame%E5%85%AC%E5%8F%B8&utm_source=moe_homeland","https://mzh.moegirl.org.cn/index.php?utm_medium=simple_list&title=Template%3A%E5%8A%A8%E7%94%BB%E5%85%AC%E5%8F%B8&utm_source=moe_homeland"]
url_info = {}
urls_not_found = set()
urls_company = set()
urls_falid = set()
urls_pages = set()
sleepTime = 0

with open("page_info.json", "r", encoding='utf-8') as f:
    url_info = json.load(f)
    for key,value in url_info.items():
        url_info[key]["anchor_text"] = set(value["anchor_text"])


page_name = "1701510973"
# m = shutil.copy("spider_pages/" + page_name, "new_pages/" + page_name)

try:
    with open("spider_pages/" + page_name + "_to_link", "r", encoding='utf-8') as f:
        to_urls = f.readlines()
except:
    with open("page_link/" + page_name, "w", encoding='utf-8') as f:
        m = json.dump([], f, indent=4, ensure_ascii=False)

to_urls_new = set()
for i in to_urls:
    res = re.split('[#?&]', i)
    add_url = res[0].strip()
    if add_url in url_info.keys() and add_url != "https://mzh.moegirl.org.cn/index.php":
        to_urls_new.add(add_url)

with open("page_link/" + page_name, "w", encoding='utf-8') as f:
    m = json.dump(list(to_urls_new), f, indent=4, ensure_ascii=False)