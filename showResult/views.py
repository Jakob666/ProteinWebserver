from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .CONFIG import users_dir
from user_upload.models import UserFile
import datetime
import os


# Create your views here.
@csrf_exempt
def success_analysis(request):
    """
    当分析成功后解读结果文件
    :param request:
    :return:
    """
    username = request.POST["username"]
    # 通过用户名得到用户最新上传的文件的目录
    files = os.listdir(os.path.join(users_dir, username))
    files.remove("upload.log")
    mtimes = [os.path.getmtime(os.path.join(users_dir, username, f)) for f in files]
    latest_upload = os.path.join(users_dir, username, files[mtimes.index(max(mtimes))])

    result_list, row_num, summary = load_completed_result(latest_upload)

    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    response.write(json.dumps({"test_result": result_list, "row_num": row_num,
                               "summary": summary}, ensure_ascii=False))

    return response


@csrf_exempt
def fail_analysis(request):
    """
    当分析失败时解读analysis.log日志文件分析出失败原因
    :return:
    """
    username = request.POST["username"]
    # 通过用户名得到用户最新上传的文件的目录
    files = os.listdir(os.path.join(users_dir, username))
    files.remove("upload.log")
    mtimes = [os.path.getmtime(os.path.join(users_dir, username, f)) for f in files]
    latest_upload = os.path.join(users_dir, username, files[mtimes.index(max(mtimes))])

    reason = check_file_log(latest_upload)

    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    response.write(json.dumps({"fail_reason": reason}, ensure_ascii=False))

    return response


def view_history(request, upload_time, status):
    # upload_time的形式为 2018-10-08 14:07:32
    y_m_d, h_m_s = upload_time.split(" ")
    year, month, day = list(map(int, y_m_d.split("-")))
    hour, minute, second = list(map(int, h_m_s.split(":")))

    res = UserFile.objects.get(upload_time__contains=datetime.datetime(year, month, day, hour, minute, second))
    upload_dir = str(res.user_dir)
    user_name = os.path.split(os.path.split(upload_dir)[-2])[-1]

    if status == "completed":
        result_list, row_num, summary = load_completed_result(upload_dir)
        print(summary)
        response = render(request, "showResult/view_history.html", context={
            "user_name": user_name, "submit_time": upload_time, "status": status, "test_result": result_list,
            "summary": summary,
        })
        return response

    elif status == "error":
        reason = check_file_log(upload_dir)
        response = render(request, "showResult/view_history.html", context={
            "user_name": user_name, "submit_time": upload_time, "task_status": status, "fail_reason": reason,
        })
        return response


def check_file_log(target_dir):
    log_file = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith("log")][0]
    with open(log_file, "r") as f:
        content = f.read()

    if "annovar error." in content:
        reason = "Error in analysis variants VCF file. This problem had already sent to the administator."

    elif "contains no nonsynonymous variant." in content:
        reason = "VCF information without any SNV site. The further analysis interrupted."

    elif "can't match refseq to uniprot." in content:
        reason = "Can't match the Uniprot Accession to RefSeq ID. The further analysis interrupted."

    return reason


def load_completed_result(target_dir):
    result_file = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith("json")][0]
    with open(result_file, "r") as f:
        data = json.load(f)

    result_list = []
    summary = []
    # data中有两个key，分别是 cancer和 test_res。
    test_res = data["test_res"]
    proteins = test_res.keys()
    for protein in proteins:
        stats = test_res[protein]
        summary.append(
            [protein, stats["motif_length"], stats["background_length"], stats["significance"], stats["p_value"]])

        # motif_mutation和 background_mutation的形式都是list，list中每一个元素的形式为
        # [cancer, uniprot, position, from, to, patient_id, count]
        background_mutation = test_res[protein]["background_mutation"]
        for bm in background_mutation:
            bm.insert(2, "out motif")
            result_list.append(bm[: -1])
        motif_mutation = test_res[protein]["motif_mutation"]
        for mm in motif_mutation:
            mm.insert(2, "in motif")
            result_list.append(mm[: -1])
    row_num = len(result_list)

    return result_list, row_num, summary
