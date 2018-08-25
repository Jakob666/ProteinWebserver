# -*- coding: utf-8 -*-
"""
@author: hbs
@date: 2018-8-20
description:
    当用户上传文件并开始对文件进行处理时，如果日志中出现 annovar error的字样，说明服务器的annovar配置出现问题，此时应该给网站管理员
    发送邮件。
"""
import smtplib
from email.mime.text import MIMEText
import time
import os
from .CONFIG import send_to_admin


class Mail2Admin:
    @staticmethod
    def read_logging(upload_dir):
        """
        对日志文件进行读取，查看是否有annovar error
        :param upload_dir: 用户最近一次上传的文件所在的目录
        :return:
        """
        log_file = os.path.join(upload_dir, "analysis.log")
        annovar_error = False
        f = open(log_file, "r")
        content = f.read()
        f.close()
        if "annovar error." in content:
            annovar_error = True
        return annovar_error

    @staticmethod
    def send_mail():
        """
        给管理员发邮件提示服务器的annovar注释软件有问题
        :return:
        """
        smtp_server = send_to_admin["smtp_server"]
        from_addr = send_to_admin["from_addr"]
        password = send_to_admin["password"]
        to_addr = send_to_admin["admin_addr"]

        # 定义文本信息
        mail_body = "服务器上Lysine webserver使用的annovar软件出现问题，请及时解决"
        msg = MIMEText(mail_body)
        # 定义邮件标题
        msg["Subject"] = "webserver服务异常"
        msg["From"] = from_addr
        msg["To"] = ";".join(send_to_admin["admin_addr"])
        msg["date"] = time.strftime("%a, %d %b %Y %H: %M: %S %z")
        server = smtplib.SMTP()
        server.connect(smtp_server)
        try:
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())

        except smtplib.SMTPException:
            print("Error:Can not send E-mail")
            exit()
        finally:
            server.quit()
        return None
