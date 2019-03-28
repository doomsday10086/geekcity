"""
创建时间 : 2018/06/07
版本号 : V1
文档名 : shoppings.py
编辑人 : he_wm
作 用 : 购物车相关功能
源存储位置 : \\TmSccity_models\\api\\views\\shopping\\shoppings.py
修改及增加功能记录 :
    修改时间 : 
        1、2018/04/02:
        2、
    增加功能时间 :
        1、
        2、   
"""
import json
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import GenericViewSet, ViewSetMixin

from api.models import *
from utils.auth import TmAuth
from utils.response import BaseResponse
from utils.exception import PricePolicyInvalid


# {'get': 'list', 'post': 'create', 'delete': 'destroy'}
class Shoppings(APIView):
    """
    对购物车进行增删改查操作
    """
    # 引入redis
    conn = get_redis_connection("default")
    # 引入登录验证
    authentication_classes = [TmAuth, ]
    # 引入自定义错误类
    ret = BaseResponse()

    def get(self, request, *args, **kwargs):
        """
        查看购物车所有商品
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        course_list = []
        try:
            # 获取当前用户存储在redis中所有的购物车信息
            shopping_car_key = settings.SHOPPING_CAR_KEY.format(request.auth.user.id, "*", )
            # 生成器方式显示所有的课程信息
            for key in self.conn.scan_iter(shopping_car_key, count=10):
                info = {
                    "course_img": self.conn.hget(key, 'course_img').decode('utf-8'),
                    "name": self.conn.hget(key, 'name').decode('utf-8'),
                    "default_policy": self.conn.hget(key, 'default_policy').decode('utf-8'),
                    "price_policy": json.loads(self.conn.hget(key, 'price_policy').decode('utf-8')),
                }
                course_list.append(info)
                self.ret.code = 1000
                self.ret.data = course_list
        except Exception as e:
            self.ret.code = 1001
            self.ret.data = '获取数据失败'
        return Response(self.ret.dict)

    def post(self, request, *args, **kwargs):
        try:
            # ret = {"code": 1000}
            # 获取课程id与价格id
            course_id = int(request.data.get('courseid'))
            price_id = int(request.data.get('priceid'))
            # 获取课程信息
            course_obj = Course.objects.get(id=course_id)
            # 获取课程相关所有价格策略
            price_policy_list = course_obj.price_policy.all()
            price_policy_dict = {}
            for item in price_policy_list:
                price_policy_dict[item.id] = {'price': item.price, 'valid_period': item.valid_period,
                                              'valid_period_chain': item.get_valid_period_display()}
            # 判断用户提交的价格策略是否合法
            if price_id not in price_policy_dict:
                # 抛出价格测略不合法
                raise PricePolicyInvalid('价格策略不合法')
            # 生成redis购物篮头部分用户id与课程id
            shopping_car_key = settings.SHOPPING_CAR_KEY.format(request.auth.user.id, course_id, )
            # 生成redis购物篮体部分
            shopping_car_dict = {
                "course_img": course_obj.course_img,
                "name": course_obj.name,
                "default_policy": price_id,
                "price_policy": json.dumps(price_policy_dict),
            }
            # 存入redis
            self.conn.hmset(shopping_car_key, shopping_car_dict)
            self.ret.code = 1000
            self.ret.data = '添加成功'
        except PricePolicyInvalid as e:
            self.ret.code = 2001
            self.ret.error = e.msg
        except ObjectDoesNotExist as e:
            self.ret.code = 3001
            self.ret.error = '课程不存在'
        except Exception as e:
            self.ret.code = 4001
            self.ret.error = '获取购物车失败'
        return Response(self.ret.dict)

    def delete(self, request, *args, **kwargs):
        """
        购物车中删除指定课程
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # {'courseids':['2','1']}
        try:
            key_list = [settings.SHOPPING_CAR_KEY.format(request.auth.user.id, course_id, ) for course_id in
                        request.data.get('courseids')]
            self.conn.delete(*key_list)
            self.ret.code = 1000
            self.ret.data = '删除成功'
        except Exception as e:
            self.ret.code = 1001
            self.ret.data = '删除失败'

        return Response(self.ret.dict)

    def put(self, request, *args, **kwargs):
        """
        修改课程的价格策略
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            course_id = str(request.data.get('courseid'))
            price_id = str(request.data.get('priceid'))
            # 拼接课程的key
            shopping_car_key = settings.SHOPPING_CAR_KEY.format(request.auth.user.id, course_id, )
            # 如果不存在此课程返回提醒
            if not self.conn.exists(shopping_car_key):
                self.ret.data = '购物车不存在此课程'
                self.ret.code = 1001
                return Response(self.ret.dict)
            # 在redis中获取所有的价格策略
            price_policy_dict = json.loads(str(self.conn.hget(shopping_car_key, 'price_policy'), encoding='utf-8'))
            # 判断价格策略是否合法
            if price_id not in price_policy_dict:
                self.ret.data = '价格策略不合法'
                self.ret.code = 1003
                return Response(self.ret.dict)
            # 在购物车中修个默认的价格策略
            self.conn.hset(price_policy_dict, 'default_policy', price_id)
            self.ret.code = 1000
            self.ret.data = '价格修改成功'
        except Exception as e:
            self.ret.code = 1001
            self.ret.error = '价格修改失败'
        return Response(self.ret.dict)


class Check_out(APIView):
    """
    对结算进行操作
    """
    # 引入redis
    conn = get_redis_connection("default")
    # 引入验证模块
    authentication_classes = [TmAuth, ]
    # 引入自定义错误类
    ret = BaseResponse()

    def get(self, request, *args, **kwargs):
        print(1111111111111111)
        try:
            redis_pay_key = settings.PAY_KEY.format(request.auth.user_id, '*', )
            print('redis_pay_key===================>', redis_pay_key)
            # 拼接全场优惠券头
            redis_global_coupon_key = settings.PAYMENT_COUPON_KEY.format(request.auth.user_id, )
            print('redis_global_coupon_key=========>', redis_global_coupon_key)
            # 获取绑定课程的信息
            course_list = []
            for key in self.conn.scan_iter(redis_pay_key):
                print('key===============>', key)
                info = {}
                data = self.conn.hgetall(key)
                for k, v in data.items():
                    ks = k.decode('utf-8')
                    if ks == 'coupon':
                        info[ks] = json.loads(v.decode('utf-8'))
                    else:
                        info[ks] = v.decode('utf-8')
            course_list.append(info)
            #     获取全栈优惠券
            global_coupon_dict = {
                'coupon': json.loads(self.conn.hget(redis_global_coupon_key, 'coupon').decode('utf-8')),
                'default_coupon': self.conn.hget(redis_global_coupon_key, 'default_coupon').decode('utf-8')
            }
            self.ret.data = {
                "course_list": course_list,
                "global_coupon_dict": global_coupon_dict
            }
        except Exception as e:
            self.ret.code = 1001
            self.ret.error = '获取失败'
        return Response(self.ret.dict)

    def post(self, request, *args, **kwargs):
        payment_dict = {}
        try:
            # 清除redis中个人购物车的信息
            key_list = self.conn.keys(settings.PAY_KEY.format(request.auth.user_id, '*'))
            key_list.append(settings.PAYMENT_COUPON_KEY.format(request.auth.user_id))
            # print('key_list============>', key_list)
            self.conn.delete(*key_list)
            # 预定义存储优惠前数据结构
            global_coupon_dict = {
                "coupon": {},
                "default_coupon": 0
            }
            # 获取前端发送的课程id列表
            courseid_list = request.data.get('courseid')
            # print('courseid_list==============>', courseid_list)
            # [1,2]
            # 循环课程id列表
            for courseid in courseid_list:
                # 定制查询redis购物车头信息
                car_key = settings.SHOPPING_CAR_KEY.format(request.auth.user_id, courseid, )
                # print('car_key===================>', car_key)
                # 判断购物车中是否存在此课程
                if not self.conn.exists(car_key):
                    self.ret.data = '购物车不存在此课程'
                    self.ret.code = 1001
                    return Response(self.ret.dict)
                # 获取存储在redis中的课程价格策略字典
                policy = json.loads(self.conn.hget(car_key, 'price_policy').decode('utf-8'))
                defaule_policy = self.conn.hget(car_key, 'default_policy').decode('utf-8')
                policy_info = policy[defaule_policy]
                payment_course_dict = {
                    'course_id': str(courseid),
                    'name': self.conn.hget(car_key, 'name').decode('utf-8'),
                    'course_img': self.conn.hget(car_key, 'course_img').decode('utf-8'),
                    'policy_id': defaule_policy,
                    'coupon': {},
                    'defaule_coupon': 0
                }
                payment_course_dict.update(policy_info)
                payment_dict[str(courseid)] = payment_course_dict
            # 获取优惠券
            #     获取当前时间
            ctime = datetime.date.today()
            #     获取当前用户所有符合条件的优惠券
            coupon_list = CouponRecord.objects.filter(
                account=request.auth.user,
                status=0,
                coupon__valid_begin_date__lte=ctime,
                coupon__valid_end_date__gte=ctime,
            )
            for item in coupon_list:
                # 只处理绑定课程的优惠券
                if not item.coupon.object_id:
                    # 获取优惠券id
                    coupon_id = item.id
                    # 获取优惠券类型:满减.折扣.立减
                    coupon_type = item.coupon.coupon_type
                    info = {}
                    # 将优惠券类型存入字典
                    info['coupon_type'] = coupon_type
                    # 将优惠券类型中文存如字典
                    info['coupon_display'] = item.coupon.get_coupon_type_display()
                    if coupon_type == 0:  # 立减
                        # 获取立减金额
                        info['money_equivalent_value'] = item.coupon.money_equivalent_value
                    elif coupon_type == 1:  # 满减券
                        info['money_equivalent_value'] = item.coupon.money_equivalent_value
                        # 获取最低消费
                        info['minimum_consume'] = item.coupon.minimum_consume
                    else:  # 折扣券
                        info['off_percent'] = item.coupon.off_percent
                    global_coupon_dict['coupon'][coupon_id] = info
                    continue
                # 优惠券绑定课程的ID
                coupon_course_id = str(item.coupon.object_id)
                # 优惠券ID
                coupon_id = item.id
                # 优惠券类型：满减、折扣、立减
                coupon_type = item.coupon.coupon_type
                info = {}
                info['coupon_type'] = coupon_type
                info['coupon_display'] = item.coupon.get_coupon_type_display()
                if coupon_type == 0:  # 立减
                    info['money_equivalent_value'] = item.coupon.money_equivalent_value
                elif coupon_type == 1:  # 满减券
                    info['money_equivalent_value'] = item.coupon.money_equivalent_value
                    info['minimum_consume'] = item.coupon.minimum_consume
                else:  # 折扣
                    info['off_percent'] = item.coupon.off_percent
                if coupon_course_id not in payment_dict:
                    # 获取到优惠券，但是没有购买此课程
                    continue
                # 将优惠券设置到指定的课程字典中
                payment_dict[coupon_course_id]['coupon'][coupon_id] = info
                # 获取绑定的优惠券
            # 3. 将绑定优惠券课程+全站优惠券 写入到redis中（结算中心）。
            # 3.1 绑定优惠券课程放入redis
            for cid, cinfo in payment_dict.items():
                pay_key = settings.PAY_KEY.format(request.auth.user_id, cid)
                cinfo['coupon'] = json.dumps(cinfo['coupon'])
                self.conn.hmset(pay_key, cinfo)
            # 3.2 将全站优惠券写入redis
            gcoupon_key = settings.PAYMENT_COUPON_KEY.format(request.auth.user_id)
            global_coupon_dict['coupon'] = json.dumps(global_coupon_dict['coupon'])
            self.conn.hmset(gcoupon_key, global_coupon_dict)
            self.ret.code = 1000
            self.ret.data = '添加成功'
        except Exception as e:
            self.ret.code = 1001
            self.ret.error = '结算失败'
        return Response(self.ret.dict)

    def patch(self, request, *args, **kwargs):
        try:
            # 用户提交要修改的优惠券
            course = request.data.get('courseid')
            course_id = str(course) if course else course
            coupon_id = str(request.data.get('couponid'))
            print('course===', course, '======coupon_id========', coupon_id)
            redis_global_coupon_key = settings.PAYMENT_COUPON_KEY.format(request.auth.user_id, )
            # 获取存于redis中的绑定课程优惠券键
            redis_pay_key = settings.PAY_KEY.format(request.auth.user_id, course_id)
            if not course_id:
                # 修改全栈优惠券
                if coupon_id == '0':
                    # 不使用优惠券购买
                    self.conn.hset(redis_global_coupon_key, 'default_coupon', course_id)
                    self.ret.data = '设置成功'
                    return Response(self.ret.dict)
                # 使用优惠前，请求数据
                coupon_dict = json.loads(self.conn.hget(redis_global_coupon_key, 'coupon').decode('utf-8'))
                print('coupon_dict------------>', coupon_dict)
                # 判断用户选择优惠券是否合法
                if coupon_id not in coupon_dict:
                    self.ret.code = 1001
                    self.ret.error = '全栈优惠券不存在'
                    # 用户选择的优惠券合法
                self.conn.hset(redis_global_coupon_key, 'default_coupon', coupon_id, )
                # 修改课程优惠券
                # 不使用优惠券
            if coupon_id == '0':
                self.conn.hset(redis_pay_key, 'default_coupon', coupon_id)
                self.ret.data = '设置成功1'
                return Response(self.ret.dict)
            coupon_dict = self.conn.hget(redis_pay_key, 'coupon').decode('utf-8')
            print('coupon_dict====================>', coupon_dict, coupon_id)
            if coupon_id not in coupon_dict:
                self.ret.code = 1001
                self.ret.error = '课程不存在'
                return Response(self.ret.dict)
            self.conn.hset(redis_pay_key, 'default_coupon', coupon_id)
            self.ret.code = 1000
            self.ret.data = '修改成功'
            return Response(self.ret.dict)
        except Exception as e:
            self.ret.code = 1001
            self.ret.error = '修改失败'
        return Response(self.ret.dict)
