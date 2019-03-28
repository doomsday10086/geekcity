#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/28 20:56
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : note.py
# @Software: PyCharm

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class PublicNoteView(ViewSet):
    """公开笔记接口"""

    def list(self, request, *args, **kwargs):
        # 获取所有已公开笔记
        pass

    def retrieve(self, request, *args, **kwargs):
        # 获取单挑笔记
        pass


class PrivateNoteView(ViewSet):
    """私人笔记接口"""

    def list(self, request, *args, **kwargs):
        # 获取所有自己的私有笔记
        pass

    def retrieve(self, request, *args, **kwargs):
        # 获取单条笔记
        pass
