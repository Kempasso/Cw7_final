from django.urls import path

from apps.bot import views

urlpatterns = [
    path('verify', views.BotVerifyView.as_view(), name='bot_verify'), ]
