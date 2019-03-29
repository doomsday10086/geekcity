from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.db import models
import hashlib


# ########################### 1.课程相关 ################################
class CourseCategory(models.Model):
    """课程分类 example：java，python，vue"""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "课程分类"


class Teacher(models.Model):
    """讲师、导师表"""
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=64, verbose_name="职位、职称")
    signature = models.CharField(max_length=255, help_text="导师签名", blank=True, null=True)
    image = models.CharField(max_length=128)
    describe = models.TextField(max_length=1024)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "04.导师或讲师"


class Course(models.Model):
    """课程表"""
    name = models.CharField(max_length=128, unique=True)  # Python基础
    course_img = models.CharField(max_length=255)  # 原网站好像用的雪碧图，完整图片作为课程图片，人像部分作为作者图片
    sub_category = models.ForeignKey("CourseCategory", on_delete=models.DO_NOTHING)  #
    # brief = models.TextField(verbose_name="课程（模块）概述", max_length=2048)
    status_choices = ((0, '更新中'), (1, '更新完成'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    template_id = models.SmallIntegerField("前端模板id", default=1, help_text="前端模板应该是分为文字和视频两种展示类型")
    teacher = models.ForeignKey("Teacher", verbose_name="课程讲师", on_delete=models.DO_NOTHING)
    hours = models.IntegerField("课时")

    # coupon = GenericRelation("Coupon")

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "06.专题课或学位课模块"


class CourseDetail(models.Model):
    """课程详情页内容"""
    course = models.OneToOneField("Course", on_delete=models.CASCADE)
    course_slogan = models.CharField(max_length=125, blank=True, null=True)
    video_brief_link = models.CharField(verbose_name='课程介绍', max_length=255, blank=True, null=True)
    why_study = models.TextField(verbose_name="为什么学习这门课程")
    what_to_study_brief = models.TextField(verbose_name="我将学到哪些内容")
    career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True)

    asked_question = GenericRelation("OftenAskedQuestion")

    def __str__(self):
        return "%s" % self.course

    class Meta:
        verbose_name_plural = "07.课程或学位模块详细"


class OftenAskedQuestion(models.Model):
    """常见问题"""
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1024)

    def __str__(self):
        return "%s-%s" % (self.content_object, self.question)

    class Meta:
        unique_together = ('content_type', 'object_id', 'question')
        verbose_name_plural = "08. 常见问题"


class CourseChapter(models.Model):
    """课程章节"""
    course = models.ForeignKey("Course", related_name='coursechapters', on_delete=models.CASCADE)
    chapter = models.SmallIntegerField(verbose_name="第几章", default=1)
    name = models.CharField(max_length=128)
    summary = models.TextField(verbose_name="章节介绍", blank=True, null=True)
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)

    class Meta:
        unique_together = ("course", 'chapter')
        verbose_name_plural = "10. 课程章节"

    def __str__(self):
        return "%s:(第%s章)%s" % (self.course, self.chapter, self.name)


class CourseSection(models.Model):
    """课时目录"""
    chapter = models.ForeignKey("CourseChapter", related_name='coursesections', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    order = models.PositiveSmallIntegerField(verbose_name="课时排序", help_text="建议每个课时之间空1至2个值，以备后续插入课时")
    section_type_choices = ((0, '文档'), (1, '音频'), (2, '视频'))
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices)
    # 59EE3275E977AADB9C33DC5901307461
    section_link = models.CharField(max_length=255, blank=True, null=True, help_text="若是video，填vid,若是文档，填link")
    # pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    free_trail = models.BooleanField("是否可试看", default=False)

    class Meta:
        unique_together = ('chapter', 'section_link')
        verbose_name_plural = "11. 课时"

    def __str__(self):
        return "%s-%s" % (self.chapter, self.name)


