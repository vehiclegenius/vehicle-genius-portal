from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.index_get), name='index'),
    path('<str:pk>', login_required(views.id_get), name='id'),
    path('answer-user-prompt/', login_required(views.answer_user_prompt_post), name='answer-user-prompt'),
]
