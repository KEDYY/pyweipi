# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
用于向微信服务器拉取数据和管理
"""

import logging
import os
import requests
from time import (time)
from datetime import datetime

from .WXError import *
from .WXUtils import (quote, url_encode)


class MPReply(object):
    def __init__(self, open_id):
        self.touser = open_id
        self.msgtype = None


class MPCenter(object):
    """
    微信公众号后台接口
    """

    def __init__(self, app_id, app_secret, enable_token_cache=True, token=None, expires=None):
        super(MPCenter, self).__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.enable_cache = enable_token_cache
        self.access_token_cache = token
        if expires is None:
            self.access_token_date = None
        else:
            self.access_token_date = datetime.fromtimestamp(expires)

    def get(self, url, **kwargs):
        # type: (object, dict) -> dict
        params = dict(kwargs)
        params.update(dict(access_token=self.access_token))
        return self.valid_response(requests.get(url=url, params=params))

    def post(self, url, data=None, json=None, **kwargs):
        params = dict(access_token=self.access_token)
        if data is not None:
            return self.valid_response(requests.post(url, data, params=params, **kwargs))
        if json is not None:
            from json import dumps
            data = dumps(json, encoding="utf-8", ensure_ascii=False)
            return self.valid_response(requests.post(url, data, params=params, **kwargs))

    def download(self, url, params=None, **kwargs):
        stream = requests.get(url, params=params, stream=True, **kwargs)
        if stream.ok:
            return stream.raw.data
        raise WXApiError(url)

    def update(self, app_id, app_secret):
        self.app_id = app_id or self.app_id
        self.app_secret = app_secret

    def refresh_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = dict(
            grant_type='client_credential',
            appid=self.app_id,
            secret=self.app_secret
        )
        rs = requests.get(url, params=params).json()
        expires_in = int(rs['expires_in'])
        self.access_token_cache = rs['access_token']
        self.access_token_date = datetime.fromtimestamp(expires_in + time() - 60)
        logging.warn("刷新access_token {0} 将于{1}过期".format(self.access_token_cache, self.access_token_date))
        return dict(rs)

    @property
    def access_token(self):
        if self.enable_cache and self.access_token_cache is not None \
                and self.access_token_date > datetime.now():
            return self.access_token_cache
        else:
            self.refresh_access_token()
            return self.access_token

    def _after_request_error(self, error, call_back, *args):
        if isinstance(error, WeChatError):
            if error.is_access_token_expires():
                self.refresh_access_token()
                return call_back(*args)

    def valid_response(self, res_obj):
        # type: (requests.Response) -> dict
        if res_obj.ok:
            result = res_obj.json()
            if 'errcode' in result:
                if result['errcode'] == 0:
                    return result
                else:
                    raise WeChatError(result)
            return result
        raise WXApiError("微信服务器返回异常状态:" + res_obj.status_code)

    def reply(self, mp_reply):
        """此接口主要用于客服等有人工消息处理环节的功能,时限48小时"""
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send'
        try:
            self.post(url, json=mp_reply)
        except WeChatError as e:
            logging.error(e.message)
        except Exception as e:
            logging.error("客服消息回复失败")
            raise WXApiError(e)
        else:
            return True

    def add_kf(self, account, nickname, password):
        """
        增加客服账号
        :return:
        """
        url = 'https://api.weixin.qq.com/customservice/kfaccount/add'
        params = {
            "kf_account": account,
            "nickname": nickname,
            "password": password,
        }
        try:
            self.post(url, json=params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            return True

    def broadcast(self):
        """该接口不适用,服务号每月最大4次"""
        pass

    #######################
    # 菜单界面管理
    #######################
    def add_menu(self, wx_ui):
        """
        请求微信服务器增加菜单
        :param wx_ui: JSON Object 菜单数据
        :return: True if success else False
        """
        url = 'https://api.weixin.qq.com/cgi-bin/menu/create'
        try:
            self.post(url, json=wx_ui)
        except WeChatError as e:
            logging.error(e.message)
            return False
        else:
            logging.info('添加菜单成功')
            return True

    def get_menu(self):
        """请求微信服务器，获取当前有效的菜单格式"""
        url = 'https://api.weixin.qq.com/cgi-bin/menu/get'
        try:
            res_obj = self.get(url)
        except WeChatError as e:
            logging.error(e.message)
        else:
            return res_obj

    def del_menu(self):
        """请求微信服务器，清空菜单"""
        url = 'https://api.weixin.qq.com/cgi-bin/menu/delete'
        try:
            self.get(url)
        except WeChatError as e:
            logging.error(e.message)
        else:
            logging.info("成功删除菜单")

    #########################
    # 组管理
    #########################
    def create_group(self, group_name):
        """新建组名称30字符内，返回(组名(str),微信分配的组Id(int))"""
        url = 'https://api.weixin.qq.com/cgi-bin/groups/create'
        params = {
            "group": {
                "name": group_name
            }
        }
        try:
            res_obj = self.post(url, json=params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            gid = res_obj['group']['id']
            logging.info('createGroups成功[group_id:%d,group_name:%s]' % (gid, group_name))
            return group_name, gid  # 同一名字可以对应多个ID

    def update_group(self, gid, group_name):  # 更新组名称
        """
        更改已建的组名称30字符内,(int,str)失败时抛出
        :raise WXError
        """
        url = 'https://api.weixin.qq.com/cgi-bin/groups/update'
        params = {
            "group": {
                "id": gid,
                "name": group_name
            }
        }
        try:
            self.post(url, json=params)
        except WeChatError as e:
            logging.error(e.message)
            return False
        else:
            logging.info('updateGroups成功[gid:%d,Gname:%s]' % (gid, group_name))
            return True

    def get_groups(self):
        """
        获取以创建的所有分组,成功[{name:, id:, users:)},...]失败
        :raise WXError
        """
        url = 'https://api.weixin.qq.com/cgi-bin/groups/get'
        try:
            res_obj = self.get(url)
        except WeChatError as e:
            logging.error(e.message)
        else:
            logging.info('getGroups成功')
            return [_group for _group in res_obj['groups']]

    ##########################
    # 用户管理
    ##########################
    def update_user_gid(self, openid, gid):  # 移动用户分组
        """
        传入 用户的openid和目的组id
        """
        url = 'https://api.weixin.qq.com/cgi-bin/groups/members/update'
        params = {
            "openid": openid,
            "to_groupid": gid
        }
        try:
            self.post(url, json=params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            logging.info('`update_user_gid` 更改用户组成功')

    def get_user_gid(self, openid):
        """
        获取指定用户的组ID
        :param openid:
        :return:
        :raise WXError
        """
        url = 'https://api.weixin.qq.com/cgi-bin/groups/getid'
        params = dict(openid=openid)
        try:
            res_obj = self.post(url, json=params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            logging.info('`get_user_gid` 获取用户组ID成功')
            return res_obj

    def get_user_info(self, openid, language='zh_CN'):
        """
        获取用户个人信息
        :param openid:
        :param language:
        :return:
        :raise WXError
        """
        params = dict(openid=openid, lang=language)
        url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        try:
            res_obj = self.get(url, **params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            logging.info('`get_user_info` 获取用户信息成功')
            return res_obj

    def _get_user(self, url, next_openid=None):
        """
        :param url:
        :param next_openid:
        :return:
        """
        try:
            if next_openid is not None:
                params = dict(next_openid=next_openid)
                res_obj = self.get(url, **params)
            else:
                res_obj = self.get(url)
        except WeChatError as e:
            logging.error(e.message)
        else:
            return res_obj

    def get_users(self):
        """获取所有关注者的openid"""
        all_users = list()
        url = 'https://api.weixin.qq.com/cgi-bin/user/get'
        logging.info('获取所有用户')
        res_obj = self._get_user(url)

        total = res_obj['total']
        count = res_obj['count']
        all_users += res_obj['data").get("openid']
        while count != total:
            next_openid = res_obj['next_openid']
            if not next_openid:
                break  # 防止死循环
            if total != res_obj['total']:
                logging.warning("`get_users` 获取用户总数不一致")
                break  # 防止死循环
            res_obj = self._get_user(url, next_openid)
            count += res_obj['count']
            all_users += res_obj['data").get("openid']
        logging.info("成功获取所有用户:[%d]位" % len(all_users))
        return all_users

    ###################
    # 多媒体管理
    ###################
    def upload_media(self, file_path, file_type):
        # type: (str, str) -> dict
        """
        上传指定文件，成功则返回对应的 `media_id`
        :param file_path: 
        :param file_type: 'image' 'thumb', 'voice', 'video'
        :return: `None` if failed else dict
        """
        url = 'http://file.api.weixin.qq.com/cgi-bin/media/upload' + '&type='
        if not os.path.exists(file_path):
            logging.error("uploadMedia指定的文件不存在[%s]" % file_path)
            raise WXApiError("指定路径文件不存在")
        if file_path.endswith('jpg') and file_type == 'image':
            if os.path.getsize(file_path) > 128 * 1024:
                logging.error("上传Image文件最大为128KB")
                raise WXApiError("Image文件最大128KB")
        elif file_path.endswith('jpg') and file_type == 'thumb':
            if os.path.getsize(file_path) > 64 * 1024:
                logging.error("上传thumb文件最大为64KB")
                raise WXApiError("thumb文件最大64KB")
        elif (file_path.endswith('amr') or file_path.endswith('mp3')) and file_type == 'voice':
            if os.path.getsize(file_path) > 256 * 1024:
                logging.error("voice文件最大256KB")
                raise WXApiError("voice文件最大256KB")
        elif file_path.endswith('mp4') and file_type == 'video':
            if os.path.getsize(file_path) > 1 * 1024 * 1024:
                logging.error("Video文件最大1MB")
                raise WXApiError("Video文件最大1MB")
        else:
            logging.error("指定的文件类型不支持上传")
            raise WXApiError("不支持的文件类型或格式")
        url += file_type
        try:
            res_obj = self.post(url, files={'image': (open(file_path, 'rb'))})
        except WeChatError as e:
            logging.error("上传文件失败")
            logging.error(e.message)
        else:
            logging.info('uploadMedia上传文件成功,media_id:[%s]' % res_obj['media_id'])
            return res_obj

    def download_media(self, media_id, des_path, overwrite=False):
        # type: (str, str, bool) -> bool
        """
        下载指定的 `media_id` 并存储
        :param media_id: 
        :param des_path: 
        :param overwrite: 
        :return: 
        """
        if os.path.exists(os.path.abspath(des_path)) and (not overwrite):
            logging.error("指令路径文件已存在，且未指定覆盖")
            raise WXApiError("指令路径文件已存在，且未指定覆盖")
        url = 'http://file.api.weixin.qq.com/cgi-bin/media/get'
        params = dict(media_id=media_id)
        try:
            bin_data = self.download(url, params=params)
        except WeChatError as e:
            logging.error(e.message)
        else:
            with open(des_path, 'wb') as f:
                f.write(bin_data)
            logging.info("文件下载保存成功")
            return True

    ###############
    # 推广二维码管理
    ###############
    def create_qrcode(self, scene_value, expire_seconds=2592000):
        """指定是创建二维码,以及场景ID
        默认创建 30天的临时ID，
        如果指定的时间超过该限制或者给定的场景值是字符串则使用永久的ID
        action_name QR_SCENE QR_LIMIT_SCENE QR_LIMIT_STR_SCENE
        """
        url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create'
        if expire_seconds <= 2592000 and type(scene_value) is int:
            params = {
                "action_name": "QR_SCENE",
                "action_info": {
                    "scene": {
                        "scene_str": "123"
                    }
                }
            }
        else:
            if type(scene_value) is int:
                if scene_value not in range(1, 100001):
                    raise WeChatError("微信服务器要求给定的场景编号不超过 100000")
                params = {
                    "action_name": "QR_LIMIT_SCENE",
                    "action_info": {
                        "scene": {
                            "scene_id": scene_value
                        }
                    }
                }
            else:
                if len(scene_value) > 64:
                    raise WeChatError("微信服务器要求给定的场景标志不超过64个英文字符")
                params = {
                    "action_name": "QR_LIMIT_STR_SCENE",
                    "action_info": {
                        "scene": {
                            "scene_str": str(scene_value)
                        }
                    }
                }
        try:
            if params is not None:
                res_obj = self.post(url, json=params)
            else:
                raise WXApiError("没有指定二维码参数")
        except WeChatError as e:
            logging.error("创建二维码出错")
            logging.error(e.message)
        else:
            ticket = quote(res_obj['ticket'])  # 创建二维码ticket
            url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=' + ticket
            # 凭借ticket到指定URL换取二维码,返回地址,自行决定是分发URL还是下载
            return url

    def save_qrcode(self, des_path, qr_url, overwrite=True):
        # type: (str, str, bool) -> bool
        """将指定的二维码url保存到本地,失败/出错 抛出异常 WXError WeChatError IOError"""
        if os.path.exists(os.path.abspath(des_path)) and (not overwrite):
            logging.error("指令路径文件已存在，且未指定覆盖")
            raise WXApiError("指令路径文件已存在，且未指定覆盖")
        try:
            bin_data = self.download(qr_url)
        except WeChatError as e:
            logging.error("上传文件时出错")
            logging.error(e.message)
        else:
            with open(des_path, 'wb') as f:
                f.write(bin_data)
            logging.info("文件下载保存成功")
            return True
