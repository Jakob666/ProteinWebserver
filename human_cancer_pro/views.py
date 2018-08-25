from django.shortcuts import render
from django.http import HttpResponse
from .test_for_elm.test_significant import SignificanceTest
from .test_for_elm.get_mutation_info import GetMutationInfo
from .test_for_vcf.vcf2avinput import Vcf2Avinput
from .test_for_vcf.annovar_annotate import AnnovarAnnotate
from .test_for_vcf.get_mutation_vcf import GetMutationVCF
from .test_for_tab.tab2avinput import Tab2Avinput
from user_upload.CONFIG import user_files
from .CONFIG import log_file_config
from .mail2admin import Mail2Admin
import os
import numpy as np
import pandas as pd
import warnings
from operator import itemgetter
import logging
import logging.config
import logging.handlers
import yaml
import json
from collections import ChainMap


# Create your views here.
def get_mutate_elm(request):
    """
    调用test_for_elm中get_mutation_info的GetMutationInfo类从用户提交的elm文件获取突变信息
    :param request:
    :return:
    """
    warnings.filterwarnings("ignore")
    g = GetMutationInfo()
    area_len, motif_mut, background_mut = g.main("C:/Users/hbs/Desktop/lysine/test_user.elm", "BRCA")
    res = np.array(background_mut).tolist()
    string = ""
    for i in res:
        info = list(map(str, i))
        info = "\t".join(info)
        string += info + "\n"
    return HttpResponse(string)


def test_result_elm(request):
    """
    通过对用户提取的elm文件进行突变数据的提取，使用之前的算法检验用户提交的elm
    蛋白是否是显著突变蛋白。
    :param request:
    :return:
    """
    warnings.filterwarnings("ignore")
    g = GetMutationInfo()
    area_len, motif_mut, background_mut = g.main("C:/Users/hbs/Desktop/lysine/test_user.elm", "BRCA")
    s = SignificanceTest(motif_mut, background_mut, area_len)
    s.get_result()
    s.test_res.sort(key=itemgetter("p_value"))
    res = "\n".join(["\t".join(list(map(str, i.values()))) for i in s.test_res])
    return HttpResponse(res)


