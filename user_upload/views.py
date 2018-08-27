from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .CONFIG import user_files, log_default_config
import os
import shutil
from .models import UserFile
from .forms import UploadForm
from django.utils import timezone
from .cookies import Cookies
# from .check_format import FormatChecker
from human_cancer_pro.views import test_result_elm2
from user_history.history_result import HistoryResult
import logging
import logging.config
import logging.handlers
import yaml
import threading


# Create your views here.
@csrf_protect
def user_upload(request):
    """
    用于对用户上传的数据进行处理。需要从COOKIE中获取uid（前提是用户之前访问过网站且没有清理COOKIE，如果没有则新建uid）。
    同时需要创建文件目录用于存放用户此次添加的数据。
    :param request:
    :return:
    """
    # 用于告知用户如何正确上传文件
    file_upload_rule = "为确保正常执行服务器预测功能，请按照如下任意形式上传文件:\n(1) 上传单独的一份elm格式文件。\n" \
                       "(2) 上传一份elm和一份vcf格式文件。\n(3) 上传一份elm和一份tab格式文件\n(4) 上传单独的vcf或tab格式文件并选取修饰类型。"
    history_record = HistoryResult.get_task_status(request)
    if request.method == "GET":
        obj = UploadForm()
        response = render(request, "user_upload/upload.html", {"form": obj, "file_upload_rule": file_upload_rule,
                                                               "user_history": history_record})
        return response

    # 设定上标记，查看是否有三类文件
    has_elm = False
    has_vcf = False
    has_tab = False
    form = UploadForm(request.POST)
    # 如果通过POST方法上传，但是数据不规范。则原样返回用户输入数据让其修改
    if request.method == "POST" and not form.is_valid():
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": form, "file_upload_rule": file_upload_rule})
        return response
# ------------------------如果用户提交的表单符合要求，则开始进一步的处理工作----------------------------------------------------
    webserver_name = "lysine"
# ------------------------首先创建或者获取之前已有的uid，并依据本次提交时间创建上传目录------------------------------------------
    # 从COOKIE中获取uid信息，如果没有uid则会创建一个新的uid
    uid = Cookies.check_cookies(request)
    # 开始对用户本次提交数据的目录进行设置
    cur_time = timezone.now()
    # 生成本次用户提交数据的存放位置，并通过系统命令生成上传目录
    dir_name = cur_time.strftime("%Y%m%d_%H%M%S")
    upload_path = os.path.join(user_files, uid, dir_name)
    os.makedirs(upload_path)

# -----------------------将用户的提交记录存储到数据库中，同时在用户目录下生成日志文件 -------------------------------------------
    # 同时在数据库中生成对应的UserFile记录
    uf = UserFile(username=uid, upload_time=cur_time, user_dir=upload_path)
    uf.save()
    # 获取日志对象，获取的同时用户目录中出现日志文件，名为 upload.log
    user_dir = os.path.join(user_files, uid)
    logger = setup_logging(user_dir=user_dir, default_config=log_default_config)

# -----------------------对用户表单中提交的数据进行验证，验证过程记录在日志中---------------------------------------------------
#     # 用户是否在文本框中输入数据
#     text_context = request.POST["input_text"]
#     if text_context:
#         # 如果input_text中有内容先判断属于哪类文本并保存。如果都不符合elm、vcf和Tab格式，则报错
#         try:
#             has_elm, has_vcf, has_tab = FormatChecker.textarea_handler(text_context, upload_path,
#                                                                        has_elm, has_vcf, has_tab, logger)
#         except RuntimeError:
#             # 如果格式不对会报出RuntimeError
#             response = render(request=request, template_name="user_upload/upload.html",
#                               context={"form": form, "input_text.error": "invalid format in textarea"})
#             response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
#             os.rmdir(upload_path)
#             logger.error("Invaild text input. Fail to upload.")
#             delete_user_record(upload_path)
#             return response

