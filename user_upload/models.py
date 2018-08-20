from django.db import models
import django.utils.timezone as timezone
import time


# 定义UserFile类
class UserFile(models.Model):
    """
    定义用户文件类，用于记录某个用户在上传时间上传某个文件。对于后续提取文件和定期删除文件是十分必要的。
    """
    username = models.CharField(max_length=30)
    # UserFile的每一条记录默认是当前时间
    upload_time = models.DateTimeField(default=timezone.now())
    # 每个用户会有一个用户目录，每次提交会在当前时刻创建目录用于存放文件
    user_dir = models.FileField()
    # 一个时间值，用于后续定期删除工作
    visit_time = models.BigIntegerField(default=time.time())

    # 是否上传成功，成功是1，反之为0
    upload_success = models.IntegerField(default=0)

    class Meta:
        db_table = "user_record"

    def __str__(self):
        return "%s -> %s" % (self.username, self.user_dir)

