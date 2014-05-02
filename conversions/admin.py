# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django import forms
from conversions.models import *

admin.site.register( Web )
admin.site.register( Campaign )
admin.site.register( Banner )