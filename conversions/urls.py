from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'start/cid-(?P<campaign_id>[0-9]+)/pid-(?P<partner_id>[0-9]+)/$', 'conversions.views.start'),
                       (r'finish/$', 'conversions.views.finish'),
                       (r'bannerlist/$', 'conversions.views.bannerlist'),
                       (r'bannerlist/(?P<campaign_id>[0-9]+)/$', 'conversions.views.bannerlist'),
                       (r'cash_requests/$', 'conversions.views.cash_requests'),
                       (r'cash/$', 'conversions.views.cash'),
                       (r'pay/(?P<rid>[0-9]+)/$', 'conversions.views.pay'),
                       (r'rawexport/$', 'conversions.views.raw_data'),
                       )