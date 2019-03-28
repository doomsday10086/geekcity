#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/28 20:47
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : account.py
# @Software: PyCharm

from rest_framework.response import Response
from rest_framework.views import APIView


class AuthStatus(APIView):
    """登录退出接口"""

    def get(self, request, *args, **kwargs):
        # 退出  前端请求接口，并将vuex和cookies中保留的token清空掉
        pass

    def post(self, request, *args, **kwargs):
        # 登录  前端请求接口，响应携带token返回，前端保存在cookies和vuex中，并在之后的请求中携带token进行验证
        pass


class AccountView(APIView):
    """用户信息接口，包含展示和修改"""

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class AgreeView(APIView):
    """点赞接口"""

    def pacth(self, request, *args, **kwargs):
        # 获取所有已公开笔记
        pass


class CollectionView(APIView):
    """收藏接口"""

    def pacth(self, request, *args, **kwargs):
        # 更改评论数，表结构要进行修改，用户和用户收藏对象要做联合唯一约束
        # 也可以是创建表存储用户id，文章id，让后定义一个标志位，收藏或取消只需要进行取反就行，也存在redis中，定时存储到数据库
        pass


class CommentView(APIView):
    """评论接口"""

    def pacth(self, request, *args, **kwargs):
        # 这个用serializer反序列化有问题，只有手动进行
        pass

    def delete(self, request, *args, **kwargs):
        pass