def test_result_elm2(request):
    warnings.filterwarnings("ignore")
    # 通过cookie中cname（形式为lysine=XXX，其中XXX是uid），通过uid得到用户目录和日志文件
    uid = request.COOKIES["cname"].split("=")[1]
    user_dir = os.path.join(user_files, uid)
    upload_log = os.path.join(user_dir, "upload.log")
    # 对用户目录的upload.log文件进行解读，如果之前用户上传失败就直接退出不进行后续分析
    has_elm, has_vcf, has_tab = None, None, None
    try:
        has_elm, has_vcf, has_tab = judge_from_upload_log(upload_log)
    except RuntimeError:
        exit()

    # 获取用户目录下最新建的文件目录，该目录是本次用户提交文件所生成的目录
    files = os.listdir(user_dir)
    files.remove("upload.log")
    mtimes = [os.path.getmtime(os.path.join(user_dir, f)) for f in files]
    latest_upload = files[mtimes.index(max(mtimes))]

    # 进行分析工作之前先创建日志对象
    logger = setup_logging(os.path.join(user_dir, latest_upload), default_config=log_file_config)
    logger.debug(has_elm)
    logger.debug(has_vcf)
    logger.debug(has_tab)

    # 获取POST方式提交的数据，其中modification是list形式， organism是字符串形式， threshold是字符串形式， cancer是list形式
    modification = request.POST.getlist("modification")
    logger.debug("\t".join(modification))
    organism = request.POST["organism"]
    logger.debug(organism)
    threshold = request.POST["threshold"]
    cancer = request.POST.getlist("cancer")
    logger.debug("\t".join(cancer))
    email = request.POST["email"]
    elm_file = os.path.join(user_dir, latest_upload, "user.elm")
    vcf_file = os.path.join(user_dir, latest_upload, "user.vcf")
    tab_file = os.path.join(user_dir, latest_upload, "user.tab")
    # （1）同时上传elm和vcf文件
    if has_elm and has_vcf:
        logger.debug("analysis elm and vcf file")
        testing(user_dir=user_dir, latest_upload=latest_upload, logger=logger, organism=organism, elm_file=elm_file,
                vcf_file=vcf_file, cancer=cancer)

    # （2）同时上传elm和tab文件
    elif has_elm and has_tab:
        logger.debug("analysis elm and tab file")
        testing(user_dir=user_dir, latest_upload=latest_upload, logger=logger, organism=organism, elm_file=elm_file,
                tab_file=tab_file, cancer=cancer)

    # （3）仅上传vcf文件，同时点选modification选项
    elif has_vcf and modification:
        logger.debug("analysis vcf file and ticjed modifications")
        testing(user_dir=user_dir, latest_upload=latest_upload, logger=logger, organism=organism, vcf_file=vcf_file,
                modification=modification, cancer=cancer)

    # （4）仅上传tab文件，同时点选modification选项
    elif has_tab and modification:
        logger.debug("analysis tab file and ticjed modifications")
        testing(user_dir=user_dir, latest_upload=latest_upload, logger=logger, organism=organism, tab_file=tab_file,
                modification=modification, cancer=cancer)

    # （5）仅上传elm文件
    elif has_elm:
        logger.debug("only analysis elm file")
        g = GetMutationInfo()
        result = {}
        if organism == "human":
            for c in cancer:
                area_len, motif_mut, background_mut = g.main(elm_file, c)
                s = SignificanceTest(motif_mut, background_mut, area_len)
                s.get_result()
                res = {"cancer": c, "test_res": s.test_res}
                result = dict(ChainMap(result, res))
        else:
            area_len, motif_mut, background_mut = g.main(elm_file)
            area_len.to_csv(os.path.join(user_dir, latest_upload, "area_len.txt"), sep="\t", index=False, mode="a")
            s = SignificanceTest(motif_mut, background_mut, area_len)
            s.get_result()

        with open(os.path.join(user_dir, latest_upload, "res.json"), "w") as f:
            json.dump(result, f, indent=4)
    logger.debug("analysis complete.")
    logging.shutdown()

    return None


def annotate_for_vcf_and_tab(user_dir, latest_upload, logger, vcf_file=None, tab_file=None):
    """
    将用户提交的vcf文件或tab文件进行注释并解析成最终的vcf_annotated.tsv文件。
    :param user_dir: 用户目录
    :param latest_upload: 用户本次提交的数据存放的目录
    :param vcf_file: 用户提交的vcf文件
    :param tab_file: 用户提交的tab文件
    :param logger: 日志对象
    :return:
    """
    target_dir = os.path.join(user_dir, latest_upload)
    avinput_file = os.path.join(user_dir, latest_upload, "user.avinput")
    if vcf_file:
        # 通过Vcf2Avinput对象对vcf文件格式进行转换，形成annovar需要的avinput文件
        v2a = Vcf2Avinput(vcf_file=vcf_file, avin_file=avinput_file)
        v2a.vcf2avin()
        logger.debug("vcf to avinput, done")
    if tab_file:
        # 通过Tab2Avinput对象对tab文件格式进行转换，形成annovar需要的avinput文件
        t2a = Tab2Avinput(tab_file=tab_file, avin_file=avinput_file)
        t2a.tab2avin()
        logger.debug("tab to avinput, done")
    # AnnovarAnnotate类对象对avinput文件进行注释，如果annovar注释失败（可能是本地的annovar软件出问题了），会报出RuntimeError
    try:
        AnnovarAnnotate.annotate(user_dir=target_dir,  avinput_file=avinput_file)
        logger.debug("annovar annotate, done")
    except RuntimeError:
        logger.error("annovar error.")
        return False
    # 如果没出问题则继续对annovar注释文件进行提取，annovar_res是list形式
    annovar_res = AnnovarAnnotate.variant_process(user_dir=target_dir)
    # 如果返回的结果list为空，说明vcf记录的突变中不存在非同义突变
    if not annovar_res:
        logger.error("contains no nonsynonymous variant.")
        return False
    # 注释文件中是refseq号，需要匹配其Uniprot号。如果比对的结果为空，会报出RuntimeError
    try:
        AnnovarAnnotate.match2uniport(annovar_res, user_dir=target_dir)
    except RuntimeError:
        logger.error("can't match refseq to uniprot.")
        return False
    return True


