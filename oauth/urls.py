from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    path('', views.get_challenge, name='oauth_get_challenge'),
    path('generate_challenge/', views.generate_challenge, name='oauth_generate_challenge'),
    path('submit_challenge/', views.submit_challenge, name='oauth_submit_challenge'),
]
