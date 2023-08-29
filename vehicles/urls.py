from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('add', login_required(views.add_get), name='add'),
    path('add/<str:pk>/fetch/', login_required(views.add_fetch_post), name='add_fetch'),
    path('<str:pk>/prompt/<int:index>', login_required(views.id_prompt_get), name='prompt'),
    path('<str:pk>/chatbot', login_required(views.id_chatbot_get), name='chatbot'),
    path('<str:pk>', login_required(views.id_get), name='id'),
    path('<str:pk>/edit', login_required(views.id_edit), name='id_edit'),
    path('answer-user-prompt/', login_required(views.answer_user_prompt_post), name='answer-user-prompt'),
    path('feedback/', login_required(views.feedback_post), name='feedback'),
]
