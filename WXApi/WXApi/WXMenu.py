# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

"""
用于生成菜单界面
尚不可使用
"""
import sys
import json

from .WXError import WXApiError


class Button(object):
    accept_types = ['click', 'view', 'scancode_push', 'scancode_waitmsg', 'pic_sysphoto', 'pic_photo_or_album',
                    'pic_weixin', 'location_select', 'media_id', 'view_limited']


class WXMenu(object):
    MAX_Button = 3

    def __init__(self, current_menu=None, encoding="utf-8"):
        self.encoding = encoding
        self.buttons = list()

        if current_menu is not None:
            menu = json.loads(current_menu, encoding=encoding)['menu']
            for button in menu.get('button'):
                self._add_button(button['name'], button)

    def _add_button(self, name, button, has_sub_button=False):
        # type: (str, dict, bool) -> None
        if len(self.buttons) > WXMenu.MAX_Button:
            raise WXApiError("最多添加 {0} 个一级菜单".format(WXMenu.MAX_Button))
        try:
            name = name.decode(self.encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        print("button", button)
        for button in self.buttons:
            if button['name'] == name:
                raise WXApiError("重名的菜单")
        if not has_sub_button:
            self.buttons.append(button)
        elif 'sub_button' in button:
            for sub_button in button['sub_button']:
                self._add_sub_button(name, sub_button['name'], button)
        else:
            raise WXApiError("无效的菜单")

    def _add_sub_button(self, parent_name, name, button):
        print("parent_name", parent_name)

    def create_view(self, view_name, view_link, button_name=None):
        try:
            view_link_tmp = view_link.encode(self.encoding)
            if len(view_link_tmp) > 1024:
                raise WXApiError("链接地址过长，微信服务器限制为1024字符")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

        button = dict(name=view_name, type='view', url=view_link)
        if button_name is not None:
            self._check_name(view_name, True)
            self._add_sub_button(button_name, view_name, button)
        else:
            self._check_name(view_name, False)
            self._add_button(view_name, button)

    def create_click(self, click_name, click_key, button_name=None):
        button = dict(name=click_name, type='click', key=click_key)
        if button_name is not None:
            self._check_name(click_name, True)
            self._add_sub_button(button_name, click_name, button)
        else:
            self._check_name(click_name, False)
            self._add_button(click_name, button)

    def _check_name(self, name, is_sub_button=False):
        try:
            name = name.encode(self.encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        if not is_sub_button:
            if len(name) > 16:
                raise WXApiError("一级菜单名称太长，建议4个汉字以内，最大8个汉字")
        else:
            if len(name) > 40:
                raise WXApiError("二级菜单名称太长，建议7个汉字以内，最大20个汉字")

    def __str__(self):
        if len(self.buttons) < 1:
            raise WXApiError("最少添加 1 个一级菜单")
        elif len(self.buttons) > WXMenu.MAX_Button:
            raise WXApiError("最多添加 {0} 个一级菜单".format(WXMenu.MAX_Button))
        else:
            return json.dumps(dict(button=self.buttons), encoding=sys.stdout.encoding, ensure_ascii=False)

    def __repr__(self):
        if len(self.buttons) < 1:
            raise WXApiError("最少添加 1 个一级菜单")
        elif len(self.buttons) > WXMenu.MAX_Button:
            raise WXApiError("最多添加 {0} 个一级菜单".format(WXMenu.MAX_Button))
        else:
            return json.dumps(dict(button=self.buttons), encoding=self.encoding, ensure_ascii=False)

    def to_json_object(self):
        if len(self.buttons) < 1:
            raise WXApiError("最少添加 1 个一级菜单")
        elif len(self.buttons) > WXMenu.MAX_Button:
            raise WXApiError("最多添加 {0} 个一级菜单".format(WXMenu.MAX_Button))
        else:
            return dict(button=self.buttons)

    def to_json_string(self):
        return self.__repr__()
