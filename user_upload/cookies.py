# -*- coding: utf-8 -*-
"""
@author: hbs
@date: 2018-8-13
description:
    用于设置查询用户的cookie信息，主要是提取cookie中的uid信息。
"""
import numpy as np
from .models import UserFile
from django.shortcuts import render


class Cookies:
    @staticmethod
    def check_cookies(request):
        """
        从用户的COOKIE中查找是否之前有访问过本站且依旧保留有uid
        :param request:
        :return:
        """
        # 假设网站始终将用户的COOKIE中的键设置为"cname",cname的形式为 lysine=XXX（XXX是uid）
        try:
            client_name = request.COOKIES["cname"]
            uid = client_name.split("=")[-1]
        # 如果没有这个键，则说明COOKIE中不存在记录
        except KeyError:
            uid = Cookies.create_uid()
        return uid

    @staticmethod
    def create_uid():
        """
        如果没有在COOKIE中查找到uid，就为用户重建uid
        :return:
        """
        prefix = "lysine"
        chars = np.array(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                          'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                          't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
                          'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        uid = np.random.choice(chars, 8)
        uid = prefix + "".join(uid)
        if UserFile.objects.filter(username=uid).exists():
            uid = Cookies.create_uid()
        return uid

    @staticmethod
    def set_cookies(uid, webserver_name, response):
        """
        无论是否是新建的client_name，都需要将其重新添加到COOKIE中，设置过期时间为7天
        :param uid: 由check_cookie得到的uid
        :param webserver_name: webserver的名称，作为cookie信息的前缀
        :param response: 一个render对象
        :return:
        """
        client_name = webserver_name + "=" + uid
        # 设置cookie的生命周期7天
        cookie_max_age = 60 * 60 * 24 * 7
        # set_cookie方法的max_age参数对应cookie信息存活的秒数
        response.set_cookie(key="cname", value=client_name, max_age=cookie_max_age)
        return response
