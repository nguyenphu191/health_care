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
            
            if not message_content:
                return JsonResponse({'error': 'Message content is required'}, status=400)
            
            # Khởi tạo service
            chatbot_service = ChatbotService()
            
            # Lấy hoặc tạo session
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            if not session_key and not user:
                request.session.create()
                session_key = request.session.session_key
            
            session = chatbot_service.get_or_create_session(user=user, session_key=session_key)
            
            # Xử lý tin nhắn
            bot_response = chatbot_service.process_message(session, message_content)
            
            # Trả về response
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