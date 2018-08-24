# -*-coding: utf-8 -*-
import os
import time
from .CONFIG import users_dir
import logging


class UploadLogChecker:
    def __init__(self, username):
        self.upload_log = os.path.join(users_dir, username, "upload.log")
        self.check_res = None

    def check_log(self):
        while True:
            if not os.path.exists(self.upload_log):
                time.sleep(1)
                continue
            else:
                with open(self.upload_log, "r") as f:
                    content = f.read()
            if "Fail to upload." in content:
                self.check_res = False
                break
            elif "successfully upload." in content:
                self.check_res = True
                break
            else:
                time.sleep(1)
                continue

