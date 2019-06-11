# WXAPI


WXApi 是一个基于微信公众号平台API文档开发的一个
![Python](https://pypi.python.org/static/images/python-logo.png)服务接口

用于将微信服务号请求的消息（事件）转换为一个类对象，
更简单的属性，更容易的操作
> 版本支持
> * 2.6 
> * 2.7 
> * 3.x

## 状态
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)
[![PyPI](https://img.shields.io/badge/PyPi-download-brightgreen.svg?style=flat-square)](https://pypi.python.org/pypi/pyweipi/1.0.1)
[![release](https://img.shields.io/badge/release-v1.0.1--beta-green.svg?style=flat-square)]()
[![Licence](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/kedyy/pyweipi/LICENSE)


## 安装
```bash
$pip install pyweipi
```

## 案例
一个基于flask的 请求处理demo
```python
# -*- coding: utf-8 -*-
from WXApi import *
from flask import Flask, Response, request
app = Flask(__name__)

BASE_URL = '/wechatrequest'
BASE_TOKEN = 'wechatrequest'


def service_route(ask):
    # type: (WeChatObject) -> ReplyObject
    if isinstance(ask, ImageMsg):
        return ImageReply(ask, ask.media_id)

    if isinstance(ask, VoiceMsg):
        ques = "{0}".format(ask.recognition)
        return VoiceReply(ask, ask.media_id)

    if isinstance(ask, TextMsg):
        msg = ask.content
        return TextMsg(ask)

    if isinstance(ask, LinkMsg):
        return NewsReply(ask, title=ask.title, desc=ask.description, 
        picture_url='',link=ask.link)

    if isinstance(ask, SubEvent):
        return TextReply(ask, "欢迎关注")
    
    if isinstance(ask, UnSubEvent):
        return EmptyReply(ask)

    return TextReply(ask, "我不懂你在说什么才是最大的痛吧 😪")


# 用于处理微信的数据请求
@app.route(BASE_URL, methods=['GET', 'POST'])
def app_main():
    query = url_decode(request.query_string)
    # 认证是否是微信的合法请求
    if auth_signature(BASE_TOKEN, query):
        if 'echostr' in query:
            return Response(query.get('echostr'), 200)
    else:
        return Response(status=401)
    if 'POST' != request.method:
        return Response(status=400)
    # 认证成功,处理POST数据
    try:
        json_req = xml2event(request.data)
        res_data = service_route(json_req).create_xml() + ""
    except Exception as e:
        return Response(status=200)
    else:
        return Response(res_data, 200)
```

## 许可
The MIT License

