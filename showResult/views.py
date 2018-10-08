from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .CONFIG import users_dir
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
        summary.append([protein, stats["motif_length"], stats["background_length"], stats["significance"], stats["p_value"]])

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

    log_file = [os.path.join(latest_upload, f) for f in os.listdir(latest_upload) if f.endswith("log")][0]
    with open(log_file, "r") as f:
        content = f.read()

    if "annovar error." in content:
        reason = "Error in analysis variants from VCF file. This problem had already sent to the administator."

    elif "contains no nonsynonymous variant." in content:
        reason = "VCF information without any SNV site. The further analysis interrupted."

    elif "can't match refseq to uniprot." in content:
        reason = "Can't match the Uniprot Accession to RefSeq ID. The further analysis interrupted."

    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    response.write(json.dumps({"fail_reason": reason}, ensure_ascii=False))

    return response

