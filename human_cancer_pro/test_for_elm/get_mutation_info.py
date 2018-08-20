# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-7-20
description:
    用于解析用户传递上来的elm格式的文件，elm格式大致如下，

    PLMD ID	Uniprot Accession	Position	Type	Sequence	Species	PMIDs
    PLMD-1	O00115	52	Ubiquitination	MIPLLL……	Homo sapiens	21963094;23266961

其中PLMD ID这一列不是必须的，需要提取的关键列是 Uniprot Accession、position（修饰位点）和Type（修饰类型）其他的不用提取。
注意用户输入的Uniprot Accession有可能是 Isoform而非 Canonical，这时需要将其转换为Canonical，因为目前没有对isoform进行建库。
    用户上传的elm数据将会被暂存至一个临时文件中，使用pandas进行提取。最终返回的结果为两部分数据，
    （1）在修饰区域中的突变
    （2）不在修饰区域中的突变
    两个数据格式是相同的，都是以dataframe的方式返回，形式为
        cancer_type, protein_id, mutate_position, from, to, patient_count
    得到这两部分数据的目的是将其传入后续的程序中生成修饰区和非修饰区的gamma分布，同时也可传入到可视化的程序中完成可视化工作。
"""
import pandas as pd
from .if_overlapped import if_overlapped
import warnings
import json
from django.db import models
from functools import reduce
from human_cancer_pro.CONFIG import *
from human_cancer_pro.models import Motif, Mutation, ProteinInfo


class GetMutationInfo:
    # 初始化一个modification_motif变量，该变量用于记录各种修饰的motif长度
    modification_motif = None

    @staticmethod
    def load_modification():
        """
        用于加载modification.json文件，生成字典格式便于之后计算motif区域
        :return:
        """
        # 此处的modification_file是config文件中加载得到
        with open(modification_file, "r") as f:
            modification_motif = json.load(f)
            GetMutationInfo.modification_motif = dict(modification_motif)
        return None

    @staticmethod
    def load_elm_data(user_file):
        """
        用于读取序列文件。提取的列分别为Uniprot ID、修饰位点和修饰类型
        :param 用户提交的elm格式的文件
        :return:
        """
        data = pd.read_csv(user_file, sep="\t", usecols=["Uniprot Accession", "Position", "Type"])
        data.columns = ["Uniprot Accession", "Position", "Type"]
        return data

    @staticmethod
    def get_protein_len(uniprot_id):
        """
        通过获取到的Uniprot的ID从数据库中获取蛋白质的长度信息，目前先使用sqlite3，以后会尽量改为ORM。
        需要查找的信息主要是蛋白质序列的长度防止在计算motif的时候避免出现超出序列长度的情况。
        :param uniprot_id: 传入Uniprot ID作为查询的目标
        :return:
        """
        try:
            q = ProteinInfo.objects.get(protein_id=uniprot_id)
            prot_length = q.protein_length
        except models.ObjectDoesNotExist:
            prot_length = 0
        return prot_length

    @staticmethod
    def calc_motif_range(record):
        """
        用于根据不同的修饰类型计算motif区域的范围。
        :param record: data中的每一行数据，通过Dataframe的apply方法传入。
        :return:
        """
        uni_id = record["Uniprot Accession"]
        mod_type = record["Type"]
        if mod_type not in GetMutationInfo.modification_motif.keys():
            mod_type = "other"
        mod_position = record["Position"]
        prot_len = GetMutationInfo.get_protein_len(uni_id)

        start = mod_position - GetMutationInfo.modification_motif[mod_type]["left"]
        end = mod_position + GetMutationInfo.modification_motif[mod_type]["right"]
        # 修饰区域起点不能是负数，修饰区域终点也不能超过蛋白质本身的长度
        if start <= 0:
            start = 1
        if end > prot_len:
            end = prot_len
        # 蛋白质长度为0表示库中没有该蛋白，start设置为1是为了在calc_motif_len方法中使得motif区域长度为0
        if prot_len == 0:
            start = 1
        record["start"] = start
        record["end"] = end
        return record

    @staticmethod
    def motif_area(data):
        """
        对 calc_motif_range方法计算得到的motif范围进行检验，筛查是否存在重叠区域，如果有重叠则需要合并。

            返回的dataframe的索引列为Uniprot号  数据列为start  end分别是motif的起始和终止
        :return:
        """
        motif_area = data[["Uniprot Accession", "start", "end"]]
        motif_area.set_index("Uniprot Accession", inplace=True)
        # 获取所有不同的蛋白质
        proteins = motif_area.index.unique()
        motif_res = []
        for p in proteins:
            data = motif_area.ix[p]
            if type(data) == pd.core.series.Series:
                motif_res += [[p, data["start"], data["end"]]]
                continue
            # 起始位点从小到大排序
            data.sort_values("start", inplace=True)
            # 得到某个蛋白质序列上所有的motif area
            areas = list(zip(list(data.index), list(data["start"]), list(data["end"])))
            # 只有在该蛋白上有多个motif区域时才进行检查
            if len(areas) > 1:
                for i in range(len(areas)-1):
                    interval1 = [areas[i][1], areas[i][2]]
                    interval2 = [areas[i+1][1], areas[i+1][2]]
                    # 鉴定两个区域是否有重叠
                    overlap = if_overlapped(interval1, interval2)
                    # 如果存在重叠，则将重叠区域进行合并
                    if overlap:
                        areas[i] = [p, None, None]
                        areas[i+1] = [p, min(interval1[0], interval2[0]), max(interval1[1], interval2[1])]
                    else:
                        areas[i] = list(areas[i])
                        areas[i+1] = list(areas[i+1])
            else:
                areas[0] = list(areas[0])
            motif_res += areas
        motif_area = pd.DataFrame(motif_res, columns=["Uniprot Accession", "start", "end"])
        motif_area.set_index("Uniprot Accession", drop=False, inplace=True)
        motif_area.dropna(inplace=True)
        return motif_area

    @staticmethod
    def calc_motif_len(motif_area):
        """
        用于计算每个蛋白修饰区长度、非修饰区长度
        :param motif_area: 由motif_area方法得到的dataframe
        :return:  Uniprot Accession    motif_len    background_len
        """
        motif_area["motif_len"] = motif_area["end"] - motif_area["start"] + 1
        proteins = set(motif_area["Uniprot Accession"])
        length = {}
        for p in proteins:
            protein_len = GetMutationInfo.get_protein_len(p)
            length[p] = protein_len
        area_len = motif_area.groupby(by="Uniprot Accession", axis=0, as_index=False)["motif_len"].sum()
        # 定义函数func用于计算背景区域长度
        background = lambda record: length[record["Uniprot Accession"]]-record["motif_len"]
        area_len["background_len"] = area_len.apply(background, axis=1)
        return area_len

    @staticmethod
    def get_mutation_info(protein, motif_area, cancer_type, motif_mut, background_mut):
        """
        根据 motif_area计算得到的结果获取在蛋白质修饰区和非修饰区所有的突变位点。修饰位点的筛选条件 明确 cancer_type、protein_id这两个
        关键字段。
        motif_area产生的dataframe的其中一条记录，对dataframe使用 apply方法将每一条记录传入。
        :param protein: 传入蛋白质的Uniprot Accession
        :param motif_area: 传入记录修饰区域范围的dataframe
        :param cancer_type: 明确查找的癌症类型。
        :param motif_mut: 存放修饰区突变的list
        :param background_mut: 存放背景区修饰的list
        :return:
        """
        records = motif_area[motif_area["Uniprot Accession"] == protein]
        motif_range = list(zip(records["start"], records["end"]))
        # 用于存放UNION的连接对象
        mut_in_list = []
        mut_in = None
        mut_all = None
        if cancer_type is not None:
            # 如果整条序列中存在突变则查询在motif中的突变
            for i in motif_range:
                motif_start = i[0]
                motif_end = i[1]
                mut_in = Mutation.objects.filter(cancer_type=cancer_type, protein_id=protein,
                                                 mutate_position__gte=motif_start, mutate_position__lte=motif_end)
                if mut_in.count() != 0:
                    mut_in_list.append(mut_in)

            # 查询某个蛋白序列上所有的突变
            mut_all = Mutation.objects.filter(cancer_type=cancer_type, protein_id=protein)

        elif cancer_type is None:
            # 如果整条序列中存在突变则查询在motif中的突变
            for i in motif_range:
                motif_start = i[0]
                motif_end = i[1]
                mut_in = Mutation.objects.filter(protein_id=protein, mutate_position__gte=motif_start,
                                                 mutate_position__lte=motif_end)
                if mut_in.count() != 0:
                    mut_in_list.append(mut_in)

            # 查询某个蛋白序列上所有的突变
            mut_all = Mutation.objects.filter(protein_id=protein)
        # 将在motif中的突变结果合并并去重
        if len(mut_in_list) != 0:
            mut_in = reduce(models.QuerySet.union, mut_in_list)

        # # 如果数据库中该蛋白在某类癌症的所有记录中整条序列上没有突变，则其在修饰区和非修饰区都没有突变
        if mut_all.count() == 0:
            # Uniprot Accession, mut_position, from, to, patient, count
            motif_mut.append([protein, None, None, None, None, 0])
            background_mut.append([protein, None, None, None, None, 0])
            return None

        # 如果查询结果显示在该修饰区域中没有突变，则将该蛋白在motif区域的记录设为0
        if len(mut_in_list) == 0:
            motif_mut.append([protein, None, None, None, None, 0])
        # 如果存在该motif区域中的修饰，则将该蛋白在motif区的记录加入列表
        else:
            for mut in mut_in:
                res = [mut.protein_id, mut.mutate_position, mut.mut_from, mut.mut_to, mut.patient, 1]
                motif_mut.append(res)

        # 从所有突变记录中排除在修饰区中的记录，得到修饰区域外的突变记录
        res_out = [i for i in list(mut_all) if i not in list(mut_in)]
        if len(res_out) == 0:
            background_mut.append([protein, None, None, None, None, 0])
        for res in res_out:
            res = [res.protein_id, res.mutate_position, res.mut_from, res.mut_to, res.patient, 1]
            background_mut.append(res)
        return None

    @staticmethod
    def main(user_file, cancer_type=None):
        """
        用户传入elm文件后将整个分析流程串联起来
        :param user_file: 用户上传的elm文件路径
        :param cancer_type: 用户指定查询的癌症类型
        :return:
        """
        # 初始化两个空list用于存放修饰区和非修饰区的数据
        motif_mut = []
        background_mut = []
        # 将所有的突变信息从json文件中读取出来
        GetMutationInfo.load_modification()

        # 首先从用户上传的elm中读取和提取信息
        data = GetMutationInfo.load_elm_data(user_file)
        # 求出用户指定的各个修饰位点所在motif的区域
        data["start"] = 0
        data["end"] = 0
        # 通过不同的修饰的json文件初步获取elm文件中每个修饰位点的范围
        data = data.apply(GetMutationInfo.calc_motif_range, axis=1)

        # 对同一个蛋白上的修饰位点确定的motif进行处理，将有重叠的motif进行合并
        motif_area = GetMutationInfo.motif_area(data)

        # 计算每个蛋白质的修饰区和非修饰区长度，该数据在之后的显著性检验中会用到
        area_len = GetMutationInfo.calc_motif_len(motif_area)

        # 得到蛋白质修饰区和非修饰区的突变信息
        proteins = list(area_len["Uniprot Accession"])
        for p in proteins:
            GetMutationInfo.get_mutation_info(p, motif_area, cancer_type, motif_mut, background_mut)

        if cancer_type is not None:
            motif_mut = pd.DataFrame(motif_mut, columns=["Uniprot Accession", "mut_position", "from", "to",
                                                         "patient", "count"])
            background_mut = pd.DataFrame(background_mut, columns=["Uniprot Accession", "mut_position", "from",
                                                                   "to", "patient", "count"])
            motif_mut.insert(loc=0, column="cancer", value=cancer_type)
            background_mut.insert(loc=0, column="cancer", value=cancer_type)
        elif cancer_type is None:
            motif_mut = pd.DataFrame(motif_mut, columns=["Uniprot Accession", "mut_position", "from", "to",
                                                         "patient", "count"])
            background_mut = pd.DataFrame(background_mut, columns=["Uniprot Accession", "mut_position", "from",
                                                                   "to", "patient", "count"])
        motif_mut.drop_duplicates(inplace=True)
        motif_mut.dropna(inplace=True)
        background_mut.drop_duplicates(inplace=True)
        return area_len, motif_mut, background_mut


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    m = GetMutationInfo()
    m.main("C:/Users/hbs/Desktop/lysine/test_user.elm", "BRCA")

