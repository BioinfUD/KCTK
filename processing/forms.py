from django import forms
from django.db import models


class UploadFileForm(forms.Form): 
    title = forms.CharField(max_length=50) 
    fileUploaded = forms.FileField() 
    description = models.TextField(max_length=200)