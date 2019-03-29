#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/28 19:45
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : urls.py
# @Software: PyCharm

from django.urls import re_path
from api.views import course

urlpatterns = [
    # 课程相关接口
    re_path('^course/$', course.CourseViewSet.as_view({"get": "list"})),
    re_path('^course/(?P<id>\d+)/$', course.CourseViewSet.as_view({"get": "retrieve"})),
    re_path('^course/category/$', course.CourseCategoryViewSet.as_view({"get": "list"}))
]
