from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'hcal.views.index'),
    url(r'^(?P<theme>\w+)/$', 'hcal.views.index'),
    url(r'^(?P<theme>\w+)/(?P<hyear>\d+)/$', 'hcal.views.index'),
    
    # Examples:
    # url(r'^$', 'hcaldjango.views.home', name='home'),
    # url(r'^hcaldjango/', include('hcaldjango.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
