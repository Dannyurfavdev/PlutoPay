from django.urls import path

from . import views

urlpatterns=[
    path('', views.overview, name='overview'),
    path('signup_view/', views.signup_view, name='signup_view'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_transaction/', views.user_transaction, name='user_transaction'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('sell_crypto/', views.sell_crypto, name='sell_crypto'),
    path('sell_crypto_status/', views.sell_crypto_status, name='sell_crypto_status'),
    path('buy_airtime/', views.buy_airtime, name='buy_airtime'),
    path('buy_data/', views.buy_data, name='buy_data'),
    path('verify_gambler/', views.verify_gambler, name='verify_gambler'),
    path('bet_topup/', views.bet_topup, name='bet_topup'),
    path('verify_meter/', views.verify_meter, name='verify_meter'),
    path('buy_electricity/', views.buy_electricity, name='buy_electricity'),
    path('cable_tv/', views.cable_tv, name='cable_tv'),
    path('buy_cable_tv/', views.buy_cable_tv, name='buy_cable_tv'),
    path('renew_cable_tv/', views.renew_cable_tv, name='renew_cable_tv'),
    path('buy_crypto/', views.buy_crypto, name='buy_crypto'),
    path('buy_giftCard/', views.buy_giftCard, name='buy_giftCard'),
    path('sell_giftCard/', views.sell_giftCard, name='sell_giftCard'),
    #spath('crypto_data_view/', views.crypto_data_view, name='crypto_data_view'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('deposit_view_activation/', views.deposit_view_activation, name='deposit_view_activation'),
    path('deposit_view_activation_complete/<str:pk>/', views.deposit_view_activation_complete, name='deposit_view_activation_complete'),
    path('withdrawal/', views.withdrawal, name='withdrawal'),
    path('transfer_funds/', views.transfer_funds, name='transfer_funds'),
]