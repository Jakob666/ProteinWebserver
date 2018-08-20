# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-7-19
description:
    根据计算得到用户输入序列的gamma分布的分布函数，之前的操作将用户的输入序列分为 修饰区和 非修饰区。得到
    这两个区域每个aa的突变次数。通过之前的推导可知
        P(lambda1│lambda2,Y)=Gamma( alpha+sum(Yi),k+beta)     i in [1, k]
        P(lambda2│lambda1,Y)=Gamma( alpha+sum(Yi),n-k+beta)   i in [k+1, n]
    其中 lambda1、lambda2分别是修饰区和非修饰区平均突变数目。 n是序列的长度，k是非修饰区的长度。
    alpha是gamma分布的形状参数，beta是gamma分布的尺度参数。
    生成两个区域的gamma分布函数。

"""
import random


class GammaDistribution:
    def __init__(self, in_motif_mut, out_motif_mut, motif_len, background_len, sample_num, alpha=1.0, beta=0.5):
        """
        初始化gamma分布的参数 alpha和 beta
        :param in_motif_mut: 修饰motif内的突变信息。
        :param out_motif_mut: 修饰motif外的突变信息。
        :param motif_len: 修饰区域的长度。
        :param background_len: 背景区域的长度。
        :param sample_num: 采样的样本数
        :param alpha: 形状参数alpha，默认1.0
        :param beta: 尺度参数 beta，默认0.5
        """
        self.alpha = alpha
        self.beta = beta
        self.motif_len = motif_len
        self.background_len = background_len
        self.in_motif_mut = in_motif_mut
        self.out_motif_mut = out_motif_mut
        # 采样的次数，在样本量的基础上加上200次的burn-in过程
        self.sampling_time = sample_num + 200

    def get_final_param(self):
        """
        根据修饰区和非修饰区的长度及每个位点的突变数，得到最终的gamma分布的参数
        :return:
        """
        alpha1 = self.alpha + self.out_motif_mut
        alpha2 = self.alpha + self.in_motif_mut
        beta1 = self.beta + self.background_len
        beta2 = self.beta + self.motif_len
        return alpha1, alpha2, beta1, beta2

    def gamma_sample(self):
        """
        获得序列修饰区和非修饰区每个位点上的突变病人数目
        :return:
        """
        a1, a2, b1, b2 = self.get_final_param()
        d1 = random.gammavariate(a1, 1/b1)
        d2 = random.gammavariate(a2, 1/b2)
        lambda1_sample = []
        lambda2_sample = []
        for i in range(self.sampling_time):
            if i < 200:
                continue
            lambda1_sample.append(d1)
            lambda2_sample.append(d2)
        return lambda1_sample, lambda2_sample
