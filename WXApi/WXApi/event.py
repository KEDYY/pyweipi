# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import time
import warnings

__date__ = "2017/11/22"

__all__ = ['TextMsg', 'ImageMsg', 'VoiceMsg', 'VideoMsg', 'LocationMsg', 'LinkMsg',
           'SubEvent', 'UnSubEvent', 'ScanEvent', 'ClickEvent', 'ViewEvent', 'LocationEvent',
           'ReplyObject', 'EmptyReply', 'TextReply', 'ImageReply', 'VoiceReply', 'VideoReply', 'MusicReply',
           'NewsReply']


class Msg(dict):
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None


class WeChatObject(object):
    def __init__(self, msg):
        super(WeChatObject, self).__init__()
        self.from_id = msg['FromUserName']
        self.to_id = msg['ToUserName']
        self.time = msg['CreateTime']


class WeChatMsg(WeChatObject):
    def __init__(self, msg):
        super(WeChatMsg, self).__init__(msg)
        self.type = msg['MsgType'].lower()
        self.message_id = msg['MsgId']

    def __eq__(self, other):
        return self.message_id == other.message_id

    def __contains__(self, item):
        return self.message_id == item.message_id


class WeChatMedia(WeChatMsg):
    def __init__(self, msg):
        super(WeChatMedia, self).__init__(msg)
        self.media_id = msg['MediaId']


class WeChatEvent(WeChatObject):
    def __init__(self, msg):
        super(WeChatEvent, self).__init__(msg)
        assert msg['MsgType'] == 'event', "不是事件类型"
        self.event = msg['Event'].lower()


class TextMsg(WeChatMsg):
    def __init__(self, msg):
        super(TextMsg, self).__init__(msg)
        assert self.type == 'text', "消息不是文本类型消息"
        self.content = msg['Content']


class VoiceMsg(WeChatMedia):
    def __init__(self, msg):
        super(VoiceMsg, self).__init__(msg)
        assert self.type == 'voice', "消息不是语音类型消息"
        self.format = msg['Format']
        self.recognition = msg.get('Recognition')  # 可以没有


class VideoMsg(WeChatMedia):
    def __init__(self, msg):
        super(VideoMsg, self).__init__(msg)
        assert self.type == 'video', "消息不是语音类型消息"
        self.thumb_media_id = msg['ThumbMediaId']


class ImageMsg(WeChatMedia):
    def __init__(self, msg):
        super(ImageMsg, self).__init__(msg)
        assert self.type == 'image', "消息不是语音类型消息"
        self.image_link = msg['PicUrl']


class LocationMsg(WeChatMsg):
    def __init__(self, msg):
        super(LocationMsg, self).__init__(msg)
        assert self.type == 'location', "消息不是定位类型消息"
        self.x = msg['Location_X']  # 地理位置纬度
        self.y = msg['Location_Y']  # 地理位置经度
        self.scale = msg['Scale']  # 地图缩放大小
        self.label = msg['Label']  # 地理位置信息


class LinkMsg(WeChatMsg):
    def __init__(self, msg):
        super(LinkMsg, self).__init__(msg)
        assert self.type == 'link', "消息不是链接类型消息"
        self.title = msg['Title']
        self.description = msg['Description']
        self.link = msg['Url']


class SubEvent(WeChatEvent):
    def __init__(self, msg):
        super(SubEvent, self).__init__(msg)
        assert self.event == 'subscribe', "不是订阅事件"
        self.event_key = msg.get('EventKey')
        self.ticket = msg.get('Ticket')
        if self.event_key is not None:
            assert self.ticket.startswith('qrscene_'), "不是二维码订阅事件"


class UnSubEvent(WeChatEvent):
    def __init__(self, msg):
        super(UnSubEvent, self).__init__(msg)
        assert self.event == 'unsubscribe', "不是取消订阅事件"


class ScanEvent(WeChatEvent):
    def __init__(self, msg):
        super(ScanEvent, self).__init__(msg)
        assert self.event == 'scan', "不是扫描事件"
        self.event_key = msg['EventKey']
        self.ticket = msg['Ticket']


class ClickEvent(WeChatEvent):
    def __init__(self, msg):
        super(ClickEvent, self).__init__(msg)
        assert self.event == 'click', "不是点击事件"
        self.event_key = msg['EventKey']


