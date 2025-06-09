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
    
    # Disease Prediction endpoints
    path('api/disease-prediction/', views.DiseasePredictionView.as_view(), name='disease_prediction'),
    path('api/prediction-history/', views.PredictionHistoryView.as_view(), name='prediction_history'),
    path('api/prediction-feedback/', views.PredictionFeedbackView.as_view(), name='prediction_feedback'),
    
    # Admin
    path('admin-dashboard/', views.chatbot_admin_dashboard, name='admin_dashboard'),
]