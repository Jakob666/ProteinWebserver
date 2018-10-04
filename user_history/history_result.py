# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-8-27
description:
    当用户访问webserver页面时，运行该模块调取用户之前提交的文件的信息。
"""
from user_upload.models import UserFile
from collections import OrderedDict
import os


class HistoryResult:
    @staticmethod
    def get_user_history(username):
        res = UserFile.objects.filter(username=username).order_by("upload_time")
        return (record for record in res)

    @staticmethod
    def get_task_status(request):
        """
        用于获取用户的历史任务的状态，有error、completed 和 no result三种。
        error 是用户上传文件不规范或者是服务器的annovar软件问题所致。
        completed 是用户上传任务且分析已完成。
        no result 是用户上传的文件符合规范且服务器环境没出问题的情况下因为一些特殊的原因（如vcf文件未解析出SNP位点）使得分析无法继续造成。
        :param request: 用户上传的请求。
        :return:
        """
        try:
            username = request.COOKIES["cname"]
            username = username.split("=")[-1]
        except KeyError:
            return False
        tasks_status = OrderedDict()
        res = HistoryResult.get_user_history(username)
        for record in res:
            try:
                upload_time = str(record.upload_time).split(".")[0]
                upload_dir = str(record.user_dir)
                status = HistoryResult.judge_from_log_file(upload_dir)
                tasks_status[upload_time] = status
            except FileNotFoundError:
                continue

        return tasks_status

    @staticmethod
    def judge_from_log_file(upload_dir):
        log_file = os.path.join(upload_dir, "analysis.log")
        status = "running"
        with open(log_file, "r") as f:
            content = f.read()
        # 正常情况下完成分析时的内容
        if "analysis complete" in content:
            status = "completed"

        # 服务器的annovar出错时的内容
        if "annovar error" in content:
            status = "error"

        # 用户提交的vcf文件或者tab文件经过注释后没有得到SNP结果时的内容
        if "contains no nonsynonymous variant" in content:
            status = "no result"

        # vcf或tab数据经过处理后得到的结果无法与数据库中蛋白结果匹配时的内容
        if "can't match refseq to uniprot" in content:
            status = "no result"
        del content

        return status