class ViewEvent(WeChatEvent):
    def __init__(self, msg):
        super(ViewEvent, self).__init__(msg)
        assert self.event == 'view', "不是跳转事件"
        self.event_key = msg['EventKey']


class LocationEvent(WeChatEvent):
    def __init__(self, msg):
        super(LocationEvent, self).__init__(msg)
        assert self.event == 'location', "不是定位事件"
        self.x = msg['Latitude']  # 地理位置纬度
        self.y = msg['Longitude']  # 地理位置经度
        self.scale = msg['Precision']  # 地理位置精度


class QASuccessEvent(WeChatEvent):
    """资质认证成功"""

    def __init__(self, msg):
        super(QASuccessEvent, self).__init__(msg)
        assert self.event == 'qualification_verify_success', "不是资质认证事件"
        self.valid_date = msg['ExpiredTime']


class QAFailedEvent(WeChatEvent):
    """资质认证失败"""

    def __init__(self, msg):
        super(QAFailedEvent, self).__init__(msg)
        assert self.event == 'qualification_verify_success', "不是资质认证事件"
        self.valid_date = msg['qualification_verify_fail']
        self.fail_time = msg['FailTime']
        self.fail_reason = msg['FailReason']


class NamingSuccessEvent(WeChatEvent):
    """名称认证成功（即命名成功）"""

    def __init__(self, msg):
        super(NamingSuccessEvent, self).__init__(msg)
        assert self.event == 'qualification_verify_fail', "不是资质认证事件"
        self.valid_date = msg['ExpiredTime']


class NamingFailedEvent(WeChatEvent):
    """名称认证失败"""

    def __init__(self, msg):
        super(NamingFailedEvent, self).__init__(msg)
        assert self.event == 'naming_verify_fail', "不是资质认证事件"
        self.valid_date = msg['qualification_verify_fail']
        self.fail_time = msg['FailTime']
        self.fail_reason = msg['FailReason']


class RemindEvent(WeChatEvent):
    """名称认证失败"""

    def __init__(self, msg):
        super(RemindEvent, self).__init__(msg)
        assert self.event == 'annual_renew', "不是年审提醒事件"
        self.valid_date = msg['ExpiredTime']


class NotifyEvent(WeChatEvent):
    """名称认证失败"""

    def __init__(self, msg):
        super(NotifyEvent, self).__init__(msg)
        assert self.event == 'verify_expired', "不是年审过期通知"
        self.valid_date = msg['ExpiredTime']


class WeChatXML(object):
    def __init__(self, root_name, encoding="utf-8"):
        self.encoding = encoding
        self.root = root_name
        self.node = list()

    def add_ele(self, tag, value):
        self.node.append((tag, value))

    def __str__(self):
        if sys.version_info.major == 3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode(sys.stdout.encoding)

    def __unicode__(self):
        unicode_buf = list()
        unicode_buf.append("" if (self.root is None) else "<{0}>".format(self.root))
        for tag, value in self.node:
            if tag is not None and type(value) is int:
                unicode_buf.append("<{tag}>{value}</{tag}>".format(tag=tag, value=value))
            elif tag is not None and value is not None:
                unicode_buf.append("<{tag}><![CDATA[{value}]]></{tag}>".format(tag=tag, value=value))
            elif tag is None and type(value) is int:
                unicode_buf.append("{0}".format(value))
            elif tag is None and type(value) is str:
                if sys.version_info.major < 3:
                    unicode_buf.append("{0}".format(value.decode(self.encoding)))
                else:
                    unicode_buf.append("{0}".format(value))
            elif tag is None and isinstance(value, type('')):
                unicode_buf.append(value)
            elif tag is None and isinstance(value, WeChatXML):
                unicode_buf.append(value.__unicode__())
            else:
                warnings.warn("unused node::: {tag}: {value}".format(tag=tag, value=value))
        unicode_buf.append("" if (self.root is None) else"</{0}>".format(self.root))
        return ''.join(unicode_buf)

    def __repr__(self):
        if sys.version_info.major == 3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode(self.encoding)

    def __add__(self, other):
        if not hasattr(other, '__unicode__'):
            return self.__unicode__()
        return self.__unicode__() + other.__unicode__()


