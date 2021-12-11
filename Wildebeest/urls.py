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
    path('club/<int:club_id>', views.show_club, name='show_club'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.password, name='password'),
    path('change_profile/', views.change_profile, name='change_profile'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('club/<club_name>', views.show_club, name='show_club'),
    path('<club_name>/user/<int:user_id>', views.show_user, name='show_user'),
    path('<club_name>/promote/<int:user_id>', views.promote, name='promote'),
    path('<club_name>/demote/<int:user_id>', views.demote, name='demote'),
    path('<club_name>/transfer_ownership/<int:user_id>', views.transfer_ownership, name='transfer_ownership'),
    path('<club_name>/users/', views.user_list, name='user_list'),
    path(r'mark-as-read/(<slug>[-\w]+)/', views.mark_as_read, name='mark_as_read'),
    path('<club_name>/accept/<int:user_id>', views.accept, name='accept'),
    path('<club_name>/deny/<int:user_id>', views.deny, name='deny'),
    path('<club_name>/acknowledge/', views.acknowledge, name='acknowledge'),
    path('<club_name>/view_applications/', views.view_applications, name='view_applications'),
    path('create_club/', views.create_club, name='create_club'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path('apply_club/<club_name>', views.apply_club, name='apply_club'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('<club_name>/create_tournament/', views.create_tournament, name='create_tournament'),
    path('<club_name>/ban/<int:user_id>', views.ban, name='ban'),
    path('<club_name>/leave/', views.leave, name='leave'),
    path('<club_name>/tournament/<tournament_name>/', views.show_tournament, name='show_tournament'),
    path('<club_name>/create_tournament/', views.create_tournament, name='create_tournament'),
    path('<club_name>/tournament/<tournament_name>/apply/', views.apply_tournament, name='apply_tournament'),
    path('<club_name>/tournament/<tournament_name>/withdraw/', views.withdraw_tournament, name='withdraw_tournament'),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications'))
]
handler404 = "chessclubs.views.page_not_found_view"
