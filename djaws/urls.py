"""Pro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import admin
from django.urls import path, include, re_path,include
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from persons.views import HomeList

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",HomeList.as_view(), name="home"),
    re_path(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]



"""
urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include('api.urls')),
    #path('accounts/', include('allauth.urls')),
    path("",views.HomeList.as_view(), name="home"),
    path('users/', include('persons.urls')),
    path('movies/', include('items.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r'^signup/$', accounts_views.signup, name='signup'),
    re_path(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("dashboard/", views.HomeList.as_view(), name="dashboard"),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]
"""
