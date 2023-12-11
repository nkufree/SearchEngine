from django.shortcuts import render, redirect, resolve_url
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.conf import settings
import django.core.handlers.wsgi
from django.contrib import messages
import csv
import time
import pandas as pd
import os
import random
import json


# Create your views here.
# 处理用户登录
def login(request,method=['GET', 'POST']):
    assert isinstance(request,django.core.handlers.wsgi.WSGIRequest)
    if request.method == "GET":
        return render(request,'login.html')
    action = request.POST.get('action')
    name = request.POST.get('name')
    password = request.POST.get('password')
    # print(name,password)
    if action == "login":
        with open('name_passwd.json', "r+", encoding='utf-8') as f:
            data = json.load(f)
            for i in data:
                if i["name"] == name and i["password"] == password:
                    request.session["username"] = name
                    return redirect('/index')
        messages.error(request,'用户名或密码错误')
        return render(request,'login.html')
    elif action == "signup":
        with open('name_passwd.json', "r+", encoding='utf-8') as f:
            data = json.load(f)
            for i in data:
                if i["name"] == name:
                    return JsonResponse({"code":-1})
        data.append({"name": name, "password": password, "history": []})
        with open('name_passwd.json', "w+", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return JsonResponse({"code":0})

def user_manage(request, method='POST'):
    name = request.POST.get("name")
    action = request.POST.get("action")
    if action == "add_history":
        id = request.POST.get("history")
        print({"name":name, "action":action, "doc_id": id})
    with open('name_passwd.json', "r+", encoding='utf-8') as f:
        data = json.load(f)
    for i,value in enumerate(data):
        if value["name"] == name:
            data[i]["history"].append(id)
            if len(data[i]["history"]) > 5:
                data[i]["history"] = data[i]["history"][1:]
            break
    with open('name_passwd.json', "w+", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return JsonResponse({"code":0})
