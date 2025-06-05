from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('appointments/<int:appointment_id>/update/', views.update_appointment_status, name='update_appointment_status'),
    path('schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('schedule/<int:schedule_id>/update/', views.update_schedule, name='update_schedule'),
    path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('answer/<int:question_id>/', views.answer_question, name='answer_question'),
]