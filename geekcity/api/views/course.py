#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/28 19:48
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : course.py
# @Software: PyCharm

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from api import models
from api.serializers.courseserializer import CourseSerializer, CourseDetailSerializer, CourseCategorySerializer
from api.utils.baseresponse import BaseResponse


class CourseCategoryViewSet(ViewSet):
    """分类接口"""

    def list(self, request, *args, **kwargs):
        ret = BaseResponse()
        category_queryset = models.CourseCategory.objects.all()
        ser = CourseCategorySerializer(instance=category_queryset, many=True)
        ret.data = ser.data
        return Response(ret.dict)


class CourseViewSet(ViewSet):
    """课程接口"""

    def list(self, request, *args, **kwargs):
        # 这儿要接受一下分类id，进行分类展示 example 视频课、微课
        ret = BaseResponse()
        category_id = request.GET.get('type_id')
        if category_id:
            course_queryset = models.Course.objects.filter(sub_category=category_id)
            ser = CourseSerializer(instance=course_queryset, many=True)
            ret.data = ser.data
        else:
            course_queryset = models.Course.objects.all()
            ser = CourseSerializer(instance=course_queryset, many=True)
            ret.data = ser.data
        return Response(ret.dict)

    def retrieve(self, request, *args, **kwargs):
        # 课程详细，一定要返回前端模板id，进行区分展示
        ret = BaseResponse()
        course_id = kwargs.get('id')
        try:
            course_obj = models.CourseDetail.objects.get(course_id=course_id)
            ser = CourseDetailSerializer(instance=course_obj, many=False)
            ret.data = ser.data
        except:
            ret.code = 404
            ret.error = "课程不存在或已下架"
        return Response(ret.dict)
