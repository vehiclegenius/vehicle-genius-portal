from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_ethereum_challenge, name='get_ethereum_challenge'),
    path('generate_challenge/', views.generate_challenge, name='generate_challenge'),
    path('submit_challenge/', views.submit_challenge, name='submit_challenge'),
    path('callback', views.callback, name='callback'),
]
