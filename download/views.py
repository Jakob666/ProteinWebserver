# -*- coding:utf-8 -*-
# 这里使用StreamingHTTPResponse的目的是发送文件流
from django.http import StreamingHttpResponse
from user_upload.models import UserFile
from .CONFIG import users_dir
import json
import os


# Create your views here.
def download_latest_result(request, username):
    # 通过用户名得到用户最新上传的文件的目录
    files = os.listdir(os.path.join(users_dir, username))
    files.remove("upload.log")
    mtimes = [os.path.getmtime(os.path.join(users_dir, username, f)) for f in files]
    latest_upload = os.path.join(users_dir, username, files[mtimes.index(max(mtimes))])

    result_file = [os.path.join(latest_upload, f) for f in os.listdir(latest_upload) if f.endswith("json")][0]
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

    # summary = "\n".join(["\t".join(i) for i in summary])
    for i in range(len(result_list)):
        result_list[i] = list(map(str, result_list[i]))
    details = "\n".join(["\t".join(i) for i in result_list])

    download_filename = "%s_result.tsv" % username
    response = StreamingHttpResponse(details)

    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = 'attachment;filename="{0}"'.format(download_filename)

    return response


def history_download(request, username, submit_time):
    print(submit_time)
    # history_dir = UserFile.objects.get()



