# -*- coding:utf-8 -*-
"""
@author: hbs
@date: 2018-7-26
description:
    将用户提交的被转成avinput格式输出的文件传给annovar，通过该软件对突变位点进行注释。
    输出的结果形式为：
        line9 nonsynonymous SNV IL23R:NM_144701:exon9:c.G1142A:p.R381Q, 1 67705958 67705958 G A comments: rs11209026 (R381Q), a SNP in IL23R associated with Crohn's disease
        line11 nonsynonymous SNV NOD2:NM_022162:exon4:c.C2104T:p.R702W,NOD2:NM_001293557:exon3:c.C2023T:p.R675W, 16 50745926 50745926 C comments: rs2066844 (R702W), a non-synonymous SNP in NOD2
        line12 nonsynonymous SNV NOD2:NM_022162:exon8:c.G2722C:p.G908R,NOD2:NM_001293557:exon7:c.G2641C:p.G881R, 16 50756540 50756540 G comments: rs2066845 (G908R), a non-synonymous SNP in NOD2
        line13 frameshift insertion NOD2:NM_022162:exon11:c.3017dupC:p.A1006fs,NOD2:NM_001293557:exon10:c.2936dupC:p.A979fs, 16 50763778 5076377comments: rs2066847 (c.3016_3017insC), a frameshift SNP in NOD2
        line14 frameshift deletion GJB2:NM_004004:exon2:c.35delG:p.G12fs, 13 20763686 20763686 G - comments: rs1801002 (del35G), a frameshift mutation in GJB2, associated with hearing loss
        line15 frameshift deletion GJB6:NM_001110221:wholegene,GJB6:NM_001110220:wholegene,GJB6:NM_001110219:wholegene,CRYL1:NM_015974:wholegene,GJB6:NM_006783:wholegene, 13 20797176 21105944 0 - comments: a 342kb deletion encompassing GJB6, associated with hearing loss
    保留其中的非同义突变，并提取出转录组信息和突变位点信息。并将转录组对应到相应物种的蛋白质Uniprot ID上，将得到的数据写入tsv格式文件，
    文件的各列分别为：
        refseq  position    mut_from    mut_to  chr chr_position  uniprot_id  protein_name
                                        （chr 和 chr_position这两个值与用户提供的vcf文件的内容相同）
"""
import os
import re
import pandas as pd
from human_cancer_pro.CONFIG import annovar_variant
from human_cancer_pro.models import RefSeq
import argparse


