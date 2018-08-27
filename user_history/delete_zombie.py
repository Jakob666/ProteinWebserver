# -*-coding:utf-8-*-
"""
@author: hbs
@date: 2018-8-27
description:
    用于删除数据库中用户表 user_record中超过七天的记录，同时在服务器上删除相应的文件目录。
    这个模块需要使用crontab执行。
"""
from user_upload.models import UserFile
import time
import shutil
from user_upload.CONFIG import user_files
import os


class DeleteZombie:
    @staticmethod
    def get_expire_time():
        ctime = time.time()
        # 这里尽量不要小于7天，因为user_upload应用中为用户设置的cookie有效期是7天
        expire_time = ctime - 7 * 24 * 60 * 60
        return expire_time

    @staticmethod
    def get_expire_record():
        expire_time = DeleteZombie.get_expire_time()
        res = UserFile.objects.filter(visit_time__lte=expire_time)

        # 从过期的记录中提取要删除的文件目录和相关的用户名
        expired_dirs = (str(record.user_dir) for record in res)
        related_users = (str(record.username) for record in res)
        # 从数据库中删除这些记录
        res.delete()
        return expired_dirs, related_users

    @staticmethod
    def remove_dirs():
        expired_dirs, related_users = DeleteZombie.get_expire_record()
        # 删除过期文件的目录
        for expires_dir in expired_dirs:
            shutil.rmtree(expires_dir, ignore_errors=True)

        # 如果该用户的目录被删空，连带着用户目录一并删除（因为这种用户可能近期不会再使用webserver）
        for user in related_users:
            user_dir = os.path.join(user_files, user)
            if not os.listdir(user_dir):
                shutil.rmtree(user_dir, ignore_errors=True)
        return None
