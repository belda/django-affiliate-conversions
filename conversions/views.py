from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from conversions.models import *
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
import csv


def start(request, partner_id, campaign_id):
    ''' Registers the start of the conversion tracking '''
    if 'vcr' not in request.session:
        try:
            partner  = User.objects.get(pk=str(partner_id))
            campaign = Campaign.objects.get(pk=str(campaign_id))
        except User.DoesNotExist, Campaign.DoesNotExist:
            return HttpResponse("Nonexistent campaign/partner combination") 
        vc = ViewConversion(partner = partner, campaign = campaign)
        if 'REMOTE_ADDR' in request.META:
            vc.remote_ip = request.META['REMOTE_ADDR']
        vc.save()
        request.session['vcr'] = vc.pk 
        return HttpResponse("OK")
    else:
        return HttpResponse("Session exists")

def finish(request):
     ''' Registers the end of the conversion tracking - conversion itself '''
    if 'vcr' in request.session:
        try:
            vc = ViewConversion.objects.get(pk = request.session['vcr'])
        except ViewConversion.DoesNotExist:
            return HttpResponse("Nosess")
        vc.conversion = True
        vc.conversion_ts = datetime.now()
        if 'reward' in request.GET:
            vc.reward = request.GET['reward']
        if 'reward_nonse' in request.GET:
            vc.reward_nonse = request.GET['reward_nonse']
        if 'note' in request.GET:
            vc.note = request.GET['note'] 
        vc.save()
        return HttpResponse("Finish")
    return HttpResponse("No session")
            
@login_required
def bannerlist(request, campaign_id=""):
    ''' List of available banners '''
    if campaign_id=="":
        banners = Banner.objects.all().order_by('campaign__web','campaign','pk')
    else:
        banners = Banner.objects.filter(campaign__pk=int(campaign_id)).order_by('campaign__web','campaign','pk')
    campaigns = Campaign.objects.all().order_by('web','pk')
    return render_to_response("conversions/banner_list.html",
                              {'banners' : banners, 'campaigns' : campaigns, 'user':request.user, 'BASEURL' : settings.BASEURL}, 
                              context_instance=RequestContext(request))


def get_crb(user):
    ''' returns unpayed balance for that user '''
    if len(CashRequest.objects.filter(partner=user).order_by('-request_ts'))>0:
        lastcr = CashRequest.objects.filter(partner=user).order_by('-request_ts')[0]
        balance = ViewConversion.objects.filter(partner=user, conversion=True, conversion_ts__gt=lastcr.request_ts).aggregate(Sum('reward'))['reward__sum']
        if balance==None:
            balance=0
        return (lastcr,balance)
    else:
        balance = ViewConversion.objects.filter(partner=user, conversion=True).aggregate(Sum('reward'))['reward__sum']
        if balance==None:
            balance=0
        return (None,balance)

@login_required
def cash_requests(request):
    ''' Overview of the cash requests'''
    c = {'MINDAYS' : settings.MINDAYS, 'MINCASH' : settings.MINCASH}
    if request.user.is_staff:
        c['staff'] = True
        c['payed_requests']     = CashRequest.objects.exclude(payed_ts=None).order_by('request_ts') 
        c['unpayed_requests']   = CashRequest.objects.filter(payed_ts=None).order_by('request_ts')
        c['userbalances']       = User.objects.all()
        for b in c['userbalances']:
            b.lastcr, b.balance = get_crb(b)
    else:
        c['staff'] = False
        c['payed_requests']       = CashRequest.objects.filter(partner = request.user.pk).exclude(payed_ts=None).order_by('request_ts') 
        c['unpayed_requests']     = CashRequest.objects.filter(partner = request.user.pk, payed_ts=None).order_by('request_ts')
        c['lastcr'], c['balance'] = get_crb(request.user)
        c['cancash'] = ( settings.MINCASH<= c['balance'] and ( (c['lastcr'] == None and settings.MINDAYS<=(datetime.now()-request.user.date_joined).days) or (c['lastcr'] != None and settings.MINDAYS<= (datetime.now()-c['lastcr'].payed_ts).days )) )
    return render_to_response("conversions/cash_requests.html", c, context_instance=RequestContext(request))

@login_required        
def cash(request):
    ''' Create a cash request '''
    c = {}
    c['lastcr'], c['balance'] = get_crb(request.user)
    if ( settings.MINCASH<= c['balance'] and ( (c['lastcr'] == None and settings.MINDAYS<=(datetime.now()-request.user.date_joined).days) or (c['lastcr'] != None and settings.MINDAYS<= (datetime.now()-c['lastcr'].payed_ts).days )) ):
        cr = CashRequest(partner=request.user, request_ts=datetime.now(), amount=c['balance'])
        cr.save()
        return HttpResponseRedirect("/conversions/cash_requests/")
    else:
        return HttpResponse(_("You can not cash the money at this time"))
    
@login_required        
def pay(request, rid):
    ''' Mark the cash request as payed '''
    try:
        cr = CashRequest.objects.get(pk=int(rid))
        if cr.payed_ts==None:
            cr.payed_ts = datetime.now()
            cr.save()
            return HttpResponseRedirect("/conversions/cash_requests/")
        else:
            return HttpResponse(_("Cash request already payed"))
    except CashRequest.DoesNotExist:
        return HttpResponse(_("No such cashrequest"))
    
@login_required
def raw_data(request):
    ''' Data export '''
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'

    writer = csv.writer(response)
    vcs = ViewConversion.objects.all() if request.user.is_staff else ViewConversion.objects.filter(partner=request.user)
    for vc in vcs:
        writer.writerow([vc.pk, vc.partner.username, vc.campaign.name, vc.campaign.web.name, vc.view_ts, vc.conversion, vc.conversion_ts, vc.remote_ip, vc.reward, vc.reward_nonse, vc.note])
    return response
