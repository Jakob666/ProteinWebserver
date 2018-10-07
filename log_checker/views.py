from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
# from .upload_log_checker import UploadLogChecker
from .analysis_log_checker import AnalysisLogChecker


# Create your views here.
# 必需加上这个修饰器，否则ajax post过来会产生403错误
@csrf_exempt
def check_logs(request):
    username = request.POST.get("username", None)
    # 因为流程有变动，这部分提交过程日志的代码现在不需要了。留着万一以后有用
    # upload_handler = UploadLogChecker(username=username)
    # check_res = upload_handler.check_log()
    # if not check_res:
    #     return HttpResponse(json.dumps({"log_result": check_res}, ensure_ascii=False))
    analysis_handler = AnalysisLogChecker(username=username)
    check_res = analysis_handler.check_log()
    return HttpResponse(json.dumps({"log_result": check_res}, ensure_ascii=False))
