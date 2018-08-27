# -*-coding: utf-8 -*-
import os
import time
from .CONFIG import users_dir


class UploadLogChecker:
    def __init__(self, username):
        self.upload_log = os.path.join(users_dir, username, "upload.log")

    def check_log(self):
        while True:
            if not os.path.exists(self.upload_log):
                time.sleep(1)
                continue
            else:
                with open(self.upload_log, "r") as f:
                    content = f.read()
            # 出现 finish checking 说明新的日志还没录入
            if "finish checking" in content:
                time.sleep(1)
                continue
            # 出现 Fail to upload 说明上传失败
            elif "Fail to upload." in content:
                check_res = False
                break
            # 出现 successfully upload 说明上传成功
            elif "successfully upload." in content:
                check_res = True
                break
            # 如果上面的情况都没有出现说明日志正在录入，但是没有录入完成
            else:
                time.sleep(1)
                continue
        with open(self.upload_log, "a") as f:
            f.write("finish checking")
        return check_res

