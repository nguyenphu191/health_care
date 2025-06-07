from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot interface
    path('', views.ChatbotView.as_view(), name='chat_interface'),
    
    # API endpoints
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/history/', views.ChatHistoryView.as_view(), name='chat_history'),
    path('api/feedback/', views.ChatFeedbackView.as_view(), name='chat_feedback'),
    path('api/doctors/', views.ChatDoctorsView.as_view(), name='chat_doctors'),
    path('api/specializations/', views.ChatSpecializationsView.as_view(), name='chat_specializations'),
    path('api/quick-action/', views.QuickActionView.as_view(), name='quick_action'),
    
    # Admin
    path('admin-dashboard/', views.chatbot_admin_dashboard, name='admin_dashboard'),
]