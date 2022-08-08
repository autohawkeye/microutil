"""micro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from microutil.server.site import jsonrpc_site
from django.urls import path
from .views import test_views

urlpatterns = [
    path('get/test123', test_views.get_test),
    # url(r'^json/', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),  # 1.0.2 版本
    url(r'^jsonp/', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),  # >=1.0.3 版本
]
