from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from search_engine.settings import es
import re
import math
# Create your views here.

field_boost = {"url":2, "title":2, "anchor_text":2, "content":1}

def get_standard_data(res, username=None, count=20):
    def get_len(vec):
        sum = 0
        for v in vec["terms"].values():
            sum += v["term_freq"] * v["term_freq"]
        return math.sqrt(sum)
    
    def get_inner_product(vec1, vec2):
        sum = 0
        for key,value in vec1["terms"].items():
            if key in vec2["terms"].keys():
                sum += value["term_freq"] * vec2["terms"][key]["term_freq"]
        return sum / (vec1["len"] * vec2["len"])

    pages = res['hits']['hits']
    data = []
    # 查找与之最相关的count个文档
    for index, page in enumerate(pages):
        try:
            url_text = page["highlight"]["url"][0]
        except:
            url_text = page["_source"]["url"]
        try:
            title = page["highlight"]["title"][0]
        except:
            title = page["_source"]["title"]
        try:
            content = " ".join(page["highlight"]["content"])
        except:
            content = page["_source"]["content"]
            if len(content) > 500:
                content = content[:500]
        info = {
            "id": page["_id"],
            "url_text": url_text,
            "url": page["_source"]["url"],
            "title": title,
            "content": content,
            "score": page["_score"],
            "page_rank": page["_source"]["page_rank"],
        }
        data.append(info)
        if index > count:
            break
    recommand = []
    if username == None:
        return data, recommand
    # 如果有用户名，查找该用户的历史记录
    with open('name_passwd.json', "r+", encoding='utf-8') as f:
        info = json.load(f)
    history = None
    for i in info:
        if i["name"] == username:
            history = i["history"]
            break
    if history == None or len(history) == 0:
        return data, recommand
    # 按照与用户历史记录文档的相关性排序
    # 1) 构建历史记录文档的向量
    history_terms = []
    tv_query = {
        "fields" : ["content"],
        "offsets" : False,
        "payloads" : False,
        "positions" : False,
        "term_statistics" : False,
        "field_statistics" : False
    }
    for entry in history:
        tv = es.termvectors(index="index", id=entry, body=tv_query)
        tvt = tv["term_vectors"]["content"]
        tvt["len"] = get_len(tvt)
        history_terms.append(tvt)
    # 2) 构建文档的向量，计算内积
    for info in data:
        tv = es.termvectors(index="index", id=info["id"], body=tv_query)
        tvt = tv["term_vectors"]["content"]
        tvt["len"] = get_len(tvt)
        inner = [get_inner_product(tvt, i) for i in history_terms]
        info["sims"] = max(inner)
    # data.sort(key=lambda x:x["sims"], reverse=True)
    sort_weight = {"score":0.4, "page_rank":0.4, "sims": 0.2}
    for key in sort_weight.keys():
        max_value = max(data, key=lambda x:x[key])[key]
        min_value = min(data, key=lambda x:x[key])[key]
        for entry in data:
            if max_value == min_value:
                entry[key + "_standard"] = 1
            else:
                entry[key + "_standard"] = (entry[key] - min_value) / (max_value - min_value)
    for entry in data:
        entry["weighted_score"] = 0
        for key, value in sort_weight.items():
            entry["weighted_score"] += entry[key+"_standard"] * value
    data.sort(key=lambda x:x["weighted_score"], reverse=True)
    
    # 获取推荐结果
    recommand = get_recommend_data(history)
    return data, recommand

def get_recommend_data(history):
    likes = []
    for i in history:
        likes.append({"_index": "index", "_id": i})
    query = {
        "query": {
            "more_like_this": {
                "fields": ["content"],
                "like": likes,
                "min_term_freq": 1,
                "max_query_terms": 10
            }
        },
        "_source": {
            "excludes": ["content"]
        }
    }
    # print("相关查询：", query)
    res = es.search(index='index', body=query)
    # print("recommend: ", res)
    data = res["hits"]["hits"]
    recommend = []
    for i in  data:
        recommend.append({"id": i["_id"], "url": i["_source"]["url"], "title":  i["_source"]["title"]})
    return recommend

def search_index(request):
    return render(request,'index.html')

def search_detail(request, method='GET'):
    key = request.GET.get('key')
    username = request.GET.get('username')
    if key == None:
        key = ""
        return render(request,'search.html',{'key':key, "data":[], "more":[]})
    query = {
        "query": {
            "multi_match": {
                "query":key,
                "fields":[
                    f"url^{field_boost['url']}",
                    f"title^{field_boost['title']}",
                    f"content^{field_boost['content']}",
                    f"anchor_text^{field_boost['anchor_text']}"
                ]
            }
        },
        "highlight": {
            "pre_tags" : ["<font color='red'>"],
            "post_tags" : ["</font>"],
            "fields" : {
                "title" : {},
                "url" : {},
                "content" : {}
            }
        },
        "from": 0,
        "size": 30,
    }
    res = es.search(index='index', body=query)
    data, recommend = get_standard_data(res, username)
    return render(request,'search.html',{'key': key, "data": data, "more": recommend})

def search_advance(request, method='POST'):
    data = {}
    # print(request.POST)
    data["username"] = request.POST.get("username")
    data["key"] = request.POST.get("key")
    data["site"] = request.POST.get("site")
    data["queryType"] = request.POST.get("queryType")
    data["field"] = request.POST.getlist("field[]")
    if data["queryType"] == "bool":
        data["boolFilter"] = {}
        data["boolFilter"]["must"] = request.POST.get("boolFilter[must]").split()
        data["boolFilter"]["must_not"] = request.POST.get("boolFilter[must_not]").split()
        data["boolFilter"]["should"] = request.POST.get("boolFilter[should]").split()
    # print(data)
    # 查询搜索引擎，查找相关内容
    query = {
        "query": {
            "multi_match": {
                "query": data["key"],
                "fields":[i+"^"+str(field_boost[i]) for i in data["field"]]
            }
        },
        "highlight": {
            "pre_tags" : ["<font color='red'>"],
            "post_tags" : ["</font>"],
            "fields" : {
                "title" : {},
                "url" : {},
                "content" : {}
            }
        },
        "from": 0,
        "size": 30,
    }
    if data["queryType"] == "match_phrase":
        query["query"] = {"bool":{"should":[]}}
        for field in data["field"]:
            query["query"]["bool"]["should"].append({"match_phrase": {field:data["key"]}})
    elif data["queryType"] == "bool":
        query["query"] = {"bool":{}}
        boolFilter = data["boolFilter"]
        for key,values in boolFilter.items():
            if len(values) != 0:
                query["query"]["bool"][key] = []
                for value in values:
                    for field in data["field"]:
                        query["query"]["bool"][key].append({"match_phrase": {field:value}})
    print(query)
    res = es.search(index='index', body=query)
    ret, recommend = get_standard_data(res, data["username"])
    # print("搜索结果：", ret)
    if data["site"] != "":
        ret = list(filter(lambda x:re.match(data["site"] + ".*", x["url"]), ret))
    # 返回数据
    # res = []
    # testEntry = {
    #     "id": 1,
    #     "url": "http://aaa",
    #     "url_text": "http://aaa",
    #     "title": "今天开始我要自己上厕所",
    #     "content": "今天开始我要自己上厕所，爸爸妈妈你们不要小看我",
    #     "score": 1.11111111111,
    #     "page_rank": 0.0111
    # }
    # res.append(testEntry)
    return JsonResponse({"code":0, "data":ret, "more":recommend})