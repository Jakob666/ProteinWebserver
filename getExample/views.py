from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from .CONFIG import examples_dir


# Create your views here.
def get_example(request):
    target_file = None
    example_type = request.POST.get("exampleType", None)
    if example_type == "elm exmple":
        target_file = os.path.join(examples_dir, "example.elm")
    elif example_type == "vcf exmple":
        target_file = os.path.join(examples_dir, "example.vcf")
    elif example_type == "tab exmple":
        target_file = os.path.join(examples_dir, "example.tab")
    content = load_file(target_file)
    return HttpResponse(content)


def load_file(file):
    with open(file, "r") as f:
        content = f.read()

    return content

