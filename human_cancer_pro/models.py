from django.db import models


class ProteinInfo(models.Model):
    """
    对蛋白质进行建模
    """
    protein_id = models.CharField(max_length=20)
    protein_length = models.IntegerField()

    class Meta:
        db_table = "protein_sequence"

    def __str__(self):
        return "%s: %s" % (self.protein_id, self.protein_length)


class Mutation(models.Model):
    """
    对突变对象进行建模。
    """
    cancer_type = models.CharField(max_length=10)
    protein_id = models.CharField(max_length=20)
    mutate_position = models.IntegerField()
    mut_from = models.CharField(max_length=1)
    mut_to = models.CharField(max_length=1)
    patient = models.CharField(max_length=30)

    class Meta:
        db_table = "mutation_table"

    def __str__(self):
        return "%s: %s -> %s" % (self.protein_id, self.mutate_position, self.patient)


class Motif(models.Model):
    """
    对motif进行建模。
    """
    cancer_type = models.CharField(max_length=10)
    protein_id = models.CharField(max_length=30)
    protein_length = models.IntegerField()
    modification = models.CharField(max_length=30)
    modify_position = models.IntegerField()
    motif_seq = models.CharField(max_length=20)
    start = models.IntegerField()
    end = models.IntegerField()

    class Meta:
        db_table = "motif_table"

    def __str__(self):
        return "%s: %s -> %s" % (self.modification, self.start, self.end)


class RefSeq(models.Model):
    """
    对RefSeq进行建模，目的是在annovar对用户提交VCF文件处理后将RefSeq号对应到Uniprot上面去。
    """
    refseq = models.CharField(max_length=30)
    uniprot_id = models.CharField(max_length=30)
    protein_name = models.TextField()

    class Meta:
        db_table = "human_ref2uni"

    def __str__(self):
        return "%s -> %s" % (self.refseq, self.uniprot_id)

