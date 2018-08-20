# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-7-26
description:
    如果用户上传的是VCF格式的文件，需要使用annovar软件将基因组的突变位置注释到转录组上。
    首先的一步是需要将VCF格式的文件转换为annovar需要的 .avinput文件。
    其中，vcf文件的格式为：
        #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Sample0
        17	10584116	.	C	T	50	PASS	.	GT	1/1
        16	89350178	.	G	A	50	PASS	.	GT	1/1
        17	78302157	.	C	A	50	PASS	.	GT	1/1
        17	41133071	.	T	C	50	PASS	.	GT	1/1
        1	145586403	.	G	T	50	PASS	.	GT	1/1
        10	13653653	.	A	G	50	PASS	.	GT	1/1
    需要转成的avinput格式为：
        #CHROM  start   end REF	ALT
        17	10584116	10584116	C	T
        16	89350178	89350178	G	A
        17	78302157	78302157	C	A
        17	41133071	41133071	T	C
        1	145586403	145586403	G	T
        10	13653653	13653653	A	G
"""
import argparse


class Vcf2Avinput:
    def __init__(self, vcf_file, avin_file):
        """
        对该类进行初始化
        :param vcf_file: 用户提交的vcf文件的所在位置。
        :param avin_file: avinput文件的路径。
        """
        self.vcf_file = vcf_file
        self.output = avin_file

    def vcf2avin(self):
        """
        对用户提交的vcf文件进行读取。
        :return:
        """
        avinput = open(self.output, "w")
        with open(self.vcf_file, "r") as vcf:
            for line in vcf:
                # 以'#'号开头的是注释行需要跳过
                if line.startswith("#"):
                    continue
                data = line.strip().split("\t")[:5]
                # new_line中分别是 染色体位置、突变起始位点、突变终止位点、参考序列的nt、突变的nt
                # 因为本次仅针对突变位点，所以起始位点和终止位点都是突变位点
                new_line = [data[0], data[1], data[1], data[3], data[4]]
                avinput.write("\t".join(new_line) + "\n")
        avinput.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="vcf2avinput", description="vcf2avinput.py 用于将vcf格式转为avinput格式")
    parser.add_argument("-v", "--vcf", action="store", required=True, help="用户提交的vcf文件路径")
    parser.add_argument("-a", "--avinput", action="store", required=True, help="输出的avinput文件路径")
    args = parser.parse_args()
    vcf_file = args.vcf
    avinput_file = args.avinput
    v2a = Vcf2Avinput(vcf_file=vcf_file, avin_file=avinput_file)
    v2a.vcf2avin()
