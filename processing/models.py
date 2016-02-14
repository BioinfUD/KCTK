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

# Opciones estáticas
POSIBLES_ESTADOS_PROCESOS = (
    (0, "Terminado exitosamente"),
    (1, "Terminado con errores"),
    (2, "Iniciado"),
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
#borrar este diccionario de MApeadores:
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

    class Meta:
        verbose_name_plural = 'Archivos'

    def get_contenido(self):
        # falta/pendiente cambiar direccion
        return Django_File(open("/home/nazkter/Develop/KmerCountersToolKit%s"%(self.fileUpload.url))).read()
        
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
        return POSIBLES_ESTADOS_PROCESOS[self.estado][1]

    def get_resultado(self):
        return self.resultado.get_contenido()

    def run_process(self):
        self.estado = 2
        self.save()
        try:
            p = subprocess.Popen(str(self.comando), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
        return u"ID: %s Estado: %s \n Comando: %s \n STDOUT: \n %s \n STDERR: %s\n " % (str(self.id), str(self.estado), str(self.comando), str(self.std_out), str(self.std_err))


class BFCounter(models.Model):

    """"
    Run example
    type=1 -> Single end
    type=2 -> Paired end
    m = Mapeo(name="Exp", mapeador=0, tipo=1, profile=p)
    m.save()
    """
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
        comando_part1 = " BFCounter count -t %s -k %s -n %s -o %s %s" % (settings.CORES, k, numKmers, tmp_dir,file)
        comando_part2 = "BFCounter dump -k %s -i %s -o %s_dump" % (k, tmp_dir, tmp_dir)
        comando = "%s && %s" % (comando_part1, comando_part2) 
        #comando = "$TRINITY_HOME/util/align_and_estimate_abundance.pl --thread_count %s  --output_dir %s  --transcripts %s --left %s --right %s --seqType fq --est_method RSEM --aln_method bowtie --prep_reference" % (settings.CORES, tmp_dir, reference, " ".join(reads_1), " ".join(reads_2))
        print "comando: %s" % (comando)
        p1 = Proceso(comando=str(comando), profile=self.profile, contador="BFCounter")
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
        out_file = File(fileUpload=Django_File(open(file_name)), description="Salida " + self.name, profile=self.profile, ext="results")
        out_file.save()
        self.out_file = out_file
        p1.resultado = out_file
        p1.save()

    def run(self, file="", k="", numKmers=""):
        t = threading.Thread(target=self.run_this, kwargs=dict(file=file, k=k, numKmers=numKmers))
        t.setDaemon(True)
        t.start()

    class Meta:
        verbose_name_plural = "Procesos de alinear y estimar abundancia"

    def __unicode__(self):
        return u"Alineamiento y estimación \n %s" % self.name
