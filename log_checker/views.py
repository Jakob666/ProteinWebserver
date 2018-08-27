from django.http import HttpResponse
import json
from .upload_log_checker import UploadLogChecker
from .analysis_log_checker import AnalysisLogChecker


# Create your views here.
def check_logs(request):
    username = request.POST.get("username", None)
    upload_handler = UploadLogChecker(username=username)
    check_res = upload_handler.check_log()
    if not check_res:
        return HttpResponse(json.dumps({"log_result": check_res}, ensure_ascii=False))
    analysis_handler = AnalysisLogChecker(username=username)
    check_res = analysis_handler.check_log()
    return HttpResponse(json.dumps({"log_result": check_res}, ensure_ascii=False))