# ---------------------对用户提交的文件进行处理-----------------------------------------------

    # 处理完文本域中的内容后对用户上传的文件进行处理，保存后将相应的文件路径设置在COOKIE中
    elm_file = request.FILES.get("elm_file")
    vcf_file = request.FILES.get("vcf_file")
    tab_file = request.FILES.get("tab_file")
    file_upload_error = "File upload failed."
    if elm_file:
        # 如果之前用户已经在textarea中提交了elm文件，同时也上传了elm文件，此时报错，提醒用户一个文件只能交一次
        if has_elm:
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "elm_file.error": "you have already upload elm data in textarea",
                                       "file_upload_error": file_upload_error})
            logging.error("resubmit elm file, already upload it from textarea. Fail to upload.")
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            shutil.rmtree(upload_path)
            delete_user_record(upload_path)
            return response
        suffix = elm_file.name.split(".")[-1]
        if not suffix.lower() == "elm":
            # 在浏览器上显示文件后缀名不符合要求
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "elm_file_error": "invalid file's suffix",
                                       "file_upload_error": file_upload_error})
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            logging.error("Invalid elm file suffix. Fail to upload.")
            shutil.rmtree(upload_path)
            delete_user_record(upload_path)
            return response
        target_file = os.path.join(upload_path, "user.elm")
        save_user_file(elm_file, target_file)
        logging.debug("elm file upload completed.")
        has_elm = True

    if vcf_file:
        # 如果之前用户已经在textarea中提交了vcf文件，同时也上传了vcf文件，此时报错，提醒用户一个文件只能交一次
        if has_vcf:
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "vcf_file_error": "you have already upload vcf data in textarea",
                                       "file_upload_error": file_upload_error})
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            logging.error("resubmit vcf file, already upload it from textarea. Fail to upload.")
            delete_user_record(upload_path)
            shutil.rmtree(upload_path)
            return response
        suffix = vcf_file.name.split(".")[-1]
        if not suffix.lower() == "vcf":
            # 在浏览器上显示文件后缀名不符合要求
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "vcf_file_error": "invalid file's suffix",
                                       "file_upload_error": file_upload_error})
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            logging.error("Invalid vcf file suffix. Fail to upload.")
            delete_user_record(upload_path)
            shutil.rmtree(upload_path)
            return response
        target_file = os.path.join(upload_path, "user.vcf")
        save_user_file(vcf_file, target_file)
        logging.debug("vcf file upload completed.")
        has_vcf = True

    if tab_file:
        # 如果之前用户已经在textarea中提交了tab文件，同时也上传了tab文件，此时报错，提醒用户一个文件只能交一次
        if has_tab:
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "tab_file.error": "you have already upload tab data in textarea",
                                       "file_upload_error": file_upload_error})
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            logging.error("resubmit tab file, already upload it from textarea. Fail to upload.")
            delete_user_record(upload_path)
            shutil.rmtree(upload_path)
            return response
        suffix = tab_file.name.split(".")[-1]
        if not suffix.lower() == "tab":
            # 在浏览器上显示文件后缀名不符合要求
            response = render(request=request, template_name="user_upload/upload.html",
                              context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                       "tab_file_error": "invalid file's suffix",
                                       "file_upload_error": file_upload_error})
            response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
            logging.error("Invalid tab file suffix. Fail to upload.")
            delete_user_record(upload_path)
            shutil.rmtree(upload_path)
            return response
        target_file = os.path.join(upload_path, "user.tab")
        save_user_file(tab_file, target_file)
        logging.debug("tab file upload completed.")
        has_tab = True

    # 对用户上传的文件处理完成后检查用户提交的信息是否满足进行显著蛋白鉴定的条件
    has_modification = request.POST.get("modification")

    # 如果用户同时上传三种文件是无法对其进行预测的
    if has_elm and has_vcf and has_tab:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "file_upload_error": file_upload_error})
        logger.error("The specification requirement for file uploading have not been met. Fail to upload.")
        delete_user_record(upload_path)
        shutil.rmtree(upload_path)
        return response

    file_upload_success = "文件上传成功"
    # 形式1：用户提交vcf文件、elm文件
    if has_vcf and has_elm:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "upload_success": "上传成功，开始解析vcf、elm文件",
                                   "file_upload_success": file_upload_success})
    # 形式2：用户提交vcf文件和modification选项
    elif has_vcf and has_modification:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "upload_success": "上传成功，开始解析vcf文件",
                                   "file_upload_success": file_upload_success})
    # 形式3：用户提交tab文件和elm文件
    elif has_tab and has_elm:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "upload_success": "上传成功，开始解析tab、elm文件",
                                   "file_upload_success": file_upload_success})
    # 形式4：用户提交tab文件和modification选项
    elif has_tab and has_modification:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "upload_success": "上传成功，开始解析tab文件",
                                   "file_upload_success": file_upload_success})
    # 形式5：用户仅提交elm文件
    elif has_elm:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule,
                                   "upload_success": "上传成功，开始解析elm文件",
                                   "file_upload_success": file_upload_success})
    # 如果均不符合以上条件，则返回信息，告知用户至少需要提交哪些文件
    else:
        response = render(request=request, template_name="user_upload/upload.html",
                          context={"form": UploadForm(), "file_upload_rule": file_upload_rule})
        logging.error("not keep the file upload rule. Fail to upload.")
        delete_user_record(upload_path)
        shutil.rmtree(upload_path)
        return response
    # 对COOKIE信息进行更新，返回的response是一个HttpResponse类
    response = Cookies.set_cookies(uid=uid, webserver_name=webserver_name, response=response)
    u = UserFile.objects.get(user_dir=upload_path)
    u.save()
    logging.debug("successfully upload.")
    logging.shutdown()
    # 开启另一个子线程完成分析工作
    t = ThreadAnalysis(func=test_result_elm2, args=request)
    t.start()
    return response


def save_user_file(files, target_file):
    """
    对用户上传的文件进行存储
    :param files: 传入的request.FILES["name"]得到的内存中的文件
    :param target_file: 文件的存放路径
    :return:
    """
    # 如果用户是通过 <input type="file" name="" /> 标签上传的文件，需要通过request.FILES["name"]进行提取，FILES中的每个键为标签中
    # name属性的值
    files = files.read()
    # 这里使用“wb”模式是因为内存中文件是以字节形式存放的
    with open(target_file, "wb") as destination:
        destination.write(files)


def setup_logging(user_dir, default_config):
    """
    用于创建用户的上传日志。返回的是一个logger对象。
    :param user_dir: 用户目录。
    :param default_config: 默认的日志配置文件。
    :return:
    """
    log_file = os.path.join(user_dir, "upload.log")
    with open(log_file, "w") as f:
        f.write("")
    local_dir = os.path.dirname(os.path.realpath(__file__))
    default_config = os.path.join(local_dir, default_config)
    with open(default_config, "r", encoding="utf-8") as f:
        config = yaml.load(f)
        config["handlers"]["upload_file_handler"]["filename"] = log_file
        logging.config.dictConfig(config)
    logger = logging.getLogger("uploadProcess")
    return logger


# 定制一个线程类，使得分析用户上传文件的任务能够在另一个线程中执行，主线程可以不等待其执行完
class ThreadAnalysis(threading.Thread):
    def __init__(self, func, args):
        super(ThreadAnalysis, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(self.args)


def delete_user_record(upload_dir):
    """
    当用户上传数据失败的时候删除该条上传记录
    :param upload_dir: 本次上传的路径
    :return:
    """
    u = UserFile.objects.get(user_dir=upload_dir)
    u.delete()
