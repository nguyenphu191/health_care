from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
import json
from .models import ChatSession, ChatMessage, ChatbotFeedback
from .services import ChatbotService
from .forms import ChatbotFeedbackForm
from doctors.models import Doctor, Specialization
from .ml_models import DiseasePredictor
from .models import Symptom, DiseasePrediction
class ChatbotView(View):
    """Main chatbot interface"""
    
    def get(self, request):
        """Hiển thị giao diện chatbot"""
        context = {
            'user': request.user if request.user.is_authenticated else None,
        }
        return render(request, 'chatbot/chat_interface.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """API endpoint cho chatbot"""
    
    def post(self, request):
        """Xử lý tin nhắn chat"""
        try:
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            action_type = data.get('action_type', '')
            selected_symptoms = data.get('selected_symptoms', [])
            prediction_id = data.get('prediction_id', '')
            feedback_data = data.get('feedback', {})
            
            if not message_content and not action_type:
                return JsonResponse({'error': 'Message content or action is required'}, status=400)
            
            # Khởi tạo service
            chatbot_service = ChatbotService()
            
            # Lấy hoặc tạo session
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            if not session_key and not user:
                request.session.create()
                session_key = request.session.session_key
            
            session = chatbot_service.get_or_create_session(user=user, session_key=session_key)
            
            # Xử lý các action types khác nhau
            if action_type == 'symptom_selection':
                bot_response = chatbot_service.handle_symptom_selection(session, selected_symptoms)
            elif action_type == 'prediction_feedback':
                success = chatbot_service.handle_prediction_feedback(
                    prediction_id, 
                    feedback_data.get('type', ''),
                    feedback_data.get('comment', '')
                )
                return JsonResponse({'success': success})
            elif action_type == 'quick_symptom':
                bot_response = chatbot_service.handle_quick_symptom(message_content, session)
            else:
                # Xử lý tin nhắn thông thường
                bot_response = chatbot_service.process_message(session, message_content)
            
            # Lưu response vào database nếu cần
            if isinstance(bot_response, dict):
                bot_message = ChatMessage.objects.create(
                    session=session,
                    sender='bot',
                    message_type=bot_response.get('type', 'text'),
                    content=bot_response.get('content', ''),
                    metadata=bot_response.get('metadata', {})
                )
                
                response_data = {
                    'success': True,
                    'bot_message': {
                        'id': bot_message.id,
                        'content': bot_message.content,
                        'type': bot_message.message_type,
                        'metadata': bot_message.metadata,
                        'timestamp': bot_message.created_at.isoformat()
                    },
                    'session_id': str(session.id)
                }
            else:
                # bot_response là ChatMessage object
                response_data = {
                    'success': True,
                    'bot_message': {
                        'id': bot_response.id,
                        'content': bot_response.content,
                        'type': bot_response.message_type,
                        'metadata': bot_response.metadata,
                        'timestamp': bot_response.created_at.isoformat()
                    },
                    'session_id': str(session.id)
                }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class ChatHistoryView(View):
    """Lấy lịch sử chat"""
    
    def get(self, request):
        try:
            # Lấy session
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            if user:
                session = ChatSession.objects.filter(user=user, is_active=True).first()
            elif session_key:
                session = ChatSession.objects.filter(session_key=session_key, is_active=True).first()
            else:
                return JsonResponse({'messages': []})
            
            if not session:
                return JsonResponse({'messages': []})
            
            # Lấy tin nhắn
            messages = ChatMessage.objects.filter(session=session).order_by('created_at')
            
            messages_data = []
            for msg in messages:
                messages_data.append({
                    'id': msg.id,
                    'sender': msg.sender,
                    'content': msg.content,
                    'type': msg.message_type,
                    'metadata': msg.metadata,
                    'timestamp': msg.created_at.isoformat()
                })
            
            return JsonResponse({'messages': messages_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ChatFeedbackView(View):
    """API để gửi feedback"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            rating = data.get('rating')
            comment = data.get('comment', '')
            
            if not session_id or not rating:
                return JsonResponse({'error': 'Session ID and rating are required'}, status=400)
            
            session = get_object_or_404(ChatSession, id=session_id)
            
            feedback = ChatbotFeedback.objects.create(
                session=session,
                rating=int(rating),
                comment=comment
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Cảm ơn bạn đã đóng góp ý kiến!'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ChatDoctorsView(View):
    """API để lấy danh sách bác sĩ"""
    
    def get(self, request):
        try:
            specialty = request.GET.get('specialty', '')
            
            doctors_query = Doctor.objects.filter(is_verified=True)
            
            if specialty:
                doctors_query = doctors_query.filter(
                    specializations__name__icontains=specialty
                )
            
            doctors = doctors_query[:10]
            
            doctors_data = []
            for doctor in doctors:
                doctors_data.append({
                    'id': doctor.user.id,
                    'name': doctor.user.get_full_name(),
                    'specializations': [spec.name for spec in doctor.specializations.all()],
                    'experience_years': doctor.experience_years,
                    'consultation_fee': float(doctor.consultation_fee),
                    'bio': doctor.bio[:200] + '...' if len(doctor.bio) > 200 else doctor.bio
                })
            
            return JsonResponse({'doctors': doctors_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ChatSpecializationsView(View):
    """API để lấy danh sách chuyên khoa"""
    
    def get(self, request):
        try:
            specializations = Specialization.objects.all()
            
            specs_data = []
            for spec in specializations:
                specs_data.append({
                    'id': spec.id,
                    'name': spec.name,
                    'description': spec.description
                })
            
            return JsonResponse({'specializations': specs_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class QuickActionView(View):
    """Xử lý các hành động nhanh từ chatbot"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'book_appointment':
                return self.handle_appointment_booking(request, data)
            elif action == 'find_doctors':
                return self.handle_find_doctors(request, data)
            elif action == 'emergency_help':
                return self.handle_emergency_help()
            else:
                return JsonResponse({'error': 'Unknown action'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def handle_appointment_booking(self, request, data):
        """Xử lý đặt lịch nhanh"""
        if not request.user.is_authenticated or request.user.user_type != 'patient':
            return JsonResponse({
                'error': 'Bạn cần đăng nhập với tài khoản bệnh nhân để đặt lịch hẹn',
                'redirect': '/login/'
            })
        
        # Chuyển hướng đến trang đặt lịch
        return JsonResponse({
            'success': True,
            'message': 'Chuyển hướng đến trang đặt lịch hẹn...',
            'redirect': '/patients/book-appointment/'
        })
    
    def handle_find_doctors(self, request, data):
        """Tìm bác sĩ theo chuyên khoa"""
        specialty = data.get('specialty', '')
        
        if specialty:
            doctors = Doctor.objects.filter(
                is_verified=True,
                specializations__name__icontains=specialty
            )[:5]
            
            doctors_info = []
            for doctor in doctors:
                doctors_info.append({
                    'name': doctor.user.get_full_name(),
                    'experience': f"{doctor.experience_years} năm kinh nghiệm",
                    'fee': f"{doctor.consultation_fee:,.0f} VNĐ"
                })
            
            return JsonResponse({
                'success': True,
                'doctors': doctors_info,
                'message': f'Tìm thấy {len(doctors_info)} bác sĩ chuyên khoa {specialty}'
            })
        
        return JsonResponse({'error': 'Vui lòng cung cấp chuyên khoa'})
    
    def handle_emergency_help(self):
        """Xử lý trợ giúp cấp cứu"""
        return JsonResponse({
            'success': True,
            'message': 'Thông tin cấp cứu',
            'emergency_info': {
                'hotline': '115',
                'hospitals': [
                    'Bệnh viện Bạch Mai - 024 3869 3731',
                    'Bệnh viện Việt Đức - 024 3825 3531',
                    'Bệnh viện 103 - 024 3972 5134'
                ]
            }
        })

# Views cho admin
@login_required
def chatbot_admin_dashboard(request):
    """Dashboard quản lý chatbot"""
    if not request.user.is_staff:
        return redirect('home')
    
    # Thống kê cơ bản
    total_sessions = ChatSession.objects.count()
    total_messages = ChatMessage.objects.count()
    recent_sessions = ChatSession.objects.order_by('-created_at')[:10]
    
    context = {
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'chatbot/admin_dashboard.html', context)
@method_decorator(csrf_exempt, name='dispatch')
class DiseasePredictionView(View):
    """API endpoint riêng cho disease prediction"""
    
    def post(self, request):
        """Thực hiện dự đoán bệnh"""
        try:
            data = json.loads(request.body)
            selected_symptoms = data.get('symptoms', [])
            
            if not selected_symptoms:
                return JsonResponse({
                    'error': 'No symptoms selected'
                }, status=400)
            
            # Lấy session
            user = request.user if request.user.is_authenticated else None
            if not user:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)
            
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            from .services import ChatbotService
            chatbot_service = ChatbotService()
            session = chatbot_service.get_or_create_session(user=user, session_key=session_key)
            
            # Thực hiện dự đoán
            disease_predictor = DiseasePredictor()
            result = disease_predictor.predict_from_symptoms(session, selected_symptoms)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request):
        """Lấy danh sách triệu chứng"""
        try:
            disease_predictor = DiseasePredictor()
            symptoms_by_category = disease_predictor.get_available_symptoms()
            
            return JsonResponse({
                'symptoms_by_category': symptoms_by_category
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PredictionHistoryView(View):
    """Lịch sử dự đoán của người dùng"""
    
    @method_decorator(login_required, name='dispatch')
    def get(self, request):
        """Lấy lịch sử dự đoán"""
        try:
            predictions = DiseasePrediction.objects.filter(
                session__user=request.user
            ).order_by('-created_at')[:10]
            
            predictions_data = []
            for pred in predictions:
                symptoms = [s.name for s in pred.selected_symptoms.all()]
                predictions_data.append({
                    'id': pred.id,
                    'symptoms': symptoms,
                    'predictions': pred.predicted_diseases,
                    'confidence': pred.confidence_score,
                    'feedback': pred.user_feedback,
                    'created_at': pred.created_at.isoformat()
                })
            
            return JsonResponse({
                'predictions': predictions_data
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PredictionFeedbackView(View):
    """API để gửi feedback về dự đoán"""
    
    @method_decorator(csrf_exempt, name='dispatch')
    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        try:
            data = json.loads(request.body)
            prediction_id = data.get('prediction_id')
            feedback_type = data.get('feedback_type')
            rating = data.get('rating', 3)
            comment = data.get('comment', '')
            
            if not prediction_id or not feedback_type:
                return JsonResponse({
                    'error': 'Prediction ID and feedback type required'
                }, status=400)
            
            # Lấy prediction
            prediction = DiseasePrediction.objects.get(
                id=prediction_id,
                session__user=request.user
            )
            
            # Cập nhật feedback
            prediction.user_feedback = feedback_type
            prediction.save()
            
            # Tạo detailed feedback nếu có
            if comment or rating != 3:
                from .models import PredictionFeedback
                PredictionFeedback.objects.update_or_create(
                    prediction=prediction,
                    defaults={
                        'accuracy_rating': rating,
                        'suggested_improvements': comment
                    }
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Cảm ơn bạn đã đóng góp ý kiến!'
            })
            
        except DiseasePrediction.DoesNotExist:
            return JsonResponse({
                'error': 'Prediction not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)