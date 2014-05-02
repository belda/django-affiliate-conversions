from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
   (r'^conversions/', include(conversion.urls)),
   (r'^admin/', include(admin.site.urls)),
)   