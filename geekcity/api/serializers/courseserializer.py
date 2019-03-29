#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/29 13:37
# @Author  : Shen
# @Email   : st201304@163.com
# @File    : courseserializer.py
# @Software: PyCharm

from rest_framework import serializers
from api.models import CourseDetail, Course, CourseChapter, CourseSection


class CourseCategorySerializer(serializers.Serializer):
    name = serializers.CharField()


class CourseSerializer(serializers.ModelSerializer):
    sub_category = serializers.CharField(source="sub_category.name")
    teacher = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "course_img", "sub_category", "teacher", "hours", "sections"]

    def get_teacher(self, obj):
        teacher_obj = obj.teacher
        return {"name": teacher_obj.name,
                "title": teacher_obj.title,
                "signature": teacher_obj.signature,
                "describe": teacher_obj.describe}

    def get_sections(self, obj):
        chapters = obj.coursechapters.all()
        section_list = []
        for chapter in chapters:
            for section in chapter.coursesections.all():
                section_list.append({"id": section.order, "name": section.name, "section_link": section.section_link,
                                     "free_trail": section.free_trail})
        return section_list[:5]


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseChapterSerializer(serializers.ModelSerializer):
    pass


class CourseSectionSerializer(serializers.ModelSerializer):
    pass


class CourseTeacherSerializer(serializers.ModelSerializer):
    pass