class ReplyObject(object):
    def __init__(self, sender):
        super(ReplyObject, self).__init__()
        self.to_id = sender.from_id
        self.from_id = sender.to_id
        assert self.from_id is not None, "ToUserName is None"
        assert self.to_id is not None, "FromUserName is None"
        self.time = int(time.time())

    def _create_xml(self):
        root = WeChatXML("xml")
        root.add_ele("FromUserName", self.from_id)
        root.add_ele("ToUserName", self.to_id)
        root.add_ele("CreateTime", self.time)
        root.add_ele("MsgType", self.msg_type())
        root.add_ele(None, self.node())
        return root

    def __repr__(self):
        return repr(self._create_xml())

    def __str__(self):
        return str(self._create_xml())

    def create_xml(self):
        return repr(self._create_xml())

    def msg_type(self):
        raise NotImplementedError

    def node(self):
        raise NotImplementedError


class EmptyReply(ReplyObject):
    """当消息不需要回复或者后续以客服接口回复时返回一个空或者 Success 作为标识"""

    def __init__(self, sender):
        super(EmptyReply, self).__init__(sender)

    def create_xml(self):
        return "success"

    def node(self):
        pass

    def msg_type(self):
        pass


class TextReply(ReplyObject):
    def __init__(self, sender, msg):
        super(TextReply, self).__init__(sender)
        self.type = 'text'
        self.content = msg

    def msg_type(self):
        return self.type

    def node(self):
        node = WeChatXML(None)
        node.add_ele("Content", self.content)
        return node


class ImageReply(ReplyObject):
    def __init__(self, sender, media_id):
        super(ImageReply, self).__init__(sender)
        self.type = 'image'
        self.media_id = media_id

    def msg_type(self):
        return self.type

    def node(self):
        node = WeChatXML("Image")
        node.add_ele("MediaId", self.media_id)
        return node


class VoiceReply(ReplyObject):
    def __init__(self, sender, media_id):
        super(VoiceReply, self).__init__(sender)
        self.type = 'voice'
        self.media_id = media_id

    def msg_type(self):
        return self.type

    def node(self):
        node = WeChatXML("Voice")
        node.add_ele("MediaId", self.media_id)
        return node


class VideoReply(ReplyObject):
    def __init__(self, sender, media_id, title, desc):
        super(VideoReply, self).__init__(sender)
        self.type = 'video'
        self.media_id = media_id
        self.title = title
        self.description = desc

    def msg_type(self):
        return self.type

    def node(self):
        node = WeChatXML("Video")
        node.add_ele("MediaId", self.media_id)
        node.add_ele("Title", self.title)
        node.add_ele("Description", self.description)
        return node


class MusicReply(ReplyObject):
    def __init__(self, sender, title, desc, music_url, music_url_hq, media_id):
        super(MusicReply, self).__init__(sender)
        self.type = 'music'
        self.media_id = media_id
        self.title = title
        self.description = desc
        self.music_url = music_url
        self.music_url_hq = music_url_hq

    def msg_type(self):
        return self.type

    def node(self):
        node = WeChatXML("Music")
        node.add_ele("Title", self.title)
        node.add_ele("Description", self.description)
        node.add_ele("MusicUrl", self.music_url)
        node.add_ele("HQMusicUrl", self.music_url_hq)
        node.add_ele("ThumbMediaId", self.media_id)
        return node


class NewsReply(ReplyObject):
    MAX_NUM_OF_NEWS = 8

    def __init__(self, sender, title, desc, picture_url, link):
        super(NewsReply, self).__init__(sender)
        self.type = 'news'
        self.news = list()
        self.add_more_news(title, desc, picture_url, link)

    def msg_type(self):
        return self.type

    def node(self):
        node1 = WeChatXML("ArticleCount")
        node1.add_ele(None, len(self.news))
        node = WeChatXML("Articles")
        for new in self.news:
            item = WeChatXML("item")
            item.add_ele("Title", new.title)
            item.add_ele("Description", new.description)
            item.add_ele("PicUrl", new.image_url)
            item.add_ele("Url", new.link)
            node.add_ele(None, item)
        return node1 + node

    def add_more_news(self, title, desc, picture_url, link):
        if len(self.news) >= NewsReply.MAX_NUM_OF_NEWS:
            warnings.warn("过多的消息，最多{num}条，不再继续添加".format(num=NewsReply.MAX_NUM_OF_NEWS))
            return
        news = Msg(title=title,
                   description=desc,
                   image_url=picture_url,
                   link=link)
        self.news.append(news)
