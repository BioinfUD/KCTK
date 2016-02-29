# -*- coding: utf-8 -*-
from django.db import models
import subprocess
import datetime
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
import csv

# Opciones estáticas
POSIBLES_ESTADOS_PROCESOS = (
    (0, "Terminado exitosamente"),
    (1, "Terminado con errores"),
    (2, "Ejecutandose"),
    (3, "En espera")
)
CONTADORES = (
    (0, "BFCounter"),
    (1, "DSK"),
    (2, "Jellyfish"),
    (3, "KAnalyze"),
    (4, "KHMer"),
    (5, "KMC2"),
    (6, "MSPKmerCounter"),
    (7, "Tallymer"),
    (8, "Turtle"),
)
TIPO = (
    (0, "output"),
    (1, "input"),
)
REVERSE = (
    (0, "duplicate"),
    (1, "single"),
    (1, "canonical"),
)
FORMATO = (
    (0, "raw"),
    (1, "fasta"),
    (2, "fastq"),
    (3, "fastagz"),
    (4, "fastqgz"),
)
# borrar este diccionario de MApeadores:
MAPEADORES = (
    (0, "BFCounter"),
)
TIPOS_MAPEO = (
    (0, "BFCounter"),
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
    tipo = models.IntegerField(choices=TIPO, default=0)
    test = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Archivos'

    def get_contenido(self):
        # falta/pendiente cambiar direccion
        return Django_File(open("%s%s" % (settings.BASE_DIR, self.fileUpload.url))).read()

    def get_kmer_dict(self):
        with open("%s%s" % (settings.BASE_DIR, self.fileUpload.url)) as file_object:
            d = list(csv.reader(file_object, delimiter="\t", dialect=csv.excel))
        return sorted(d)

    def __unicode__(self):
        return u"ARCHIVO \n Location: %s \n Description: %s " % (self.fileUpload.path, self.description)


class Proceso(models.Model):

    estado = models.IntegerField(choices=POSIBLES_ESTADOS_PROCESOS, default=3)
    std_err = models.TextField(default="None")
    std_out = models.TextField(default="None")
    comando = models.CharField(max_length=2000, default="echo Hola mundo")
    profile = models.ForeignKey(Profile)
    contador = models.TextField(default="")
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True)
    resultado = models.ForeignKey(File, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Procesos'

    def get_estado(self):
        return POSIBLES_ESTADOS_PROCESOS[self.estado][1] if self.estado <= 3 else "Terminado con errores"

    def get_resultado(self):
        return self.resultado.get_contenido()

    def get_kmer_dict(self):
        if "Tallymer" == self.contador:
            return sorted(self.resultado.get_kmer_dict(), key=lambda x: x[1])
        else:
            return self.resultado.get_kmer_dict()

    def run_process(self):
        self.estado = 2
        self.save()
        try:
            p = subprocess.Popen(
                str(self.comando), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.std_out, self.std_err = p.communicate()
            self.estado = p.returncode
            print p.returncode
            self.fin = datetime.datetime.now()
        except:
            try:
                self.std_out, self.std_err = p.communicate()
                self.estado = 0
                self.save()
                self.fin = datetime.datetime.now()
            except:
                self.estado = 0
                self.save()
                self.fin = datetime.datetime.now()
        #  self.std_out = self.std_out.replace("\n", "<br>")
        #  self.std_err = self.std_err.replace("\n", "<br>")
        self.save()

    def run(self):
        t = threading.Thread(target=self.run_process)
        t.setDaemon(True)
        t.start()

    def __unicode__(self):
        return u"ID: %s Estado: %s \n Comando: %s \n" % (str(self.id), str(self.estado), str(self.comando))


class BFCounter(models.Model):

    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    contador = models.IntegerField(choices=CONTADORES, default=0)
    profile = models.ForeignKey(Profile)
    k = models.IntegerField()
    numKmers = models.BigIntegerField()
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, file="", k="", numKmers=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "/tmp/BFCounter%s" % randint(1, 1000000)
        comando_part1 = "BFCounter count -t %s -k %s -n %s -o %s %s" % (
            settings.CORES, k, numKmers, tmp_dir, file)
        comando_part2 = "BFCounter dump -k %s -i %s -o %s_dump" % (
            k, tmp_dir, tmp_dir)
        comando = "%s && %s" % (comando_part1, comando_part2)
        # comando = "$TRINITY_HOME/util/align_and_estimate_abundance.pl
        # --thread_count %s  --output_dir %s  --transcripts %s --left %s
        # --right %s --seqType fq --est_method RSEM --aln_method bowtie
        # --prep_reference" % (settings.CORES, tmp_dir, reference, "
        # ".join(reads_1), " ".join(reads_2))
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="BFCounter")
        p1.save()
        self.procesos.add(p1)
        # To get files with path trin.fileUpload.path
        # Genero indice y espero hasta que este listo
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s_dump" % tmp_dir
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", numKmers=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, k=k, numKmers=numKmers))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class DSK(models.Model):

    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    contador = models.IntegerField(choices=CONTADORES, default=0)
    profile = models.ForeignKey(Profile)
    k = models.IntegerField()
    minAb = models.BigIntegerField()
    maxAb = models.BigIntegerField()
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, file="", k="", minAb="", maxAb=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "DSK%s" % randint(1, 1000000)
        comando_part1 = "dsk -nb-cores %s -kmer-size %s -abundance-min %s -abundance-max %s -file %s -out /tmp/%s" % (
            settings.CORES, k, minAb, maxAb, file, tmp_dir)
        comando_part2 = "dsk2ascii -file /tmp/%s.h5 -out /tmp/%s_final" % (
            tmp_dir, tmp_dir)
        comando = "%s && %s" % (comando_part1, comando_part2)
        # comando = "$TRINITY_HOME/util/align_and_estimate_abundance.pl
        # --thread_count %s  --output_dir %s  --transcripts %s --left %s
        # --right %s --seqType fq --est_method RSEM --aln_method bowtie
        # --prep_reference" % (settings.CORES, tmp_dir, reference, "
        # ".join(reads_1), " ".join(reads_2))
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="DSK")
        p1.save()
        self.procesos.add(p1)
        # To get files with path trin.fileUpload.path
        # Genero indice y espero hasta que este listo
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "/tmp/%s_final" % tmp_dir
        with open(file_name, 'r+') as f:
            text = f.read()
            f.seek(0)
            f.truncate()
            f.write(text.replace(' ', '\t'))
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", minAb="", maxAb=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, k=k, minAb=minAb, maxAb=maxAb))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class Jellyfish(models.Model):

    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    contador = models.IntegerField(choices=CONTADORES, default=0)
    profile = models.ForeignKey(Profile)
    m = models.IntegerField()
    minAb = models.BigIntegerField()
    maxAb = models.BigIntegerField()
    canonical = models.BooleanField(default=True)
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, file="", m="", minAb="", maxAb="", canonical=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "/tmp/Jellyfish%s" % randint(1, 1000000)
        # Pendiente: Crear el comando y ejecutar pruebas
        comando_part1 = "jellyfish count -t %s -m %s -s 100000 -L %s -U %s -C -o %s %s" % (
            settings.CORES, m, minAb, maxAb, tmp_dir, file)
        comando_part2 = "jellyfish dump -c -o %s_final %s" % (tmp_dir, tmp_dir)
        comando = "%s && %s" % (comando_part1, comando_part2)
        # comando = "$TRINITY_HOME/util/align_and_estimate_abundance.pl
        # --thread_count %s  --output_dir %s  --transcripts %s --left %s
        # --right %s --seqType fq --est_method RSEM --aln_method bowtie
        # --prep_reference" % (settings.CORES, tmp_dir, reference, "
        # ".join(reads_1), " ".join(reads_2))
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="Jellyfish")
        p1.save()
        self.procesos.add(p1)
        # To get files with path trin.fileUpload.path
        # Genero indice y espero hasta que este listo
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s_final" % tmp_dir
        with open(file_name, 'r+') as f:
            text = f.read()
            f.seek(0)
            f.truncate()
            f.write(text.replace(' ', '\t'))
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", m="", minAb="", maxAb="", canonical=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, m=m, minAb=minAb, maxAb=maxAb, canonical=""))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class KAnalyze(models.Model):

    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    contador = models.IntegerField(choices=CONTADORES, default=0)
    profile = models.ForeignKey(Profile)
    k = models.IntegerField()
    formato = models.IntegerField(choices=FORMATO, default=0)
    reverse = models.IntegerField(choices=REVERSE, default=0)
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, file="", k="", formato="", reverse=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "/tmp/KAnalyze%s" % randint(1, 1000000)
        # Pendiente: Crear el comando y ejecutar pruebas
        comando = "java -jar %s/bin/KAnalyze/kanalyze.jar count -d %s -k %s -o %s -f %s -r%s %s" % (settings.BASE_DIR,settings.CORES, k, tmp_dir, FORMATO[
                                                                int(self.formato)][1], REVERSE[int(self.reverse)][1], file)
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="KAnalyze")
        p1.save()
        self.procesos.add(p1)
        # To get files with path trin.fileUpload.path
        # Genero indice y espero hasta que este listo
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s" % tmp_dir
        with open(file_name, 'r+') as f:
            text = f.read()
            f.seek(0)
            f.truncate()
            f.write(text.replace(' ', '\t'))
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", formato="", reverse=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, k=k, formato=formato, reverse=reverse))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class KMC2(models.Model):

    name = models.TextField(default="Experimento")
    procesos = models.ManyToManyField(Proceso)
    contador = models.IntegerField(choices=CONTADORES, default=0)
    profile = models.ForeignKey(Profile)
    k = models.IntegerField()
    minAb = models.BigIntegerField()
    maxAb = models.BigIntegerField()
    formato = models.TextField(default="q")
    out_file = models.ForeignKey(File, null=True)

    def run_this(self, file="", k="", minAb="", maxAb="", formato=""):
        self.name = "Experimento %s" % self.id
        self.save()
        tmp_dir = "/tmp/KMC2%s" % randint(1, 1000000)
        comando_part1 = "kmc -k%s -ci%s -cx%s -m%s -f%s %s %s /tmp/" % (
            k, minAb, maxAb, settings.RAM, formato, file, tmp_dir)
        comando_part2 = "kmc_tools dump %s %s_final" % (tmp_dir, tmp_dir)
        comando = "%s && %s" % (comando_part1, comando_part2)
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="KMC2")
        p1.save()
        self.procesos.add(p1)
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s_final" % tmp_dir
        with open(file_name, 'r+') as f:
            text = f.read()
            f.seek(0)
            f.truncate()
            f.write(text.replace(' ', '\t'))
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", minAb="", maxAb="", formato=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, k=k, minAb=minAb, maxAb=maxAb, formato=formato))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class Tallymer(models.Model):

    name=models.TextField(default = "Experimento")
    procesos=models.ManyToManyField(Proceso)
    contador=models.IntegerField(choices = CONTADORES, default = 0)
    profile=models.ForeignKey(Profile)
    k=models.IntegerField()
    minAb=models.BigIntegerField()
    out_file=models.ForeignKey(File, null = True)

    def run_this(self, file = "", k = "", minAb = ""):
        self.name="Experimento %s" % self.id
        self.save()
        tmp_dir="Tallymer%s" % randint(1, 1000000)
        comando_part1="gt suffixerator -dna -pl -tis -suf -lcp -v -parts 4 -db %s -indexname /tmp/%s" % (
            file, tmp_dir)
        comando_part2="gt tallymer mkindex -mersize %s -minocc %s -indexname /tmp/tyr-%s -counts -pl -esa /tmp/%s" % (
            k, minAb, tmp_dir, tmp_dir)
        comando_part3="gt tallymer search -tyr /tmp/tyr-%s -output sequence counts -q %s > /tmp/%s_final" % (
            tmp_dir, file, tmp_dir)
        comando="%s && %s && %s" % (
            comando_part1, comando_part2, comando_part3)
        print "comando: %s" % (comando)
        p1=Proceso(comando = str(comando),
                     profile = self.profile, contador = "Tallymer")
        p1.save()
        self.procesos.add(p1)
        t1=threading.Thread(target = p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name="/tmp/%s_final" % tmp_dir
        with open(file_name, 'r+') as f:
            text=f.read()
            f.seek(0)
            f.truncate()
            f.write(text.replace(' ', '\t'))
        out_file=File(fileUpload = Django_File(open(
            file_name)), description = "Salida " + self.name, profile = self.profile, ext = "results")
        out_file.save()
        self.out_file=out_file
        p1.resultado=out_file
        p1.save()

    def run(self, file = "", k = "", minAb = ""):
        t=threading.Thread(target = self.run_this,
                             kwargs = dict(file=file, k=k, minAb=minAb))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural="Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name


class Turtle(models.Model):

    name=models.TextField(default = "Experimento")
    procesos=models.ManyToManyField(Proceso)
    contador=models.IntegerField(choices = CONTADORES, default = 0)
    profile=models.ForeignKey(Profile)
    k=models.IntegerField()
    formato=models.TextField(default = "fastq")
    out_file=models.ForeignKey(File, null = True)

    def run_this(self, file = "", k = "", formato = ""):
        self.name="Experimento %s" % self.id
        self.save()
        tmp_dir="/tmp/Turtle%s" % randint(1, 1000000)
        if formato == "fastq":
            comando="aTurtle64 -k %s -s %s -f %s -q %s" % (
                k, int(settings.RAM) / 1000, file, tmp_dir)
        else:
            comando = "aTurtle64 -k %s -s %s -i %s -q %s" % (
                k, int(settings.RAM) / 1000, file, tmp_dir)
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando),
                     profile=self.profile, contador="Turtle")
        p1.save()
        self.procesos.add(p1)
        t1 = threading.Thread(target=p1.run_process)
        t1.setDaemon(True)
        t1.start()
        while t1.isAlive():
            sleep(1)
        file_name = "%s" % tmp_dir
        out_file = File(fileUpload=Django_File(open(
            file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", formato=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(
            file=file, k=k, formato=formato))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name
