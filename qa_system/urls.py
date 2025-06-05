from django.urls import path
from . import views

urlpatterns = [
    path('', views.qa_list, name='qa_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
]