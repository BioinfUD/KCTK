# -*- coding: utf-8 -*-
from forms import *
from processing.models import *
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.template import loader, Context, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.servers.basehttp import FileWrapper
import os


#   ############ AUTENTICATION ###############
def auth_view(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'home.html')
    else:
        error = 'No se ha podido acceder, intente nuevamente'
        return render(request, 'error.html', {'error':error})
 

def error_login(request):
    error = 'El ususario o la contraseña son incorrectos'
    return render(request, 'error.html', {'error':error})


def log_in(request):
    return render(request, 'login.html')


def log_out(request):
    logout(request)
    success = 'Ha cerrado sesión satisfactoriamente. Si desdea acceder de nuevo haga clic en el siguiente botón:'
    url_continuar = '/login'
    msg_continuar = 'Acceder a la cuenta'
    return render(request, 'success.html',{'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})


#  ############ REGISTRATION ###############
def register_user(request):
    if request.POST:
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 == password2:
            new_user = User(username=email, email=email)
            new_user.set_password(password1)
            new_user.save()
            new_profile = Profile(user=new_user,
                                  email=email,
                                  firstName=request.POST.get('firstName', ''),
                                  lastName=request.POST.get('lastName', ''),
                                  )
            new_profile.save()
            success = 'Se ha registrado satisfactoriamente.'
            url_continuar = '/login'
            msg_continuar = 'Acceder a la cuenta'
            return render(request, 'success.html',{'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})
        else:
            error = 'Las contrasenas no son iguales'
            return render(request, 'error.html', {'error': error})
    else:
        return render(request, 'register.html')


#  ############ FILES ###############

@login_required(login_url='/login/')
def filesubmit(request):
    if request.method == 'POST':
        #  try:
        desc = request.POST.get('description', '')
        user = User.objects.select_related().get(id=request.user.pk)
        p = user.profile
        ext = str(request.FILES['file']).split(".")[-1]
        instance = File(fileUpload=request.FILES['file'], description=desc, profile=p,ext=ext,tipo=1)
        instance.save()
        success = 'El archivo se ha guardado satisfactoriamente.'
        url_continuar = '/files'
        msg_continuar = 'Ver lista de archivos'
        return render(request, 'success.html',{'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})
        #  except Exception as e:
        #    print e
    else:
        return render(request, 'upload.html')


@login_required(login_url='/login/')
def delete_file(request, fileID):
    try:
        file2del = File.objects.get(id=int(fileID))
        profile = ser = User.objects.select_related().get(id=request.user.pk).profile
        if file2del.profile == profile:
            file2del.delete()
            success = 'Se ha eliminado el archivo satisfactoriamente.'
            url_continuar = '/files'
            msg_continuar = 'Ver lista de archivos'
            return render(request, 'success.html',{'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})
        else:
            error = 'Este archivo no le pertenece'
            return render(request, 'error.html', {'error':error})
    except Exception, e:
        return render(request, 'error.html', {'error': e})


@login_required(login_url='/login/')
def show_fileupload(request):
    form = UploadFileForm()
    return render(request, 'fileupload.html', {'form': form})


@login_required(login_url='/login/')
def show_edit_file(request, fileID):
    return render(request, 'show_edit_file.html', {'fileID': fileID})


@login_required(login_url='/login/')
def editfile(request):
    desc = request.POST.get('description', '')
    fileID = request.POST.get('fileid', '')

    try:
        profile = User.objects.select_related().get(id=request.user.pk).profile
        instance = File.objects.get(id=int(fileID))
        instance.description = desc
        instance.save()
        success = 'Se ha editado el archivo satisfactoriamente.'
        url_continuar = '/files'
        msg_continuar = 'Ver lista de archivos'
        return render(request, 'success.html',{'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})
    except Exception, e:
        error = 'No se pudieron guardar los datos'
        return render(request, 'error.html', {'error':error})


#  ############ PAGE RENDER ###############
def home(request):
    return render(request, 'home.html')


@login_required(login_url='/login/')
def bfcounter_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'bfcounter.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def dsk_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'dsk.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def jellyfish_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'jellyfish.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def kanalyze_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'kanalyze.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def khmer_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'khmer.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def kmc2_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'kmc2.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def mspkmercounter_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'mspkmercounter.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def tallymer_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'tallymer.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def turtle_form(request):
    profile = User.objects.select_related().get(id=request.user.pk).profile
    kmerKfiles = File.objects.all().filter(profile = profile).filter(tipo=1)
    return render(request, 'turtle.html', {'fileList': kmerKfiles})

@login_required(login_url='/login/')
def upload_success(request):
    success = 'Se ha subido el archivo satisfactoriamente.'
    return render(request, 'success.html',{'success': success})


@login_required(login_url='/login/')
def show_files(request):
    user = User.objects.select_related().get(id=request.user.pk)
    profile = user.profile
    file_list = File.objects.all().filter(profile = profile).filter(tipo = 1)
    return render(request, 'files.html', {'file_list': file_list})


@login_required(login_url='/login/')
def show_process(request):
    user = User.objects.select_related().get(id=request.user.pk)
    profile = user.profile
    processes = Proceso.objects.all().filter(profile=profile)
    return render(request, 'processes.html', {'process_list': processes})


@login_required(login_url='/login/')
def show_processes(request):
    return render(request, 'show_processes.html')


#  Show standard err and output of process
@login_required(login_url='/login/')
def show_specific_process(request, process_id):
    p = Proceso.objects.get(id=process_id)
    return render(request, 'show_process_info.html', {'p': p})


@login_required(login_url='/login/')
def download_file(request, id_file):
    file_path = File.objects.get(id=id_file).fileUpload.path
    wrapper = FileWrapper(file(file_path))
    filename = file_path.split("/")[-1]
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['Content-Length'] = os.path.getsize( file_path )
    print os.path.getsize( file_path )
    print file_path
    return response



@login_required(login_url='/login/')
def run_bfcounter(request):
    #REFERENCE FILE PATH
    file_id = request.POST.get('file', '')
    file_path = File.objects.get(id=int(file_id)).fileUpload.path
    #CONFIG
    k = request.POST.get('k', '')
    numKmers = request.POST.get('numKmers', '')
    profile = User.objects.select_related().get(id=request.user.pk).profile
    bf = BFCounter(contador=0, k=k, numKmers=numKmers, profile=profile)
    bf.save()

    bf.run(file=file_path, k=k, numKmers=numKmers)
    #Falta el response
    success = 'El proceso se ha puesto en la cola de espera. Para ver este proceso en la lista de procesos haga clic en el siguiente botón:'
    url_continuar = '/process/show'
    msg_continuar = 'Ver lista de procesos'
    return render(request, 'success.html', {'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})

@login_required(login_url='/login/')
def run_dsk(request):
    #REFERENCE FILE PATH
    file_id = request.POST.get('file', '')
    file_path = File.objects.get(id=int(file_id)).fileUpload.path
    #CONFIG
    k = request.POST.get('k', '')
    minAb = request.POST.get('minAb', '')
    maxAb = request.POST.get('maxAb', '')
    profile = User.objects.select_related().get(id=request.user.pk).profile
    dsk = DSK(contador=1, k=k, minAb=minAb, maxAb=maxAb, profile=profile)
    dsk.save()
    #bf = BFCounter(contador=0, k=k, numKmers=numKmers, profile=profile)
    #bf.save()

    dsk.run(file=file_path, k=k, minAb=minAb, maxAb=maxAb)
    #Falta el response
    success = 'El proceso se ha puesto en la cola de espera. Para ver este proceso en la lista de procesos haga clic en el siguiente botón:'
    url_continuar = '/process/show'
    msg_continuar = 'Ver lista de procesos'
    return render(request, 'success.html', {'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})

@login_required(login_url='/login/')
def run_jellyfish(request):
    #REFERENCE FILE PATH
    file_id = request.POST.get('file', '')
    file_path = File.objects.get(id=int(file_id)).fileUpload.path
    #CONFIG
    m = request.POST.get('m', '')
    minAb = request.POST.get('minAb', '')
    maxAb = request.POST.get('maxAb', '')
    canonical = request.POST.get('canonical', '')
    profile = User.objects.select_related().get(id=request.user.pk).profile
    jfish = Jellyfish(contador=1, m=m, minAb=minAb, maxAb=maxAb, canonical=canonical, profile=profile)
    jfish.save()
    #bf = BFCounter(contador=0, k=k, numKmers=numKmers, profile=profile)
    #bf.save()

    jfish.run(file=file_path, m=m, minAb=minAb, maxAb=maxAb, canonical=canonical)
    #Falta el response
    success = 'El proceso se ha puesto en la cola de espera. Para ver este proceso en la lista de procesos haga clic en el siguiente botón:'
    url_continuar = '/process/show'
    msg_continuar = 'Ver lista de procesos'
    return render(request, 'success.html', {'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})

@login_required(login_url='/login/')
def run_kanalyze(request):
    #REFERENCE FILE PATH
    file_id = request.POST.get('file', '')
    file_path = File.objects.get(id=int(file_id)).fileUpload.path
    #CONFIG
    k = request.POST.get('k', '')
    formato = request.POST.get('formato', '')
    reverse = request.POST.get('reverse', '')
    profile = User.objects.select_related().get(id=request.user.pk).profile
    klyze = KAnalyze(contador=1, k=k, formato=formato, reverse=reverse, profile=profile)
    klyze.save()
    #bf = BFCounter(contador=0, k=k, numKmers=numKmers, profile=profile)
    #bf.save()

    klyze.run(file=file_path, k=k, formato=formato, reverse=reverse)
    #Falta el response
    success = 'El proceso se ha puesto en la cola de espera. Para ver este proceso en la lista de procesos haga clic en el siguiente botón:'
    url_continuar = '/process/show'
    msg_continuar = 'Ver lista de procesos'
    return render(request, 'success.html', {'success': success, 'url_continuar':url_continuar, 'msg_continuar':msg_continuar})


@login_required(login_url='/login/')
def run_ab2matrix(request):
    #Result FILE PATH
    result_paths = []
    result_id = request.POST.getlist('result', '')
    for r in result_id:
        result_paths.append(File.objects.get(id=int(r)).fileUpload.path)
    #CONFIG
    profile = User.objects.select_related().get(id=request.user.pk).profile

    ab = Abundance_to_Matrix(profile=profile)
    ab.save()
    ab.run(files=result_paths)
    success = 'El proceso se ha puesto en la cola de espera.'
    return render(request, 'success.html', {'success': success})

@login_required(login_url='/login/')
def run_expdiff(request):
    #Result FILE PATH
    matrix_id = request.POST.get('matrix', '')
    matrix_path = File.objects.get(id=int(matrix_id)).fileUpload.path
    #CONFIG
    profile = User.objects.select_related().get(id=request.user.pk).profile

    d = Differential_Expression(profile=profile)
    d.save()
    d.run(matrix=matrix_path)
    success = 'El proceso se ha puesto en la cola de espera.'
    return render(request, 'success.html', {'success': success})

@login_required(login_url='/login/')
def mapping(request):
    #REFERENCE FILE PATH
    reference_id = request.POST.get('reference', '')
    reference_path = File.objects.get(id=int(reference_id)).fileUpload.path
    #CONFIG
    type_id = request.POST.get('type', '')
    mapping_id = request.POST.get('mapping', '')
    profile = User.objects.select_related().get(id=request.user.pk).profile

    reads_se = []
    reads_1 = []
    reads_2 = []

    if mapping_id == '0':
        #BWA
        if type_id == '1':
            #SINGLE
            reads_id = request.POST.getlist('reads', '')
            for r in reads_id:
                reads_se.append(File.objects.get(id=int(r)).fileUpload.path)
            #print reads_se
            m = Mapeo(mapeador=0, tipo=0, profile=profile)
            m.save()
        else:
            #PAIRED
            #RIGHT READS FILE PATH
            rreads_id = request.POST.getlist('rreads', '')
            for rr in rreads_id:
                reads_1.append(File.objects.get(id=int(rr)).fileUpload.path)
            #LEFT READS FILE PATH
            lreads_id = request.POST.getlist('lreads', '')
            for lr in rreads_id:
                reads_2.append(File.objects.get(id=int(lr)).fileUpload.path)
            m = Mapeo(mapeador=0, tipo=1, profile=profile)
            m.save()
    else:
        #BOWTIE
        if type_id == '1':
            #SINGLE
            reads_id = request.POST.getlist('reads', '')
            for r in reads_id:
                reads_se.append(File.objects.get(id=int(r)).fileUpload.path)
            #print reads_se
            m = Mapeo(mapeador=1, tipo=0, profile=profile)
            m.save()
        else:
            #PAIRED
            #RIGHT READS FILE PATH
            rreads_id = request.POST.getlist('rreads', '')
            for rr in rreads_id:
                reads_2.append(File.objects.get(id=int(rr)).fileUpload.path)
            #LEFT READS FILE PATH
            lreads_id = request.POST.getlist('lreads', '')
            for lr in lreads_id:
                reads_1.append(File.objects.get(id=int(lr)).fileUpload.path)
            m = Mapeo(mapeador=1, tipo=1, profile=profile)
            m.save()

    m.run(reference=reference_path, reads_1=reads_1, reads_2=reads_2, reads_se=reads_se)
    #Falta el response
    return response