def tsv_test_res(annotate_file, ticked_modify, elm_file, cancer):
    """
    vcf或tab文件处理得到的avinput文件经过注释后，结果存放在vcf_annotated.tsv文件中，根据该文件中的信息对蛋白质进行预测
    :param annotate_file: tsv文件的存放路径
    :param ticked_modify: 用户通过表单上传的modification选项
    :param elm_file: 用户上传的注释修饰位点的elm文件
    :param cancer: 用户通过表单上传的cancer选项
    :return:
    """
    mut_data, modify_position = GetMutationVCF.get_motif_range(annotate_file=annotate_file, modify_position_file=elm_file,
                                                               ticked_modify=ticked_modify, cancer_type=cancer)

    motif_area, area_len = GetMutationVCF.get_motif_area(modify_position)
    motif_mut, background_mut = GetMutationVCF.mut_location(mut_data, motif_area)
    # 找到修饰和背景域的交集，common的形式类似于 {('O14977', 'Acetylation'), ('Q9Y266', 'Glycation'), ……}
    common = set(zip(motif_mut["Uniprot Accession"], motif_mut["Type"])) & set(
        zip(background_mut["Uniprot Accession"], background_mut["Type"]))
    test_result = []
    for protein, modification in common:
        in_motif_mut = motif_mut[motif_mut["Uniprot Accession"] == protein]
        in_motif_mut = in_motif_mut[in_motif_mut["Type"] == modification]
        in_background = background_mut[background_mut["Uniprot Accession"] == protein]
        in_background = in_background[in_background["Type"] == modification]
        motif = area_len[area_len["Uniprot Accession"] == protein]
        motif = motif[motif["Type"] == modification]
        s = SignificanceTest(in_motif_mut, in_background, motif)
        s.get_result()
        test_result.extend(s.test_res)
    res = "\n".join(["\t".join(list(map(str, i.values()))) for i in test_result])
    return HttpResponse(res)


def testing(user_dir, latest_upload, logger, organism, elm_file=None, vcf_file=None,
            tab_file=None, modification=None, cancer=None):
    """
    根据用户上传的文件进行测试。
    :param user_dir: 用户目录
    :param latest_upload: 最新的上传文件的目录
    :param logger: 日志对象
    :param organism: 用户通过表单提交的物种信息
    :param elm_file: 用户提交的elm文件的路径
    :param vcf_file: 用户提交的vcf文件的路径
    :param tab_file: 用户提交的tab文件的路径
    :param modification: 用户提交的修饰类型的list
    :param cancer: 用户提交的癌症的list
    :return:
    """
    # 首先需要对tab文件进行处理，生成avinput文件后对其进行annovar注释。Mail2Admin是监测服务器的annovar软件是否出问题，出错会给管理发邮件
    res = annotate_for_vcf_and_tab(user_dir, latest_upload, logger, vcf_file, tab_file)
    alert = Mail2Admin.read_logging(os.path.join(user_dir, latest_upload))
    if alert:
        Mail2Admin.send_mail()
    if not res:
        logger.error("analysis interrupted, failed")
        exit()
    tsv_file = os.path.join(user_dir, latest_upload, "vcf_annotated.tsv")
    if organism == "human":
        for c in cancer:
            tsv_test_res(tsv_file, ticked_modify=modification, elm_file=elm_file, cancer=c)
    else:
        tsv_test_res(tsv_file, ticked_modify=modification, elm_file=elm_file, cancer=None)
    logger.debug("analysis complete.")


