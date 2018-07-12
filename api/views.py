from django.shortcuts import render
from django.http import JsonResponse 
import ipfsapi
# Create your views here.
def display_ipfs(request):
    
    
    return JsonResponse({'data':api.cat(hash).decode()})
