#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/29 13:45
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : baseresponse.py
# @Software: PyCharm


class BaseResponse:

    def __init__(self):
        self.code = 200
        self.data = None
        self.error = None

    @property
    def dict(self):
        return self.__dict__
