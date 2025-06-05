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
]