def get_mutate_vcf(request):
    """
    对用户提交的VCF文件进行处理，并从中提取出修饰区内外的突变位点
    :param request:
    :return:
    """
    warnings.filterwarnings("ignore")
    mut_data, modify_position = GetMutationVCF.get_motif_range(
        annotate_file="C:/Users/hbs/Desktop/lysine/vcf_annotated.tsv",
        ticked_modify=["Acetylation", "Glycation"],
        cancer_type="BRCA")

    motif_area, area_len = GetMutationVCF.get_motif_area(modify_position)
    motif_mut, background_mut = GetMutationVCF.mut_location(mut_data, motif_area)
    # 找到修饰和背景域的交集，common的形式类似于 {('O14977', 'Acetylation'), ('Q9Y266', 'Glycation'), ……}
    common = set(zip(motif_mut["Uniprot Accession"], motif_mut["Type"])) & set(
        zip(background_mut["Uniprot Accession"], background_mut["Type"]))
    test_result = []
    for protein, modification in common:
        in_motif_mut = motif_mut[motif_mut["Uniprot Accession"] == protein]
        in_motif_mut = in_motif_mut[in_motif_mut["Type"] == modification]
        in_background = background_mut[background_mut["Uniprot Accession"] == protein]
        in_background = in_background[in_background["Type"] == modification]
        motif = area_len[area_len["Uniprot Accession"] == protein]
        motif = motif[motif["Type"] == modification]
        s = SignificanceTest(in_motif_mut, in_background, motif)
        s.get_result()
        test_result.extend(s.test_res)
    res = "\n".join(["\t".join(list(map(str, i.values()))) for i in test_result])
    return HttpResponse(res)


def setup_logging(user_dir, default_config):
    """
    用于创建用户的上传日志。返回的是一个logger对象。
    :param user_dir: 用户目录。
    :param default_config: 默认的日志配置文件。
    :return:
    """
    local_dir = os.path.dirname(os.path.realpath(__file__))
    default_config = os.path.join(local_dir, default_config)
    with open(default_config, "r", encoding="utf-8") as f:
        config = yaml.load(f)
        log_file = os.path.join(user_dir, "analysis.log")
        config["handlers"]["analysis_file_handler"]["filename"] = log_file
        logging.config.dictConfig(config)
    logger = logging.getLogger("analysisProcess")
    return logger


def judge_from_upload_log(upload_log):
    """
    对用户提交时生成的upload.log文件进行解读，查验用户是否上传成功，如果成功又上传了哪些文件。
    :param upload_log: 用户目录中upload目录upload.lg文件的路径
    :return:
    """
    has_elm, has_vcf, has_tab = False, False, False
    while True:
        # 如果用户目录的log日志不存在，可能是ajax没有异步完成，等待之后生成即可。如果存在log日志则读取其中的信息
        if not os.path.exists(upload_log):
            continue
        else:
            with open(upload_log, "r", encoding="utf-8") as log:
                log_content = log.read()
            # 如果出现 successfully upload，说明上传成功
            if "successfully upload." in log_content:
                break
            # 如果日志的内容中出现 Fail to upload的字样，则说明本次上传文件失败，不进行后续的预测。
            elif "Fail to upload." in log_content:
                raise RuntimeError("upload failed")
            else:
                continue

    # 通过日志内容获取本次用户提交了那些文件
    if "elm file upload completed." in log_content:
        has_elm = True
    if "vcf file upload completed." in log_content:
        has_vcf = True
    if "tab file upload completed." in log_content:
        has_tab = True

    return has_elm, has_vcf, has_tab
