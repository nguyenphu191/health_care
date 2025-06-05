from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Custom logout view để cho phép GET request
class CustomLogoutView(auth_views.LogoutView):
    http_method_names = ['get', 'post', 'options']
    template_name = 'registration/logout.html'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/doctors/', views.manage_doctors, name='manage_doctors'),
    path('admin/doctors/create/', views.admin_create_doctor, name='admin_create_doctor'),
    path('admin/doctors/<int:doctor_id>/toggle/', views.toggle_doctor_verification, name='toggle_doctor_verification'),
    path('admin/doctors/<int:doctor_id>/', views.doctor_detail_admin, name='doctor_detail_admin'),
    path('admin/patients/', views.manage_patients, name='manage_patients'),
    path('admin/patients/create/', views.admin_create_patient, name='admin_create_patient'),
    path('admin/patients/<int:patient_id>/', views.patient_detail_admin, name='patient_detail_admin'),
    
    # Profile editing URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/doctor/edit/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('profile/patient/edit/', views.edit_patient_profile, name='edit_patient_profile'),
]