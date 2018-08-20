# -*- coding: utf-8 -*-
"""
@author: hbs
@date: 2018-8-13
description:
    用于查看用户在文本框输入的数据是否属于 elm、vcf和Tab格式中的一种，
    如果是相应的一种，则存储为相应后缀名的文件，反之，报错。
    需要安装pyvcf模块，该模块用于检验vcf文件的格式。
"""
import os
import re
import vcf


class FormatChecker:
    @staticmethod
    def textarea_handler(input_text, upload_dir, has_elm, has_vcf, has_tab, logger):
        """

        :param input_text:
        :param upload_dir:
        :param has_elm:
        :param has_vcf:
        :param has_tab:
        :param logger:
        :return:
        """
        tempfile = os.path.join(upload_dir, "user.temp")
        with open(tempfile, "w") as f:
            f.write(input_text)
        # 检验是否是vcf格式
        res = FormatChecker.check_vcf_format(tempfile=tempfile)
        if res:

            os.rename(tempfile, os.path.join(upload_dir, "user.vcf"))
            logger.debug("vcf file upload completed.")
            has_vcf = True
        else:
            # 检查是否是elm格式
            res = FormatChecker.check_elm_format(tempfile)
            if res:
                os.rename(tempfile, os.path.join(upload_dir, "user.elm"))
                logger.debug("elm file upload completed.")
                has_elm = True
            else:
                # 检查是否是tab格式
                res = FormatChecker.check_elm_format(tempfile)
                if res:
                    os.rename(tempfile, os.path.join(upload_dir, "user.tab"))
                    logger.debug("tab file upload completed.")
                    has_tab = True
                else:
                    raise RuntimeError("invaild format")
        return has_elm, has_vcf, has_tab

    @staticmethod
    def check_vcf_format(tempfile):
        """
        vcf格式：
            #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT
                17	10584116	.	C	T	50	PASS	.	GT
                16	89350178	.	G	A	50	PASS	.	GT
                17	78302157	.	C	A	50	PASS	.	GT
                17	41133071	.	T	C	50	PASS	.	GT
                1	145586403	.	G	T	50	PASS	.	GT
                10	13653653	.	A	G	50	PASS	.	GT
        :param tempfile: 临时存放文件的路径。
        :return:
        """
        vcf_reader = vcf.Reader(filename=tempfile)
        try:
            next(vcf_reader)
        except IndexError:
            return False
        return True

    @staticmethod
    def check_elm_format(tempfile):
        """
        elm格式：
            Uniprot Accession	Position	Code	PMIDs	Enzymes	Source	Date	Type
            Q8R366	602	C	21609323	null	ZYY	20130911	Palmitoylation
            O14880	150	C	21044946	null	Little	20110224	Palmitoylation
            O14880	151	C	21044946	null	Little	20110224	Palmitoylation
            O60884	409	C	15308774	null	null	null	Farnesylation
            O75581	1394	C	18378904	null	Little	20110219	Palmitoylation
        :param tempfile: 临时文件存放路径
        :return:
        """
        with open(tempfile, 'r') as f:
            line = f.readline()
            info = line.split("\t")
            if len(info) != 8:
                return False
            uniprot_id = re.compile("[A-Z]+[0-9]+")
            position = re.compile("[0-9]+")
            code = re.compile("[A-Z]")
            mode_type = re.compile("[A-Z]+")
            if not ("uniport" in info[0].lower()) or not re.findall(uniprot_id, info[0]):
                return False
            if not ("pos" in info[1].lower()) or not re.findall(position, info[1]):
                return False
            if not ("code" in info[2].lower()) or not re.findall(code, info[2]):
                return False
            if not ("type" in info[-1].lower()) or not re.findall(mode_type, info[-1]):
                return False
        return True

    @staticmethod
    def check_tab_format(tempfile):
        """
        tab格式：
            #CHROM	POS	ID	REF	ALT
            17	10584116	.	C	T
            16	89350178	.	G	A
            17	78302157	.	C	A
            17	41133071	.	T	C
        :param tempfile: 临时文件存放路径
        :return:
        """
        with open(tempfile, 'r') as f:
            line = f.readline()
            info = line.split("\t")
            if len(info) != 5:
                return False
            chrom = re.compile("[0-9]+")
            position = re.compile("[0-9]+")
            ref = re.compile("[A-Z]")
            alt = re.compile("[A-Z]+")
            if not ("chrom" in info[0].lower()) or not re.findall(chrom, info[0]):
                return False
            if not ("pos" in info[1].lower()) or not re.findall(position, info[1]):
                return False
            if not ("ref" in info[2].lower()) or not re.findall(ref, info[-2]):
                return False
            if not ("alt" in info[-1].lower()) or not re.findall(alt, info[-1]):
                return False
        return True