class CourseReview(models.Model):
    """课程评价"""
    enrolled_course = models.OneToOneField("EnrolledCourse", on_delete=models.CASCADE)
    about_teacher = models.FloatField(default=0, verbose_name="讲师讲解是否清晰")
    about_video = models.FloatField(default=0, verbose_name="内容实用")
    about_course = models.FloatField(default=0, verbose_name="课程内容通俗易懂")
    review = models.TextField(max_length=1024, verbose_name="评价")
    disagree_number = models.IntegerField(default=0, verbose_name="踩")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    # tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
    date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
    is_recommend = models.BooleanField("热评推荐", default=False)
    hide = models.BooleanField("不在前端页面显示此条评价", default=False)

    def __str__(self):
        return "%s-%s" % (self.enrolled_course.course, self.review)

    class Meta:
        verbose_name_plural = "13. 课程评价（购买课程后才能评价）"


# ########################### 2. 深科技相关 ################################
class Article(models.Model):
    """文章资讯"""
    title = models.CharField(max_length=30, verbose_name="标题")
    author = models.ForeignKey("Account", verbose_name="作者", on_delete=models.DO_NOTHING)
    article_type_choices = ((0, '学习笔记'), (1, '技术分享'), (2, '心情随笔'))
    article_type = models.SmallIntegerField(choices=article_type_choices, default=0)
    brief = models.TextField(max_length=512, verbose_name="摘要")
    head_img = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(verbose_name="文章正文")
    pub_date = models.DateTimeField(verbose_name="发布时间")
    status_choices = ((0, '公开'), (1, '隐藏'))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="状态")
    comment_num = models.SmallIntegerField(default=0, verbose_name="评论数")
    agree_num = models.SmallIntegerField(default=0, verbose_name="点赞数")
    view_num = models.SmallIntegerField(default=0, verbose_name="阅读数")
    collect_num = models.SmallIntegerField(default=0, verbose_name="收藏数")

    # tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
    date = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")

    position_choices = ((0, '信息流'), (1, 'banner大图'), (2, 'banner小图'))
    position = models.SmallIntegerField(choices=position_choices, default=0, verbose_name="位置")

    # comment = GenericRelation("Comment")

    class Meta:
        verbose_name_plural = "17. 文章"

    def __str__(self):
        return "%s-%s" % (self.author, self.title)


class Collection(models.Model):
    """收藏"""
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    account = models.ForeignKey("Account", on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'account')
        verbose_name_plural = "18. 通用收藏表"


class Comment(models.Model):
    """通用的评论表"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name="类型", on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    p_node = models.ForeignKey("self", blank=True, null=True, verbose_name="父级评论", on_delete=models.DO_NOTHING)
    content = models.TextField(max_length=1024)
    account = models.ForeignKey("Account", verbose_name="用户名", on_delete=models.DO_NOTHING)
    disagree_number = models.IntegerField(default=0, verbose_name="踩")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = "19. 通用评论表"


# ########################### 3. 用户相关 ################################

class Account(models.Model):
    username = models.CharField("用户名", max_length=64, unique=True, help_text="用户名只能是手机号")
    nickname = models.CharField("昵称", max_length=12, null=True, blank=True)
    password = models.CharField("密码", max_length=64)
    uid = models.CharField(max_length=64, unique=True, help_text='微信用户绑定和CC视频统计')  # 与第3方交互用户信息时，用这个uid,以避免泄露敏感用户信息
    openid = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name_plural = "账户"
        verbose_name = verbose_name_plural

    def save(self, *args, **kwargs):
        if not self.pk:
            self.nickname = "xxxx"
            self.password = "xxxx"
        return super(Account, self).save(*args, **kwargs)

    def create_password(self):
        pass

    def create_nickname(self):
        pass


class UserAuthToken(models.Model):
    """
    用户Token表
    """
    user = models.OneToOneField(to="Account", on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)


# ########################### 5. 支付相关 ################################
class Coupon(models.Model):
    """优惠券生成规则"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choices = ((0, '立减券'), (1, '满减券'), (2, '折扣券'))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choices, default=0, verbose_name="券类型")

    """
    通用：
        money_equivalent_value=100
        off_percent=null
        minimum_consume=0
    满减：
        money_equivalent_value=100
        off_percent=null
        minimum_consume=1000
    折扣：
        money_equivalent_value=0
        off_percent=79
        minimum_consume=0
    """
    money_equivalent_value = models.IntegerField(verbose_name="等值货币", null=True, blank=True)
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券，例7.9折，写79", blank=True, null=True)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段", null=True, blank=True)

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField("数量(张)", default=1)
    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期（天）", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "31. 优惠券生成记录"

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)

    def save(self, *args, **kwargs):
        if not self.coupon_valid_days or (self.valid_begin_date and self.valid_end_date):
            if self.valid_begin_date and self.valid_end_date:
                if self.valid_end_date <= self.valid_begin_date:
                    raise ValueError("valid_end_date 有效期结束日期必须晚于 valid_begin_date ")
            if self.coupon_valid_days == 0:
                raise ValueError("coupon_valid_days 有效期不能为0")
        if self.close_date < self.open_date:
            raise ValueError("close_date 优惠券领取结束时间必须晚于 open_date优惠券领取开始时间 ")

        super(Coupon, self).save(*args, **kwargs)


