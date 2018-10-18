from django.shortcuts import render


# Create your views here.
def contact(request):
    return render(request, template_name="general/contact.html")


def citation(request):
    return render(request, template_name="general/citation.html")


def help_site(request):
    return render(request, template_name="general/help.html")


def homepage(request):
    return render(request, template_name="general/index.html")
