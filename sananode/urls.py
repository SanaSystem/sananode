"""sananode URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from server.views import NodeListView, UserListView, PermissionsView, api_root
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', api_root),
    url(r'^admin/', admin.site.urls),
    url(r'^nodes/$', NodeListView.as_view(), name='node-list'),
    url(r'^users/$', UserListView.as_view(), name='user-list'),
    url(r'^permissions/$', PermissionsView.as_view(), name='permission-list')
]

urlpatterns = format_suffix_patterns(urlpatterns)