class CouponRecord(models.Model):
    """优惠券发放、消费纪录"""
    coupon = models.ForeignKey("Coupon", on_delete=models.CASCADE)
    number = models.CharField(max_length=64, unique=True)
    account = models.ForeignKey("Account", verbose_name="拥有者", on_delete=models.DO_NOTHING)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")

    # order = models.ForeignKey("Order", blank=True, null=True, verbose_name="关联订单")  # 一个订单可以有多个优惠券

    class Meta:
        verbose_name_plural = "32. 用户优惠券"

    def __str__(self):
        return '%s-%s-%s' % (self.account, self.number, self.status)


class EnrolledCourse(models.Model):
    """已订阅课程"""
    account = models.ForeignKey("Account", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", limit_choices_to=~Q(course_type=2), on_delete=models.DO_NOTHING)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    valid_begin_date = models.DateField(verbose_name="有效期开始自")
    valid_end_date = models.DateField(verbose_name="有效期结束至")
    status_choices = ((0, '已开通'), (1, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    order_detail = models.OneToOneField("OrderDetail", on_delete=models.DO_NOTHING)  # 使订单购买后支持 课程评价

    # order = models.ForeignKey("Order",blank=True,null=True)

    def __str__(self):
        return "%s:%s" % (self.account, self.course)

    class Meta:
        verbose_name_plural = "34. 报名专题课"


class Order(models.Model):
    """订单"""
    payment_type_choices = ((0, '微信'), (1, '支付宝'), (2, '优惠码'), (3, '贝里'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices)

    payment_number = models.CharField(max_length=128, verbose_name="支付第3方订单号", null=True, blank=True)
    order_number = models.CharField(max_length=128, verbose_name="订单号", unique=True)  # 考虑到订单合并支付的问题
    account = models.ForeignKey("Account", on_delete=models.DO_NOTHING)
    actual_amount = models.FloatField(verbose_name="实付金额")

    status_choices = ((0, '交易成功'), (1, '待支付'), (2, '退费申请中'), (3, '已退费'), (4, '主动取消'), (5, '超时取消'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    date = models.DateTimeField(auto_now_add=True, verbose_name="订单生成时间")
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name="付款时间")
    cancel_time = models.DateTimeField(blank=True, null=True, verbose_name="订单取消时间")

    class Meta:
        verbose_name_plural = "37. 订单表"

    def __str__(self):
        return "%s" % self.order_number


class OrderDetail(models.Model):
    """订单详情"""
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 可关联普通课程或学位
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    original_price = models.FloatField("课程原价")
    price = models.FloatField("折后价格")
    content = models.CharField(max_length=255, blank=True, null=True)  # ？
    valid_period_display = models.CharField("有效期显示", max_length=32)  # 在订单页显示
    valid_period = models.PositiveIntegerField("有效期(days)")  # 课程有效期
    memo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (self.order, self.content_type, self.price)

    class Meta:
        verbose_name_plural = "38. 订单详细"
        unique_together = ("order", 'content_type', 'object_id')
