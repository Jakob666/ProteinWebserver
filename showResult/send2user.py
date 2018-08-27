# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-8-27
description:
    如果用户上传文件的时候输入了邮箱则将最终的结果发送到用户邮箱
"""
import smtplib
import email


class Send2User:
    @staticmethod
    def send_to_user(server_info, user_email):
        smtp_server = server_info["smtp_server"]
        from_addr = server_info["from_addr"]
        password = server_info["password"]
        to_addr = user_email
        msg = None

        server = smtplib.SMTP()
        server.connect(smtp_server)
        try:
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg)
        except smtplib.SMTPException:
            print("无法发送邮件到用户")
        finally:
            server.quit()
        return None

