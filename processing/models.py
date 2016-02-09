# -*- coding: utf-8 -*-
from django.db import models
import subprocess
import threading
from django.conf import settings
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import User
from time import sleep
from django.core.files import File as Django_File
from django.conf import settings
from random import randint
import os

# Opciones estáticas
POSIBLES_ESTADOS_PROCESOS = (
    (0, "Terminado exitosamente"),
    (1, "Terminado con errores"),
    (2, "Iniciado"),
    (3, "En espera")
)
MAPEADORES = (
    (0, "BWA"),
    (1, "Bowtie"),
)
TIPOS_MAPEO = (
    (0, "Single end"),
    (1, "Paired end")
)


class Profile(models.Model):
    user = models.OneToOneField(User)
    email = models.EmailField()
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'Perfiles'

    def __unicode__(self):
        return unicode(self.email)


class File(models.Model):
    fileUpload = models.FileField()
    description = models.TextField(default="")
    profile = models.ForeignKey(Profile)
    ext = models.CharField(max_length=7)

    class Meta:
        verbose_name_plural = 'Archivos'

    def __unicode__(self):
        return u"ARCHIVO \n Location: %s \n Description: %s " % (self.fileUpload.path, self.description)


class Proceso(models.Model):

    estado = models.IntegerField(choices=POSIBLES_ESTADOS_PROCESOS, default=3)
    std_err = models.TextField(default="")
    std_out = models.TextField(default="")
    comando = models.CharField(max_length=2000, default="echo Hola mundo")
    profile = models.ForeignKey(Profile)

    class Meta:
        verbose_name_plural = 'Procesos'

    def get_estado(self):
        return POSIBLES_ESTADOS_PROCESOS[self.estado][1]

    def run_process(self):
        self.estado = 2
        self.save()
        try:
            p = subprocess.Popen(str(self.comando), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.std_out, self.std_err = p.communicate()
            self.estado = p.returncode
        except:
            try:
                self.std_out, self.std_err = p.communicate()
                self.estado = 0
                self.save()
            except:
                self.estado = 0
                self.save()
        #  self.std_out = self.std_out.replace("\n", "<br>")
        #  self.std_err = self.std_err.replace("\n", "<br>")
        self.save()

    def run(self):
        t = threading.Thread(target=self.run_process)
        t.setDaemon(True)
        t.start()

    def __unicode__(self):
        return u"ID: %s Estado: %s \n Comando: %s \n STDOUT: \n %s \n STDERR: %s\n " % (str(self.id), str(self.estado), str(self.comando), str(self.std_out), str(self.std_err))


class Align_and_estimate_abundance(models.Model):

    """"
    Run example
    type=1 -> Single end
    type=2 -> Paired end
    m = Mapeo(name="Exp", mapeador=0, tipo=1, profile=p)
    m.save()
    """
    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    mapeador = models.IntegerField(choices=MAPEADORES, default=1)
    tipo = models.IntegerField(default=1, choices=TIPOS_MAPEO)
    profile = models.ForeignKey(Profile)
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, reference="", reads_1="", reads_2="", reads_se=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "/tmp/aln%s" % randint(1, 1000000)
        comando = "$TRINITY_HOME/util/align_and_estimate_abundance.pl --thread_count %s  --output_dir %s  --transcripts %s --left %s --right %s --seqType fq --est_method RSEM --aln_method bowtie --prep_reference" % (settings.CORES, tmp_dir, reference, " ".join(reads_1), " ".join(reads_2))
        print reads_1
        print reads_2
        p1 = Proceso(comando=str(comando), profile=self.profile)
        p1.save()
        self.procesos.add(p1)
        # To get files with path trin.fileUpload.path
        # Genero indice y espero hasta que este listo
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s/RSEM.isoforms.results" % tmp_dir
        out_file = File(fileUpload=Django_File(open(file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file

    def run(self, reference, reads_1="", reads_2=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(reference=reference, reads_1=reads_1, reads_2=reads_2))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class Abundance_to_Matrix(models.Model):
    name = models.TextField(default="Abundance_to_Matrix Results")
    procesos = models.ManyToManyField(Proceso)
    out_results = models.ForeignKey(File, null=True, related_name="file_results_Abundance_to_Matrix")
    profile = models.ForeignKey(Profile)

    def run_this(self, files=""):
        self.name = "Abundance_to_Matrix Results. Exp: %s " % self.id
        self.save()
        out_dir = "/tmp/matrix%s" % str(randint(1, 65000))
        try:
            os.mkdir(out_dir)
        except:
            pass
        prefix = "VS".join([f.split("/")[-1].replace(".results", "") for f in files])
        comando = "$TRINITY_HOME/util/abundance_estimates_to_matrix.pl --est_method RSEM  --out_prefix  %s/%s %s" % (str(out_dir), str(prefix), " ".join(files))
	print comando
        p = Proceso(comando=str(comando), profile=self.profile)
        p.save()
        self.procesos.add(p)
        t1 = threading.Thread(target=p.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        f1 = File(fileUpload=Django_File(open(out_dir + "/%s.counts.matrix" % prefix)), description="Salida " + self.name, profile=self.profile, ext="matrix")
        f1.save()
        self.out_results = f1

    class Meta:
        verbose_name_plural = "Procesos de abundancia a matriz"

    def run(self, files=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(files=files))  # Replace for bwa when ready
        t.setDaemon(True)
        t.run()

    def __unicode__(self):
        print name


class Differential_Expression(models.Model):
    name = models.TextField(default="Differential_Expression Results")
    procesos = models.ManyToManyField(Proceso)
    out_results = models.ForeignKey(File, null=True, related_name="file_results_Differential_Expression")
    out_params = models.ForeignKey(File, null=True, related_name="file_rparams_Differential_Expression")
    profile = models.ForeignKey(Profile)

    def run_this(self, matrix=""):
        self.name = "Differential_Expression Results. Exp: %s " % self.id
        self.save()
        out_dir = "/tmp/DE%s" % str(randint(1, 65000))
        comando = "$TRINITY_HOME/Analysis/DifferentialExpression/run_DE_analysis.pl -o  %s --matrix %s --method edgeR" % (str(out_dir), matrix)
        p = Proceso(comando=str(comando), profile=self.profile)
        p.save()
        self.procesos.add(p)
        t1 = threading.Thread(target=p.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        result = subprocess.check_output("ls -1 %s/*pdf" % out_dir, shell=True)
        f1 = File(fileUpload=Django_File(open(result.strip())), description="PDF output " + self.name, profile=self.profile, ext="pdf")
        f1.save()
        self.out_results = f1
        result = subprocess.check_output("ls -1 %s/*results" % out_dir, shell=True)
        f1 = File(fileUpload=Django_File(open(result.strip())), description="Data output " + self.name, profile=self.profile, ext="csv")
        f1.save()
        self.out_params = f1
        self.save()


    class Meta:
        verbose_name_plural = "Procesos de expresion diferencial"

    def run(self, matrix=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(matrix=matrix))  # Replace for bwa when ready
        t.setDaemon(True)
        t.run()

    def __unicode__(self):
        print name
