from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profile, name='profile'),
    path('send-money', views.send_money, name='send-money'),
    path('send-money-confirm', views.send_money_confirm, name='send-money-confirm'),
    path('transactions', views.transactions, name='transactions'),
    path('request-money', views.request_money, name='request-money'),
    path('request-money-confirm', views.request_money_confirm, name='request-money-confirm'),
    path('request-detail', views.request_detail, name='request-detail'),
    path('cards-and-accounts', views.card_and_account, name='cards-and-accounts'),

]
