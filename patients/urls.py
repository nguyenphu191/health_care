from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('appointments/', views.patient_appointments, name='patient_appointments'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
]