# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
2014/5/23将格式转换全部放置在本模块
Create:2014/5/21
"""
import sys
import traceback
import logging
from hashlib import sha1 as _sha1
from binascii import unhexlify as _unhexs
from xml.etree.ElementTree import fromstring

from .event import *
from .WXError import *

if sys.version_info.major == 2:
    from urllib import (quote, unquote, urlencode as url_encode)
if sys.version_info.major == 3:
    from urllib.parse import (quote, unquote, urlencode as url_encode)

__all__ = ['url_decode', 'url_encode', 'quote', 'unquote', 'auth_signature', 'xml2event']


def url_decode(query, encoding="utf-8"):
    """`url_encode` 的反操作, 正确与否均返回dict,若不会符合则返回空的`dict`"""
    try:
        result = dict()
        parts = query.decode(encoding).split('&')
        for part in parts:
            if part.find('='):
                k, v = map(unquote, part.split('='))
                result.update({k: v})
        return result
    except Exception as e:
        traceback.print_exc()
        logging.error("`url_decode` error:: request is {query}".format(query=query))
        logging.error("处理微信请求认证时出错:::{err}".format(err=e))
        return dict()


def auth_signature(auth_token, args, encoding="utf-8"):
    # type: (str, dict) -> bool
    """timestamp, nonce [echostr] 正确返回 True;错误/失败返回 False"""
    try:
        sign_parm = [auth_token]
        for i in ('timestamp', 'nonce'):
            sign_parm.append(args[i])
        sign_parm.sort()
        client_sign = _unhexs(args['signature'])
        server_sign = _sha1(''.join(sign_parm).encode(encoding)).digest()
        if client_sign == server_sign:
            return True
        else:
            return False
    except (KeyError, TypeError, AttributeError) as e:
        traceback.print_exc()
        logging.warn("验证失败!参数格式不符合要求:[{args}]:::{error}".format(args=args, error=e))
        return False


def xml2json(xml_data, encoding="utf-8"):
    # type: (str, str) -> dict
    result = dict()
    _add = result.update
    try:
        mxml = fromstring(xml_data)
        for node in mxml:
            _add({node.tag: node.text})
        return result
    except Exception as e:
        traceback.print_exc()
        logging.error("错误POST数据:[%s]" % xml_data.decode(encoding))
        logging.error("请求的xml数据格式不正确或不完整无法处理![%s]" % str(e))
        raise WXApiError("请求方提供的XML数据格式不正确")


def xml2event(xml_data, encoding="utf-8"):
    # type:(bytes, str)-> dict
    """入参需要是utf8编码,将xml转换为 dict,出错抛出 WXError"""
    result = xml2json(xml_data, encoding)

    msg_type = result.get('MsgType')
    if 'MsgId' in result:  # 消息
        if 'text' == msg_type:
            return TextMsg(result)
        elif 'image' == msg_type:
            return ImageMsg(result)
        elif 'voice' == msg_type:
            return VoiceMsg(result)
        elif 'video' == msg_type:
            return VideoMsg(result)
        elif 'link' == msg_type:
            return LinkMsg(result)
        elif 'location' == msg_type:
            return LocationMsg(result)
        else:
            logging.warn("未知的消息类型:[%s]" % xml_data.decode('utf8'))
            raise WXApiError("UnKnown Message Type")
    else:  # 事件或新增其他
        event = result.get('Event')
        if 'event' == msg_type:
            if 'location' == event:  #
                return LocationEvent(result)
            if 'subscribe' == event:
                return SubEvent(result)
            elif 'unsubscribe' == event:
                # logging.info("取消订阅")
                return UnSubEvent(result)
            elif 'scan' == event:  # 二维码扫描
                # logging.info("用户二维码扫描")
                return ScanEvent(result)
            elif 'click' == event:  # 自定义菜单
                # logging.info("用户点击菜单按键")
                return ClickEvent(result)
            elif 'view' == event:  # 跳转到预设的地址
                # logging.info("用户点击菜单链接")
                return ViewEvent(result)
            else:
                # logging.warn("未知的事件类型:[%s]" % xml_data.decode('utf8'))
                raise WXApiError("UnSupport Event Type")
        else:
            # logging.warn("未知的新增类型:[%s]" % xml_data.decode('utf8'))
            raise WXApiError("UnKnown Message Type or Event")
