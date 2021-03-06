from django.shortcuts import render , redirect
from django.http import HttpResponse
import string
import random
import json
import time
import threading


from alphacode.models import RandomURLs
from django.utils import timezone
  
import requests

HOURS_OF_A_DAY = 24
#alphacode/
def index(request):
    return render(request,'alphacode/index.html')

#create/
def create(request):
    groupName = request.GET.get('name')
    N = 16
    while True:
        random_string = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
        try:
            row = RandomURLs.objects.get(random_url=random_string)
        except RandomURLs.DoesNotExist:
            break  
    Row = RandomURLs(random_url=random_string, group_name=groupName, timestamp=timezone.now(), valid=True)
    Row.save()
    return redirect(workplace, workplace_id=random_string)

#Create Page API
def createapi(request):
    groupName = "alphacode"
    N = 16
    random_string = ''.join(random.choice(string.digits) for _ in range(N))
    Row = RandomURLs(random_url=random_string, group_name=groupName, timestamp=timezone.now(), valid=True)
    Row.save()
    return HttpResponse(random_string)

#Check validity API
def verify_url_api(request):
    workplace_url = request.GET.get('key')
    url_row = RandomURLs.objects.get(random_url = workplace_url)
    
    try:
        if (url_row.valid == False) or (url_row.isExpired(HOURS_OF_A_DAY, unit="hour")):
            url_row.setValidity(False)
            return HttpResponse("False")
    except url_row.DoesNotExist:
        return HttpResponse("False")
    
    return HttpResponse("True")

#alphacode/(workplace_id)
def workplace(request,workplace_id):
    try:
        groupName = RandomURLs.objects.get(random_url=workplace_id)
        if (groupName.valid == False) or (groupName.isExpired(HOURS_OF_A_DAY, unit="hour")):
            groupName.setValidity(False)
            return redirect('error-view')
    except RandomURLs.DoesNotExist:
        return redirect('error-view')
    context = {
        "workplace_id": workplace_id,
        "group_name"  : groupName.group_name,
    }
    return render(request,'alphacode/workplace.html',context)

def getTag(request):
    #       run ML function for the tag here
    #       input string
    #       output string
    data = request.GET.get('Smt')
    predictor_server_path = "http://localhost:5000"
    try:
        r = requests.post(predictor_server_path, json={'data': data})
    except Exception, e:
        print "Predictor Server inaccessible!  Default tag 'implementation' used."
        print "Error: " + str(e)
        return HttpResponse("implementation")
    try:
        if r.status_code == 200:
            resp = r.json()['prediction']
            if len(resp) > 0:
                return HttpResponse(", ".join(resp))
            else:
                return HttpResponse("N/A")
        else:
            print "Predictor Server returned error code!  Default tag 'implementation' used."
            return HttpResponse('implementation')
    except Exception, e:
        print "Encountered internal error while parsing Predictor Server response!  Default tag 'implementation' used."
        print "Error: " + str(e)
        return HttpResponse('implementation')

def error_page(request):
    context = {
    }
    return render(request,'alphacode/error.html',context)