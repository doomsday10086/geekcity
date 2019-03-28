#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/28 19:48
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : course.py
# @Software: PyCharm

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class CourseCategory(ViewSet):
    """分类接口"""

    def list(self, request):
        pass


class CourseViewSet(ViewSet):
    """课程接口"""

    def list(self, request, *args, **kwargs):
        # 这儿要对接受一下分类id，进行分类展示 example 视频课、微课
        return Response('111')

    def retrieve(self, request, *args, **kwargs):
        # 课程详细，一定要返回前端模板id，进行区分展示
        return Response('111')
