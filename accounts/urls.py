from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]