# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


# 这个表单类还得改，在每个field中添加widget参数形式为  widget=forms.XXXInput(attrs={"class": "XXX", "placeholder": "XXX"})
# attrs中都是CSS和bootstrap的形式
class UploadForm(forms.Form):
    # 用户输入elm、vcf或者Tab格式文本的文本框
    input_text = forms.CharField(label="data input", required=False,
                                 widget=forms.Textarea(attrs={"class": "form-control input-xlarge", "rows": 10}))
    # 上传elm、vcf和Tab文件的表单元素
    elm_file = forms.FileField(label="elm file", required=False, widget=forms.ClearableFileInput(
        attrs={"type": "file", "id": "elm_upload", "value": "browse"}))
    vcf_file = forms.FileField(label="vcf file", required=False)
    tab_file = forms.FileField(label="Tab file", required=False)
    # 物种选项，暂定会有多个物种，返回类型是字符串
    organism = forms.ChoiceField(label="Organism*", choices=(("human", "Homo sapiens"), ("mouse", "Mus musculus"),),
                                 required=True, initial="human", widget=forms.Select(attrs={"class": "radio-inline"}))
    # 修饰类型选项，返回类型是列表
    modification = forms.MultipleChoiceField(label="Modification",
                                             choices=(("Acethylation", "Acethylation"), ("Glycation", "Glycation"),
                                                      ("Malonylation", "Malonylation"),),
                                             required=False, initial=["Acethylation", ],
                                             widget=forms.SelectMultiple(attrs={"class": "selectpicker"}))
    # , widget=forms.widgets.SelectMultiple
    # 癌症类型，只有在物种选定为人的时候才有效，返回类型是列表
    cancer = forms.MultipleChoiceField(label="Cancer",
                                       choices=(("BRCA", "BRCA"), ("UCSC", "UCSC")), required=False, initial=["BRCA", ],
                                       widget=forms.widgets.SelectMultiple(attrs={"class": "selectpicker"}))
    # 阈值选取
    threshold = forms.ChoiceField(label="Threshold*",
                                  choices=(("h", "High"), ("m", "Medium"), ("l", "Low"),), required=True, initial=1,
                                  widget=forms.widgets.Select)
    # 填写用户的email
    email = forms.EmailField(label="E-mail address(Optional)", required=False)

    # 使用bootstrap对表单进行渲染和布局
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.layout = Layout(
        Field("input_text", css_class="input-xlarge"),
        "elm_file",
        "vcf_file",
        "tab_file",
        "organism",
        "modification",
        Field("cancer", css_class="selectpicker"),
    )

