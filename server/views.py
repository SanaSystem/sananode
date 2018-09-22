from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# Create your views here.
@csrf_exempt
def resigter_users(request):
    data = json.loads(request.body)
    print(data)
    return JsonResponse({"gotit":True})

@csrf_exempt
def register_nodes(request):
    data = json.loads(request.body)
    print(data)
    return JsonResponse({"gotit":True})