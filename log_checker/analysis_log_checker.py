# -*-coding: utf-8 -*-
import os
import time
from .CONFIG import users_dir
import logging


class AnalysisLogChecker:
    def __init__(self, username):
        files = os.listdir(os.path.join(users_dir, username))
        files.remove("upload.log")
        mtimes = [os.path.getmtime(os.path.join(users_dir, username, f)) for f in files]
        latest_upload = files[mtimes.index(max(mtimes))]

        self.analysis_log = os.path.join(users_dir, username, latest_upload, "analysis.log")
        self.check_res = None

    def check_log(self):
        while True:
            if not os.path.exists(self.analysis_log):
                time.sleep(1)
                continue
            else:
                with open(self.analysis_log, "r") as f:
                    content = f.read()
            if "analysis interrupted" in content:
                self.check_res = False
                break
            elif "analysis complete." in content:
                self.check_res = True
                break
            else:
                time.sleep(1)
                continue