class AnnovarAnnotate:

    def __init__(self):
        """
        初始化该对象
        """
        pass

    @staticmethod
    def annotate(user_dir, avinput_file, output_prefix="ex1"):
        """
        通过命令行的形式对avinput中的数据进行注释。注释后会生成两个文件 .variant_function 和 .exonic_variant_function文件。
        :param user_dir: 服务器上的用户目录
        :param avinput_file: 需要被annovar注释的文件， 后缀名为 .avinput
        :param output_prefix: annovar文件注释后得到的注释文件的路径和前缀名，默认为用户目录下 ex1 开头的文件
        :return:
        """
        output_prefix = os.path.join(user_dir, output_prefix)
        res = os.system("%s -geneanno -dbtype refGene -out %s -build hg19 %s humandb/" % (annovar_variant, output_prefix, avinput_file))
        if res != 0:
            raise RuntimeError("fail to annotate with annovar")
        return "success"

    @staticmethod
    def variant_process(user_dir, output_prefix="ex1"):
        """
        用于对生成的 .exonic_variant_function 文件进行处理，提取其中的关键信息。通过annovar注释得到的信息形式如下：
            line9 nonsynonymous SNV IL23R:NM_144701:exon9:c.G1142A:p.R381Q, 1 67705958 67705958 G A comments: rs11209026 (R381Q), a SNP in IL23R associated with Crohn's disease
            line12 nonsynonymous SNV NOD2:NM_022162:exon8:c.G2722C:p.G908R,NOD2:NM_001293557:exon7:c.G2641C:p.G881R, 16 50756540 50756540 G comments: rs2066845 (G908R), a non-synonymous SNP in NOD2
        需要提取其中“nonsynonymous”的记录，并从该记录中提取转录组和突变位点信息。
        提取后生成一个list，其形式和内容为：
            [[转录本, 突变位置, 原aa, 突变aa, 染色体号, 突变位点基因组位置], …………]
        :param user_dir: 服务器上用于存放文件的用户目录
        :param output_prefix: annovar生成的注释文件的前缀名
        :return:
        """
        variant_file = os.path.join(user_dir, output_prefix + ".exonic_variant_function")
        # 主要是对生成文件的第三列的信息进行提取，第三列中有 基因名:转录本:exon:cDNA突变:蛋白质突变
        # 使用正则表达式提取出其中的转录组信息和蛋白质突变位点信息
        # 编译两个pattern，一个用于提取突变信息，另一个用于提取是用户输入的基因组的位点
        mut_pattern = re.compile(".*:([A-Z]{2}_[0-9]*):.*:c.*:p\.([A-Z][0-9]+[A-Z])", re.S)
        annovar_res = []
        with open(variant_file, "r") as f:
            for line in f:
                # 仅提取非同义突变
                if "nonsynonymous" not in line:
                    continue
                info_list = line.strip().split("\t")
                # 得到当前突变对应的染色体号和染色体位置，返回的形式为 [(染色体号, 染色体位置)]
                chromosome = info_list[-5]
                chromosome_pos = info_list[-3]
                mut_info = info_list[2].split(",")
                for i in mut_info:
                    res = re.findall(mut_pattern, i)
                    # 如果当前片段没有匹配到内容即返回空列表，则换到下一个片段
                    if not res:
                        continue
                    # res返回的形式是 [('NM_001256071', 'Q1133K')]，只保留其中的元组
                    res = res[0]
                    mutate_pos = res[1]
                    mut_from = mutate_pos[0]
                    mut_to = mutate_pos[-1]
                    position = int(mutate_pos[1: -1])
                    # 将匹配到的结果统一放入一个list，内容依次为 转录本、突变位置、原aa、突变aa、染色体号、染色体位置
                    annovar_res.append([res[0], position, mut_from, mut_to, chromosome, chromosome_pos])
        return annovar_res

    @staticmethod
    def get_protein_info(record):
        """
        将annovar注释得到的NCBI的refseq对应到Uniprot ID上去，方法是从对应物种的蛋白数据库中搜索。
        :param record:
        :return:
        """
        refseq = record["refseq"]
        res = RefSeq.objects.filter(refseq=refseq).values("uniprot_id", "protein_name")
        # 如果没有对应的转录本
        if res.count() == 0:
            uniprot_id, protein_name = None, None
        else:
            uniprot_id, protein_name = res[0].uniprot_id, res[0].protein_name
        record["Uniprot Accession"] = uniprot_id
        record["protein_name"] = protein_name
        return record

    @staticmethod
    def match2uniport(annovar_res, user_dir):
        """
        对annovar_res中的NCBI refseq号进行Uniprot的匹配。并将最终的结果写入文件中，文件内的各列分别为：
            refseq  position    mut_from    mut_to  uniprot_id  protein_name
        :param annovar_res: variant_process生成的annovar_res列表
        :param user_dir: 服务器上用于存放用户提交文件的目录
        :return:
        """
        mutate_data = pd.DataFrame(annovar_res, columns=["refseq", "position", "mut_from", "mut_to", "chr", "chr_position"])
        mutate_data.insert(loc=1, column="Uniprot Accession", value=None)
        mutate_data.insert(loc=2, column="protein_name", value=None)
        mutate_data = mutate_data.apply(AnnovarAnnotate.get_protein_info, axis=1)
        # 如果annovar注释的用户输入的数据若存在没有匹配上的refseq数据则去除该部分
        mutate_data.dropna(inplace=True)
        # 比对结果为空则会报错
        if mutate_data.empty:
            raise RuntimeError("empty dataframe")
        output_file = os.path.join(user_dir, "vcf_annotated.tsv")
        mutate_data.to_csv(output_file, sep="\t", index=False, mode="w", encoding="utf-8")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="annovar_annotate", description="对用户的avinput文件进行annovar注释得到相应蛋白质。")
    parser.add_argument("-d", "--user_dir", action="store", required=True, help="服务器上用户提交文件的存放目录。")
    parser.add_argument("-i", "--input", action="store", required=True, help="用户目录下的avinput文件路径。")
    parser.add_argument("-p", "--prefix", action="store", default="avoutput", required=False,
                        help="指定annovar注释生成的中间文件的前缀名（非必需）")
    args = parser.parse_args()
    user_dir = args.user_dir
    avinput = args.input
    prefix = args.prefix
    # 对avinput文件进行注释
    AnnovarAnnotate.annotate(user_dir, avinput, prefix)
    annovar_res = AnnovarAnnotate.variant_process(user_dir, prefix)
    AnnovarAnnotate.match2uniport(annovar_res, user_dir)

    # 以下代码仅用于测试
    # res = AnnovarAnnotate.variant_process("C:/Users/hbs/Desktop/lysine/")
    # AnnovarAnnotate.match2uniport(target_table, res, "C:/Users/hbs/Desktop/lysine/")
