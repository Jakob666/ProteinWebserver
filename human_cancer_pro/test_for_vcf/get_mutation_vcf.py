# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-7-27
description:
    对用户提交的vcf文件使用annovar注释后生成的tsv文件进行处理，得到用户所提交的蛋白是否
    是显著突变蛋白。
"""
import warnings
import pandas as pd
from human_cancer_pro.test_for_elm.get_mutation_info import GetMutationInfo
from human_cancer_pro.test_for_elm.test_significant import SignificanceTest
from human_cancer_pro.models import Motif


class GetMutationVCF(GetMutationInfo):
    @staticmethod
    def load_mut_data(annotate_file):
        """
        读取tsv文件中的数据。读取后生成dataframe并返回，返回的格式
            refseq  Uniprot Accession   protein_name  position    mut_from    mut_to  chr chr_position
        :param annotate_file: annovar_annotate.py中通过annovar注释得到的文件处理后生成的tsv文件的路径。
        :return:
        """
        mut_data = pd.read_csv(annotate_file, sep="\t", encoding="utf-8")
        return mut_data

    @staticmethod
    def load_modify_file(modify_file):
        """
        如果用户提供了指定格式的文件，文件中指定的是蛋白质序列的修饰位点，修饰类型。将数据读取并返回，返回形式：
            Uniprot Accession   Position    Type
        :param modify_file: 用于记录用户提交的修饰位点文件的路径
        :return:
        """
        mod_pos = pd.read_csv(modify_file, sep="\t", encoding="utf-8")
        return mod_pos

    @staticmethod
    def search_motif_range(record, ticked_modify, cancer_type, final_res):
        """
        如果用户没有提供修饰位点的文件，就从数据库中查找相应的结果。
        :param record: 突变数据的每一条记录。
        :param ticked_modify: 用户选取的修饰类型，可以是多个，以列表的形式传入。
        :param cancer_type: 用户选定的癌症类型。
        :param final_res: 用于存放最终结果的list。
        :return:
        """
        protein = record["Uniprot Accession"]
        if cancer_type is not None:
            # 如果用户只点选了一种修饰类型，则传来的是一个仅含有一个元素的list
            if len(ticked_modify) == 1:
                res = Motif.objects.filter(cancer_type=cancer_type, protein_id=protein, modification=ticked_modify[0])
            # 如果用户只点选了多种修饰类型，则传来的是含有多个元素的list
            else:
                res = Motif.objects.filter(cancer_type=cancer_type, protein_id=protein, modification__in=ticked_modify)

        elif cancer_type is None:
            if len(ticked_modify) == 1:
                res = Motif.objects.filter(protein_id=protein, modification=ticked_modify[0])
            else:
                res = Motif.objects.filter(protein_id=protein, modification__in=ticked_modify)

        # 得到该蛋白在所选的修饰类型中对应的所有 修饰位点、修饰类型信息
        # res的形式为 [(protein_id, modify position, modification, protein_length), ……]
        if res.count() != 0:
            for r in res:
                start = max(1, r.modify_position - GetMutationVCF.modification_motif[r.modification]["left"])
                end = min(r.modify_position + GetMutationVCF.modification_motif[r.modification]["right"], r.protein_length)
                r = [r.protein_id, r.modify_position, r.modification, start, end]
                final_res.append(r)
        return None

    @staticmethod
    def get_motif_range(annotate_file, modify_position_file=None, ticked_modify=None, cancer_type=None):
        """
        得到各个修饰位点对应的motif修饰区域，具体的处理有以下两种方式
        （1）用户提交了elm格式的蛋白质修饰文件，该文件中明确指出蛋白及其相应位点的突变。
        （2）用户没有提交elm文件，而是通过浏览器在页面点选修饰类型查找蛋白上相关修饰的motif区域。
        之后将存在重叠的motif进行合并。
            返回的结果形式如下：
                "Uniprot Accession" "Position"  "Type"  "start"   "end"

        :param annotate_file: annovar注释得到的文件处理后生成的tsv文件的路径。
        :param modify_position_file: 用户提交的用于记录蛋白质修饰位点的文件。默认为None，表示可能用户不提供，此时需要用户在浏览器端选择的修饰类型进行查找。
        :param ticked_modify: 用户在没有提交记录修饰位点文件的情况下，在浏览器端点选的修饰类型。可以是多个，以list的形式传入。
        :param cancer_type: 用户选择的癌症类型，只有当物种是人的时候该项才有值。
        :return:
        """
        # 将所有类型修饰位点两端序列长度读取出来
        GetMutationVCF.load_modification()

        # 读取经annovar和后续处理得到的记录突变位点的tsv文件
        mut_data = GetMutationVCF.load_mut_data(annotate_file)

        # 如果用户提交了记录修饰位点的文件
        if modify_position_file is not None:
            modify_position = GetMutationVCF.load_modify_file(modify_position_file)
            modify_position["start"] = 0
            modify_position["end"] = 0
            modify_position = modify_position.apply(GetMutationVCF.calc_motif_range, axis=1)
        # 如果用户没有提交修饰位点文件，而是浏览器端指定了修饰类型
        elif ticked_modify is not None:
            # 初始化一个list用于存放用户提交的这些蛋白在数据库中的motif
            modify_position = []
            mut_proteins = mut_data.drop_duplicates(subset=["Uniprot Accession"], keep="first")
            mut_proteins.apply(GetMutationVCF.search_motif_range, axis=1, args=(ticked_modify, cancer_type, modify_position))
            modify_position = pd.DataFrame(modify_position,
                                           columns=["Uniprot Accession", "Position", "Type", "start", "end"])
        # 如果既没有上交修饰位点文件也没有勾选修饰类型，直接报错
        else:
            raise RuntimeError("both None for modification file and ticked modification")
        return mut_data, modify_position

    @staticmethod
    def get_motif_area(modify_position):
        """
        分别对每种蛋白的不同类型修饰的重叠motif进行合并，同时计算出每种蛋白的修饰区和非修饰区长度
        :param modify_position:
        :return:
        """
        motifs = []
        areas = []
        for (protein_id, mod_type), df in modify_position.groupby(by=["Uniprot Accession", "Type"], as_index=False):
            # 对蛋白序列上重叠的修饰区进行合并
            motif_area = GetMutationVCF.motif_area(df)
            # 计算每个蛋白质的修饰区和非修饰区长度，该数据在之后的显著性检验中会用到
            area_len = GetMutationInfo.calc_motif_len(motif_area)
            area_len.insert(loc=1, column="Type", value=mod_type)
            areas.append(area_len)
            motif_area.insert(loc=1, column="Type", value=mod_type)
            motifs.append(motif_area)
        area_len = pd.concat(areas, axis=0, ignore_index=True)
        motif_area = pd.concat(motifs, axis=0, ignore_index=True)
        return motif_area, area_len

    @staticmethod
    def mut_location(mut_data, modify_position):
        """
        用户上传的突变位点与蛋白质的序列修饰motif区域进行匹配，将突变位点分为修饰区位点和非修饰区位点。
        :param mut_data: 突变位点的dataframe，形式为
                refseq  Uniprot Accession   protein_name    position    mut_from    mut_to  chr   chr_position
        :param modify_position: 蛋白质不同修饰类型的不同motif区域，形式为
                Uniprot Accession  Position    Type    start   end
        :return:返回motif区的突变信息和background区的修饰信息
                Uniprot Accession  mut_position    from    to
        """
        mut_data = mut_data[["Uniprot Accession", "position", "mut_from", "mut_to"]]
        modify_position = modify_position[["Uniprot Accession", "Type", "start", "end"]]
        data = pd.merge(left=mut_data, right=modify_position, how="outer", on="Uniprot Accession")
        func = lambda record: record["start"] <= record["position"] <= record["end"]
        data["in motif"] = data.apply(func, axis=1)
        data = data[["Uniprot Accession", "Type", "position", "mut_from", "mut_to", "in motif"]]
        mutate = []
        for i, df in data.groupby(by=["Uniprot Accession", "Type", "position", "mut_from", "mut_to"], as_index=False):
            df.drop_duplicates(inplace=True)
            mutate.append(df)
        data = pd.concat(mutate, axis=0, ignore_index=True)
        data.drop_duplicates(subset=["Uniprot Accession", "Type", "position", "mut_from", "mut_to"], inplace=True, keep="last")
        motif_mut = data[data["in motif"] == True]
        background_mut = data[data["in motif"] == False]
        motif_mut["count"] = 1
        background_mut["count"] = 1
        return motif_mut, background_mut

    # @staticmethod
    # def main(vcf_file):
    #     """
    #     对用户提交的VCF文件进行处理的完整流程
    #     :return:
    #     """
    #     v2a = Vcf2Avinput(vcf_file=vcf_file, avin_file=avinput_file)
    #     v2a.vcf2avin()


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    # mut_data, modify_position = GetMutationVCF.get_motif_range(
    #     annotate_file="C:/Users/hbs/Desktop/lysine/vcf_annotated.tsv",motif_table=motif_table,
    #     modify_position_file="C:/Users/hbs/Desktop/lysine/vcf_user.elm",
    #     cancer_type="BRCA")
    mut_data, modify_position = GetMutationVCF.get_motif_range(annotate_file="C:/Users/hbs/Desktop/lysine/vcf_annotated.tsv",
                                                               ticked_modify=["Acetylation", "Glycation"],
                                                               cancer_type="BRCA")

    motif_area, area_len = GetMutationVCF.get_motif_area(modify_position)
    motif_mut, background_mut = GetMutationVCF.mut_location(mut_data, motif_area)
    # 找到修饰和背景域的交集，common的形式类似于 {('O14977', 'Acetylation'), ('Q9Y266', 'Glycation'), ……}
    common = set(zip(motif_mut["Uniprot Accession"],motif_mut["Type"])) & set(zip(background_mut["Uniprot Accession"],background_mut["Type"]))
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
        test_result.append(s.test_res)
    res = "\n".join(["\t".join(list(map(str, i.values()))) for i in test_result])
    print(res)
