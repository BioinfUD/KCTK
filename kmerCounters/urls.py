from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('processing.views',
    url(r'^$', 'home', name='home'),
    # Tools form
    url(r'^tools/bfcounter$', 'bfcounter_form'),
    url(r'^tools/dsk$', 'dsk_form'),
    url(r'^tools/jellyfish$', 'jellyfish_form'),
    url(r'^tools/kanalyze$', 'kanalyze_form'),
    url(r'^tools/khmer$', 'khmer_form'),
    url(r'^tools/kmc2$', 'kmc2_form'),
    url(r'^tools/mspkmercounter$', 'mspkmercounter_form'),
    url(r'^tools/tallymer$', 'tallymer_form'),
    url(r'^tools/turtle$', 'turtle_form'),
    # Users admin
    url(r'^register/$', 'register_user'),
    url(r'^login/$', 'log_in'),
    url(r'^login/auth/$', 'auth_view'),
    url(r'^logout/$', 'log_out'),
    # Files admin
    url(r'^files/$', 'show_files'),
    url(r'^files/upload/$', 'show_fileupload', name='file_upload'),
    url(r'^files/submit/$', 'filesubmit'),
    #url(r'^files/success/$', 'upload_success', name='upload_success'),
    url(r'^files/delete/(\d+)/$', 'delete_file'),
    url(r'^files/edit/(\d+)/$', 'show_edit_file', name='show_edit_file'),
    url(r'^files/(?P<id_file>\d+)/$', 'download_file', name="download_file"),
    # Proccesses admin
    url(r'^process/show/(?P<process_id>\d+)/$', 'show_specific_process', name="show_specific_process"),
    url(r'^process/show/$', 'show_process', name='show_process'),
    url(r'^process/$', 'show_processes'),
    url(r'^editfile/$', 'editfile'),
    # Tools execution
    url(r'^run/bfcounter/$', 'run_bfcounter'),
    url(r'^run/dsk/$', 'run_dsk'),
    url(r'^run/jellyfish/$', 'run_jellyfish'),
    url(r'^run/kanalyze/$', 'run_kanalyze'),
    url(r'^run/khmer/$', 'run_khmer'), #pendiente
    url(r'^run/kmc2/$', 'run_kmc2'),
    url(r'^run/mspkmercounter/$', 'run_mspkmercounter'), #pendiente
    url(r'^run/tallymer/$', 'run_tallymer'), #pendiente
    url(r'^run/turtle/$', 'run_turtle'),

    # Admin admin
    url(r'^admin/', include(admin.site.urls)),
)
