from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('processing.views',
    url(r'^$', 'home', name='home'),
    # Tools form
    url(r'^tools/bfcounter$', 'bfcounter_form'),
    url(r'^tools/dsk$', 'bfcounter_form'),
    url(r'^tools/jellyfish$', 'bfcounter_form'),
    url(r'^tools/kanalyze$', 'bfcounter_form'),
    url(r'^tools/khmer$', 'bfcounter_form'),
    url(r'^tools/kmc2$', 'bfcounter_form'),
    url(r'^tools/mspkmercounter$', 'bfcounter_form'),
    url(r'^tools/tallymer$', 'bfcounter_form'),
    url(r'^tools/turtle$', 'bfcounter_form'),
    # Users admin
    url(r'^register/$', 'register_user'),
    url(r'^login/$', 'log_in'),
    url(r'^login/auth/$', 'auth_view'),
    url(r'^logout/$', 'log_out'),
    # Files admin
    url(r'^files/$', 'show_files'),
    url(r'^files/upload/$', 'show_fileupload', name='file_upload'),
    url(r'^files/submit/$', 'filesubmit'),
    url(r'^files/success/$', 'upload_success', name='upload_success'),
    url(r'^files/delete/(\d+)/$', 'delete_file'),
    url(r'^files/edit/(\d+)/$', 'show_edit_file', name='show_edit_file'),
    url(r'^files/(?P<id_file>\d+)/$', 'download_file', name="download_file"),
    # Proccesses admin
    url(r'^process/show/(?P<process_id>\d+)/$', 'show_specific_process', name="show_specific_process"),
    url(r'^process/show/$', 'show_process', name='show_process'),
    url(r'^process/$', 'show_processes'),
    url(r'^editfile/$', 'editfile'),
    # Tools execution
    url(r'^run/abundancia/$', 'run_abundancia'),
    url(r'^run/ab2matrix/$', 'run_ab2matrix'),
    url(r'^run/expdiff/$', 'run_expdiff'),
    # Admin admin
    url(r'^admin/', include(admin.site.urls)),
)
