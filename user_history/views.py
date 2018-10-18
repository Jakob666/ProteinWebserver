# -*- coding:utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from .CONFIG import user_files
import os
import shutil
from user_upload.models import UserFile
from dwebsocket.decorators import accept_websocket


# Create your views here.
@csrf_exempt
def del_user_history(request):
    """
    当用户点击了主页上的“Clear”按钮后会删除数据库中的记录同时删除服务器上存储的文件
    :param request:
    :return:
    """
    username = request.POST["username"]
    # 删除服务器上的用户记录
    UserFile.objects.filter(username=username).delete()
    # 删除服务器上用户目录中的文件
    user_dir = os.path.join(user_files, username)
    shutil.rmtree(user_dir)
    os.system("mkdir %s" % user_dir)
    return None


# 提交页面如果有running状态的history task就会websocket实时更新
# @accept_websocket
# def update_still_running_task(request):
#     if request.is_websocket():


