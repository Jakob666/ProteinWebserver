from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .upload_log_checker import UploadLogChecker
from .analysis_log_checker import AnalysisLogChecker
import logging


# Create your views here.
def check_logs(request):
    username = request.POST.get("username", None)
    logging.warning(username)
    upload_handler = UploadLogChecker(username=username)
    upload_handler.check_log()
    logging.warning(upload_handler.check_res)
    if not upload_handler.check_res:
        return HttpResponse(json.dumps({"log_result": upload_handler.check_res}, ensure_ascii=False))
    analysis_handler = AnalysisLogChecker(username=username)
    analysis_handler.check_log()
    logging.warning(analysis_handler.check_res)
    if analysis_handler.check_res:
        return HttpResponse(json.dumps({"log_result": analysis_handler.check_res}, ensure_ascii=False))
