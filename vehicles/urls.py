from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('add', login_required(views.add_get), name='add'),
    path('<str:pk>/prompt/<int:index>', login_required(views.id_prompt_get), name='id'),
    path('<str:pk>', login_required(views.id_get), name='id'),
    path('answer-user-prompt/', login_required(views.answer_user_prompt_post), name='answer-user-prompt'),
    path('feedback/', login_required(views.feedback_post), name='feedback'),
]
