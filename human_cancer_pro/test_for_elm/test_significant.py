# -*- coding:utf-8 -*-
"""
@author:hbs
@date:2017-7-19
description:
    通过用户输入的蛋白质序列修饰区和非修饰区每个aa的突变次数，检验该蛋白是否是显著突变蛋白。
    修饰区域内的突变和修饰区域外的突变是由程序 get_mutation_info.py生成，这两个数据的格式如下，
            cancer, protein Accession  mut_position  from  to  patient_count
        修饰区和非修饰区长度是area_len的dataframe
            Uniprot Accession    motif_len    background_len
"""
from .gamma_distribution import GammaDistribution
import pandas as pd
import numpy as np


class SignificanceTest:
    def __init__(self, motif_mut, background_mut, area_len, sample_num=5000):
        """
        初始化gamma分布的参数 alpha和 beta
        :param motif_mut: 修饰区内的突变信息。
        :param background_mut: 背景区内的突变信息。
        :param area_len: 记录修饰区域、非修饰区的长度的dataframe。
        :param sample_num: 所要采样的样本数目。
        """
        self.motif_mut = motif_mut
        self.background_mut = background_mut
        self.area_len = area_len
        self.sample_num = sample_num
        # 初始化一个dict用于存放用户提交的蛋白的检验结果
        self.test_res = {}

    def get_result(self):
        """
        通过对gamma分布进行gibbs 采样并进行显著性检验，最终返回每个蛋白对应的显著性检验结果。返回形式是列表，内部的元素是布尔值，
        分别对应着用户输入的蛋白的检验结果。
        注意：只保留修饰区和非修饰区同时存在突变的蛋白。
        :return:
        """
        mm = self.motif_mut.groupby(by="Uniprot Accession", as_index=False)["count"].sum()
        bm = self.background_mut.groupby(by="Uniprot Accession", as_index=False)["count"].sum()
        mm = mm[mm["count"] != 0]
        bm = bm[bm["count"] != 0]
        proteins = set(mm["Uniprot Accession"]) & set(bm["Uniprot Accession"])
        for protein in proteins:
            self.significant_test(protein, mm, bm)
            area = self.area_len[self.area_len["Uniprot Accession"] == protein].values
            self.test_res[protein]["motif_length"] = area[0][1]
            self.test_res[protein]["background_length"] = area[0][2]
            motif_mut = self.motif_mut[self.motif_mut["Uniprot Accession"] == protein].values.tolist()
            back_mut = self.background_mut[self.background_mut["Uniprot Accession"] == protein].values.tolist()
            self.test_res[protein]["background_mutation"] = back_mut
            self.test_res[protein]["motif_mutation"] = motif_mut
        # return None

    def get_samples(self, protein, motif_mut, background_mut):
        motif_mut = int(motif_mut[motif_mut["Uniprot Accession"] == protein]["count"])
        background_mut = int(background_mut[background_mut["Uniprot Accession"] == protein]["count"])
        motif_len = int(self.area_len[self.area_len["Uniprot Accession"] == protein]["motif_len"])
        background_len = int(self.area_len[self.area_len["Uniprot Accession"] == protein]["background_len"])
        gd = GammaDistribution(motif_mut, background_mut, motif_len, background_len, self.sample_num)
        # lambda1和lambda2分别是背景区和修饰区的突变平均数
        lambda1_sample, lambda2_sample = gd.gamma_sample()
        return lambda1_sample, lambda2_sample

    def significant_test(self, protein, motif_mut, back_mut):
        """
        传入protein，得到其验是否是赖氨酸相关的显著突变蛋白的判断。假设lambda1、lambda2分别是非修饰区和修饰区平均突变数的采样样本值
        h0: 非修饰区不小于修饰区突变次数    （lambda1/lambda2 >= 1）
        h1: 非修饰区比修饰区突变次数少      （lambda1/lambda2 < 1）
        是单尾检验
        :param protein: protein的 Uniprot ID，对该蛋白进行突变显著性检验
        :param motif_mut: 蛋白质在修饰区的突变计数
        :param back_mut: 蛋白质在非修饰区的突变计数
        :return:
        """
        # lambda1、lambda2分别是非修饰区和修饰区平均突变数的采样样本值
        lambda1, lambda2 = self.get_samples(protein, motif_mut, back_mut)
        # 用非修饰区的平均突变数除以修饰区的平均突变数
        r = np.array(lambda1) / np.array(lambda2)
        ratio = 0
        for i in r:
            # 计算非修饰区突变大于修饰区突变的概率
            if i > 1:
                ratio += 1
        ratio /= self.sample_num
        if ratio > 0.05:
            significance = False
        else:
            significance = True
        self.test_res[protein] = {"significance": significance, "p_value": format(ratio, '0.5E')}
        return None

