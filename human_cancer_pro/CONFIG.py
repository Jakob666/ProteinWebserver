# -*- coding:utf-8 -*-
"""
用于将整个应用相关的所有环境变量存储在一个文件中
"""
import os
app_dir = os.path.dirname(os.path.realpath(__file__))
# 连接的数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lysine',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '123456',
        'PORT': 3308,
    }
}

# annovar软件地址
annovar_variant = "/CLS/sysu_rj_1/software/annovar/annotate_variation.pl"

# 存放人类蛋白质序列信息的表
sequence_table = "human_protein_sequence"

# 存放人类蛋白质突变记录的表（数据仅来源于TCGA）
mutation_table = "human_mutation"

# 用于存放人类蛋白质模体区域的表
motif_table = "motif_table"

# 人类蛋白质refseq与uniprot进行匹配所用的表
red2uni_table = "human_ref2uni"

# 存放各类修饰的上下游模体长度的json文件
modification_file = os.path.join(app_dir, "modification.json")

# 日志配置文件的文件名
log_file_config = "logging.conf.yaml"

# 给管理员发送文件的邮件配置信息
send_to_admin = {
    "from_addr": "admin@renlab.org", "password": "renlab#322",  "smtp_server": "server.targetgene.com",
    "admin_addr": ["826850754@qq.com"]
}
