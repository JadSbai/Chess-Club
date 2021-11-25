"""Wildebeest URL Configuration

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

from django.contrib import admin
from django.urls import path, include
from chessclubs import views
import notifications.urls
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('club/', views.show_club, name='show_club'), # TODO
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.password, name='password'),
    path('change_profile/', views.change_profile, name='change_profile'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('user/<int:user_id>', views.show_user, name='show_user'),
    path('promote/<int:user_id>', views.promote, name='promote'),
    path('demote/<int:user_id>', views.demote, name='demote'),
    path('transfer_ownership/<int:user_id>', views.transfer_ownership, name='transfer_ownership'),
    path('users/', views.user_list, name='user_list'),
    path(r'mark-as-read/(<slug>[-\w]+)/', views.mark_as_read, name='mark_as_read'),
    path('accept/<int:user_id>', views.accept, name='accept'),
    path('deny/<int:user_id>', views.deny, name='deny'),
    path('acknowledged/', views.acknowledged, name='acknowledged'),
    path('view_applications/', views.view_applications, name='view_applications'),
    path('create_club/', views.create_club, name='create_club'),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications'))
]
handler404 = "chessclubs.views.page_not_found_view"
