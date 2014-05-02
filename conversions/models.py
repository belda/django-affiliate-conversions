# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Web(models.Model):
    ''' Represents one website. Top level of the structure '''
    name = models.CharField(max_length=50)
    url  = models.URLField(verify_exists=False)
    def __unicode__(self):
        return self.name
    
class Campaign(models.Model):
    ''' Represents a campaign consisting of multiple Banners. Mid level of the structure '''
    name    = models.CharField(max_length=100, help_text=_("Name of the campaign"))
    web     = models.ForeignKey(Web)
    target  = models.URLField(verify_exists=False)
    def __unicode__(self):
        return self.name + " ("+self.web.name+")"
    
    
BannerTypeChoices = ( (1, _("Normal weblink") ),
                      (2, _("Image (jpg/png/gif)") ),
                      (3, _("Flash") ))

class Banner(models.Model):
    ''' Represents a concrete banner/link that is being displayed. '''
    name        = models.CharField(max_length=50)
    campaign    = models.ForeignKey(Campaign)
    type        = models.IntegerField(choices = BannerTypeChoices)
    size_x      = models.IntegerField(blank=True, null=True)
    size_y      = models.IntegerField(blank=True, null=True)
    file        = models.FileField(blank=True, null=True, upload_to="banners/")
    def __unicode__(self):
        return self.name+" ("+self.campaign.name+"/"+self.campaign.web.name+")"
    
class ViewConversion(models.Model):
    ''' A simple conversion registered '''
    partner         = models.ForeignKey(User)
    campaign        = models.ForeignKey(Campaign)
    view_ts         = models.DateTimeField(auto_now_add=True)
    conversion      = models.BooleanField(default=False)
    conversion_ts   = models.DateTimeField(blank=True, null=True)
    remote_ip       = models.IPAddressField(blank=True, null=True)
    reward          = models.FloatField(default=0.0)
    reward_nonse    = models.CharField(max_length=63, blank=True, null=True)
    note            = models.TextField(blank=True, null=True)
    
class CashRequest(models.Model):
    ''' Represents the partner will to request the balance to be payed '''
    partner     = models.ForeignKey(User)
    request_ts  = models.DateTimeField(auto_now_add=True)
    amount      = models.FloatField()
    payed_ts    = models.DateTimeField(blank=True, null=True)
    
