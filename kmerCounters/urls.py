from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('processing.views',
    url(r'^$', 'home', name='home'),
    url(r'^abundancia/$', 'abundancia_form'),
    url(r'^ab2matrix/$', 'ab2matrix_form'),
    url(r'^diffexp/$', 'diffexp_form'),
    url(r'^register/$', 'register_user'),
    url(r'^login/$', 'log_in'),
    url(r'^login/auth/$', 'auth_view'),
    url(r'^logout/$', 'log_out'),
    url(r'^files/$', 'show_files'),
    url(r'^process/$', 'show_processes'),
    url(r'^files/upload/$', 'show_fileupload', name='file_upload'),
    url(r'^files/submit/$', 'filesubmit'),
    url(r'^files/success/$', 'upload_success', name='upload_success'),
    url(r'^files/delete/(\d+)/$', 'delete_file'),
    url(r'^files/edit/(\d+)/$', 'show_edit_file', name='show_edit_file'),
    url(r'^files/(?P<id_file>\d+)/$', 'download_file', name="download_file"),
    url(r'^process/show/(?P<process_id>\d+)/$', 'show_specific_process', name="show_specific_process"),
    url(r'^process/show/$', 'show_process', name='show_process'),
    url(r'^editfile/$', 'editfile'),
    url(r'^run/abundancia/$', 'run_abundancia'),
    url(r'^run/ab2matrix/$', 'run_ab2matrix'),
    url(r'^run/expdiff/$', 'run_expdiff'),
    # Examples:
    # url(r'^$', 'ExpDiff.views.home', name='home'),
    # url(r'^ExpDiff/', include('ExpDiff.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
