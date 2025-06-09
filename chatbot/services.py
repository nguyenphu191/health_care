import re
import json
import random
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from .models import ChatSession, ChatMessage, ChatbotKnowledge, ChatbotIntent
from doctors.models import Doctor, Specialization
from appointments.models import Appointment
from patients.models import Patient
from .ml_models import DiseasePredictor
from .models import Symptom
class ChatbotService:
    def __init__(self):
        self.greeting_keywords = ['xin chào', 'chào', 'hello', 'hi', 'hey', 'bạn ơi']
        self.appointment_keywords = ['đặt lịch', 'hẹn', 'khám', 'bác sĩ', 'appointment']
        self.symptoms_keywords = ['đau', 'triệu chứng', 'bệnh', 'không khỏe', 'mệt', 'sốt']
        self.emergency_keywords = ['cấp cứu', 'nguy hiểm', 'nghiêm trọng', 'khẩn cấp', 'emergency']
        self.prediction_keywords = ['dự đoán bệnh', 'chẩn đoán', 'bệnh gì', 'predict', 'diagnosis', 'kiểm tra bệnh']
        self.disease_predictor = DiseasePredictor()
    def get_or_create_session(self, user=None, session_key=None):
        """Lấy hoặc tạo phiên chat"""
        if user:
            session, created = ChatSession.objects.get_or_create(
                user=user,
                is_active=True,
                defaults={'created_at': timezone.now()}
            )
        else:
            session, created = ChatSession.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                defaults={'created_at': timezone.now()}
            )
        return session
    
    def process_message(self, session, message_content):
        """Xử lý tin nhắn từ người dùng"""
        # Lưu tin nhắn người dùng
        user_message = ChatMessage.objects.create(
            session=session,
            sender='user',
            content=message_content
        )
        
        # Phân tích ý định
        intent = self.detect_intent(message_content)
        
        # Tạo phản hồi dựa trên ý định
        response = self.generate_response(intent, message_content, session)
        
        # Lưu tin nhắn bot
        bot_message = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message_type=response.get('type', 'text'),
            content=response.get('content', ''),
            metadata=response.get('metadata', {})
        )
        
        return bot_message
    
    def detect_intent(self, message):
        """Phát hiện ý định từ tin nhắn"""
        message_lower = message.lower()
        
        # Kiểm tra lời chào
        if any(keyword in message_lower for keyword in self.greeting_keywords):
            return 'greeting'
        
        # Kiểm tra cấp cứu
        if any(keyword in message_lower for keyword in self.emergency_keywords):
            return 'emergency'
        
        # Kiểm tra đặt lịch hẹn
        if any(keyword in message_lower for keyword in self.appointment_keywords):
            return 'appointment_booking'
        
        # Kiểm tra triệu chứng
        if any(keyword in message_lower for keyword in self.symptoms_keywords):
            return 'symptom_inquiry'
        
        # Kiểm tra trong knowledge base
        knowledge = self.search_knowledge(message_lower)
        if knowledge:
            return 'knowledge_query'
        
        return 'general_inquiry'
    
    def generate_response(self, intent, message, session):
        """Tạo phản hồi dựa trên ý định"""
        if intent == 'greeting':
            return self.handle_greeting(session)
        elif intent == 'emergency':
            return self.handle_emergency()
        elif intent == 'appointment_booking':
            return self.handle_appointment_booking(session)
        elif intent == 'symptom_inquiry':
            return self.handle_symptom_inquiry(message)
        elif intent == 'knowledge_query':
            return self.handle_knowledge_query(message)
        else:
            return self.handle_general_inquiry(message)
    
    def handle_greeting(self, session):
        """Xử lý lời chào"""
        user = session.user
        if user:
            if user.user_type == 'patient':
                greeting = f"Xin chào {user.get_full_name()}! Tôi là trợ lý ảo của hệ thống chăm sóc sức khỏe."
            elif user.user_type == 'doctor':
                greeting = f"Xin chào Bác sĩ {user.get_full_name()}! Tôi có thể hỗ trợ gì cho bạn hôm nay?"
            else:
                greeting = f"Xin chào {user.get_full_name()}!"
        else:
            greeting = "Xin chào! Tôi là trợ lý ảo của hệ thống chăm sóc sức khỏe."
        
        return {
            'type': 'text',
            'content': greeting + "\n\nTôi có thể giúp bạn:\n• Đặt lịch hẹn với bác sĩ\n• Tư vấn triệu chứng sức khỏe\n• Trả lời các câu hỏi về y tế\n• Hướng dẫn sử dụng hệ thống",
            'metadata': {
                'quick_replies': [
                    'Đặt lịch hẹn',
                    'Tư vấn triệu chứng',
                    'Câu hỏi thường gặp',
                    'Liên hệ bác sĩ'
                ]
            }
        }
    
    def handle_emergency(self):
        """Xử lý tình huống cấp cứu"""
        return {
            'type': 'text',
            'content': "⚠️ TÌNH HUỐNG KHẨN CẤP ⚠️\n\nNếu bạn đang gặp tình huống y tế khẩn cấp, vui lòng:\n\n🚨 Gọi ngay 115 (Cấp cứu)\n🏥 Đến bệnh viện gần nhất\n📞 Liên hệ bác sĩ của bạn\n\nChatbot không thể thay thế việc cấp cứu y tế!",
            'metadata': {
                'emergency': True,
                'quick_replies': [
                    'Tìm bệnh viện gần nhất',
                    'Gọi cấp cứu 115',
                    'Liên hệ bác sĩ'
                ]
            }
        }
    
    def handle_appointment_booking(self, session):
        """Xử lý đặt lịch hẹn"""
        user = session.user
        
        if not user or user.user_type != 'patient':
            return {
                'type': 'text',
                'content': "Để đặt lịch hẹn, bạn cần đăng nhập với tài khoản bệnh nhân. Vui lòng đăng nhập hoặc đăng ký tài khoản mới.",
                'metadata': {
                    'quick_replies': ['Đăng nhập', 'Đăng ký']
                }
            }
        
        # Lấy danh sách chuyên khoa
        specializations = Specialization.objects.all()
        spec_list = "\n".join([f"• {spec.name}" for spec in specializations[:8]])
        
        return {
            'type': 'appointment_booking',
            'content': f"Tôi sẽ giúp bạn đặt lịch hẹn! 📅\n\nCác chuyên khoa có sẵn:\n{spec_list}\n\nBạn muốn đặt lịch với chuyên khoa nào?",
            'metadata': {
                'specializations': [spec.name for spec in specializations],
                'quick_replies': [spec.name for spec in specializations[:4]]
            }
        }
    
    def handle_symptom_inquiry(self, message):
        """Xử lý tư vấn triệu chứng"""
        # Phân tích triệu chứng cơ bản
        symptoms_advice = self.analyze_symptoms(message)
        
        return {
            'type': 'text',
            'content': symptoms_advice + "\n\n⚠️ Lưu ý: Đây chỉ là thông tin tham khảo. Để được chẩn đoán chính xác, bạn nên đặt lịch khám với bác sĩ chuyên khoa.",
            'metadata': {
                'quick_replies': [
                    'Đặt lịch hẹn',
                    'Tìm bác sĩ chuyên khoa',
                    'Câu hỏi khác'
                ]
            }
        }
    
    def analyze_symptoms(self, message):
        """Phân tích triệu chứng cơ bản"""
        message_lower = message.lower()
        
        if 'đau đầu' in message_lower or 'nhức đầu' in message_lower:
            return "Đau đầu có thể do nhiều nguyên nhân như căng thẳng, mệt mỏi, thiếu ngủ. Bạn nên:\n• Nghỉ ngơi đầy đủ\n• Uống đủ nước\n• Massage nhẹ vùng thái dương\n• Tránh ánh sáng mạnh"
        
        elif 'sốt' in message_lower:
            return "Sốt là dấu hiệu cơ thể đang chống lại nhiễm trùng. Bạn nên:\n• Nghỉ ngơi tuyệt đối\n• Uống nhiều nước\n• Hạ sốt bằng thuốc (theo chỉ dẫn)\n• Theo dõi nhiệt độ thường xuyên"
        
        elif 'ho' in message_lower:
            return "Ho có thể do cảm lạnh, viêm họng hoặc dị ứng. Bạn nên:\n• Uống nước ấm\n• Súc miệng nước muối\n• Tránh khói bụi\n• Sử dụng máy tạo ẩm"
        
        elif 'đau bụng' in message_lower:
            return "Đau bụng có nhiều nguyên nhân khác nhau. Bạn nên:\n• Ăn nhẹ, tránh thức ăn cứng\n• Uống nước ấm\n• Nghỉ ngơi\n• Theo dõi triệu chứng"
        
        else:
            return "Tôi hiểu bạn đang có một số triệu chứng sức khỏe. Để được tư vấn chính xác nhất, tôi khuyên bạn nên mô tả chi tiết triệu chứng và đặt lịch khám với bác sĩ chuyên khoa."
    
    def handle_knowledge_query(self, message):
        """Xử lý câu hỏi từ knowledge base"""
        knowledge = self.search_knowledge(message.lower())
        
        if knowledge:
            response = knowledge.answer
            if knowledge.follow_up_questions:
                response += "\n\nCâu hỏi liên quan:\n" + "\n".join([f"• {q}" for q in knowledge.follow_up_questions])
            
            return {
                'type': 'text',
                'content': response,
                'metadata': {
                    'knowledge_category': knowledge.category,
                    'quick_replies': knowledge.follow_up_questions[:3] if knowledge.follow_up_questions else []
                }
            }
        
        return self.handle_general_inquiry(message)
    
    def search_knowledge(self, query):
        """Tìm kiếm trong knowledge base"""
        # Tìm kiếm theo từ khóa
        knowledge_items = ChatbotKnowledge.objects.filter(
            is_active=True
        ).order_by('-priority')
        
        for item in knowledge_items:
            keywords = [kw.strip().lower() for kw in item.question_keywords.split(',')]
            if any(keyword in query for keyword in keywords):
                return item
        
        return None
    
    def handle_general_inquiry(self, message):
        """Xử lý câu hỏi chung"""
        responses = [
            "Tôi hiểu bạn có thắc mắc. Tuy nhiên, tôi chưa có thông tin cụ thể về vấn đề này.",
            "Câu hỏi của bạn khá thú vị! Bạn có thể hỏi chi tiết hơn hoặc liên hệ trực tiếp với bác sĩ.",
            "Tôi đang học hỏi thêm để trả lời tốt hơn. Hiện tại, tôi khuyên bạn nên tham khảo ý kiến bác sĩ chuyên khoa."
        ]
        
        return {
            'type': 'text',
            'content': random.choice(responses),
            'metadata': {
                'quick_replies': [
                    'Đặt lịch hẹn',
                    'Tư vấn triệu chứng',
                    'Câu hỏi khác',
                    'Liên hệ hỗ trợ'
                ]
            }
        }
    
    def get_available_doctors(self, specialty=None):
        """Lấy danh sách bác sĩ có sẵn"""
        doctors = Doctor.objects.filter(is_verified=True)
        
        if specialty:
            try:
                spec = Specialization.objects.get(name__icontains=specialty)
                doctors = doctors.filter(specializations=spec)
            except Specialization.DoesNotExist:
                pass
        
        return doctors[:5]  
    
    def detect_intent(self, message):
        """Phát hiện ý định từ tin nhắn"""
        message_lower = message.lower()
        
        # Kiểm tra lời chào
        if any(keyword in message_lower for keyword in self.greeting_keywords):
            return 'greeting'
        
        # Kiểm tra cấp cứu
        if any(keyword in message_lower for keyword in self.emergency_keywords):
            return 'emergency'
        
        # Kiểm tra dự đoán bệnh
        if any(keyword in message_lower for keyword in self.prediction_keywords):
            return 'disease_prediction'
        
        # Kiểm tra đặt lịch hẹn
        if any(keyword in message_lower for keyword in self.appointment_keywords):
            return 'appointment_booking'
        
        # Kiểm tra triệu chứng
        if any(keyword in message_lower for keyword in self.symptoms_keywords):
            return 'symptom_inquiry'
        
        # Kiểm tra trong knowledge base
        knowledge = self.search_knowledge(message_lower)
        if knowledge:
            return 'knowledge_query'
        
        return 'general_inquiry'
    
    def generate_response(self, intent, message, session):
        """Tạo phản hồi dựa trên ý định"""
        if intent == 'greeting':
            return self.handle_greeting(session)
        elif intent == 'emergency':
            return self.handle_emergency()
        elif intent == 'disease_prediction':
            return self.handle_disease_prediction_request(session)
        elif intent == 'appointment_booking':
            return self.handle_appointment_booking(session)
        elif intent == 'symptom_inquiry':
            return self.handle_symptom_inquiry(message)
        elif intent == 'knowledge_query':
            return self.handle_knowledge_query(message)
        else:
            return self.handle_general_inquiry(message)
    
    def handle_disease_prediction_request(self, session):
        """Xử lý yêu cầu dự đoán bệnh"""
        user = session.user
        
        if not user:
            return {
                'type': 'text',
                'content': "Để sử dụng tính năng dự đoán bệnh, bạn cần đăng nhập. Vui lòng đăng nhập để tiếp tục.",
                'metadata': {
                    'quick_replies': ['Đăng nhập', 'Đăng ký']
                }
            }
        
        # Lấy danh sách triệu chứng theo danh mục
        symptoms_by_category = self.disease_predictor.get_available_symptoms()
        
        return {
            'type': 'disease_prediction',
            'content': "🔍 **Dự đoán bệnh thông minh**\n\nTôi sẽ giúp bạn dự đoán các bệnh có thể dựa trên triệu chứng. Vui lòng chọn các triệu chứng bạn đang gặp phải:\n\n⚠️ **Lưu ý:** Đây chỉ là công cụ hỗ trợ, không thay thế chẩn đoán của bác sĩ.",
            'metadata': {
                'symptoms_by_category': symptoms_by_category,
                'action': 'show_symptom_selector',
                'quick_replies': [
                    'Tôi đang bị sốt',
                    'Tôi bị đau đầu',
                    'Tôi ho nhiều',
                    'Chọn triệu chứng khác'
                ]
            }
        }
    
    def handle_symptom_selection(self, session, selected_symptoms):
        """Xử lý khi người dùng đã chọn triệu chứng"""
        if not selected_symptoms:
            return {
                'type': 'text',
                'content': "Bạn chưa chọn triệu chứng nào. Vui lòng chọn ít nhất một triệu chứng để tôi có thể dự đoán.",
                'metadata': {
                    'quick_replies': ['Chọn lại triệu chứng', 'Hủy bỏ']
                }
            }
        
        # Gọi disease predictor
        prediction_result = self.disease_predictor.predict_from_symptoms(session, selected_symptoms)
        
        if not prediction_result['success']:
            return {
                'type': 'text',
                'content': prediction_result['message'],
                'metadata': {
                    'quick_replies': ['Thử lại', 'Đặt lịch hẹn']
                }
            }
        
        # Format kết quả dự đoán
        predictions = prediction_result['predictions']
        confidence = prediction_result['confidence_score']
        
        response_content = prediction_result['message']
        
        # Thêm thông tin chi tiết cho top prediction
        if predictions:
            top_disease = predictions[0]['disease']
            disease_info = self.disease_predictor.ml_model.get_disease_info(top_disease)
            
            if disease_info:
                response_content += f"\n\n📋 **Thông tin chi tiết về {top_disease}:**\n"
                response_content += f"🔹 **Điều trị:** {disease_info['treatment_advice']}\n"
                response_content += f"🔹 **Khi cần gặp bác sĩ:** {disease_info['when_to_see_doctor']}\n"
                
                if disease_info['prevention_tips']:
                    response_content += f"🔹 **Phòng ngừa:** {disease_info['prevention_tips']}\n"
        
        # Tạo quick replies
        quick_replies = ['Đặt lịch hẹn', 'Dự đoán lại', 'Hỏi bác sĩ']
        
        if confidence < 0.5:
            quick_replies.insert(0, 'Cần tư vấn thêm')
        
        return {
            'type': 'disease_prediction_result',
            'content': response_content,
            'metadata': {
                'prediction_id': prediction_result['prediction_id'],
                'predictions': predictions,
                'confidence_score': confidence,
                'quick_replies': quick_replies,
                'show_feedback': True
            }
        }
    
    def handle_quick_symptom(self, symptom_description, session):
        """Xử lý khi người dùng mô tả triệu chứng nhanh"""
        # Phân tích description để tìm triệu chứng phù hợp
        symptom_keywords = {
            'sốt': ['sốt', 'nóng sốt', 'bị sốt', 'thân nhiệt cao'],
            'đau đầu': ['đau đầu', 'nhức đầu', 'head ache'],
            'ho': ['ho', 'cough', 'ho khan', 'ho có đờm'],
            'đau bụng': ['đau bụng', 'stomach ache', 'bụng đau'],
            'buồn nôn': ['buồn nôn', 'nausea', 'muốn nôn'],
            'mệt mỏi': ['mệt', 'mệt mỏi', 'tired', 'uể oải'],
            'chóng mặt': ['chóng mặt', 'dizzy', 'hoa mắt'],
        }
        
        detected_symptoms = []
        description_lower = symptom_description.lower()
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_symptoms.append(symptom)
        
        if detected_symptoms:
            # Dự đoán với triệu chứng đã phát hiện
            return self.handle_symptom_selection(session, detected_symptoms)
        else:
            return {
                'type': 'text',
                'content': f"Tôi hiểu bạn có triệu chứng: \"{symptom_description}\"\n\nĐể dự đoán chính xác hơn, bạn có thể chọn triệu chứng cụ thể từ danh sách có sẵn.",
                'metadata': {
                    'quick_replies': [
                        'Chọn triệu chứng từ danh sách',
                        'Mô tả chi tiết hơn',
                        'Đặt lịch hẹn'
                    ]
                }
            }
    
    def handle_prediction_feedback(self, prediction_id, feedback_type, comment=""):
        """Xử lý feedback cho dự đoán"""
        try:
            from .models import DiseasePrediction
            prediction = DiseasePrediction.objects.get(id=prediction_id)
            prediction.user_feedback = feedback_type
            prediction.save()
            
            # Có thể lưu thêm feedback chi tiết nếu cần
            if comment:
                from .models import PredictionFeedback
                PredictionFeedback.objects.create(
                    prediction=prediction,
                    accuracy_rating=3,  # Default rating
                    suggested_improvements=comment
                )
            
            return True
        except:
            return False
    
    # Cập nhật method handle_greeting để bao gồm disease prediction
    def handle_greeting(self, session):
        """Xử lý lời chào"""
        user = session.user
        if user:
            if user.user_type == 'patient':
                greeting = f"Xin chào {user.get_full_name()}! Tôi là trợ lý ảo của hệ thống chăm sóc sức khỏe."
            elif user.user_type == 'doctor':
                greeting = f"Xin chào Bác sĩ {user.get_full_name()}! Tôi có thể hỗ trợ gì cho bạn hôm nay?"
            else:
                greeting = f"Xin chào {user.get_full_name()}!"
        else:
            greeting = "Xin chào! Tôi là trợ lý ảo của hệ thống chăm sóc sức khỏe."
        
        return {
            'type': 'text',
            'content': greeting + "\n\nTôi có thể giúp bạn:\n• 🗓️ Đặt lịch hẹn với bác sĩ\n• 🔍 Dự đoán bệnh từ triệu chứng\n• 🩺 Tư vấn triệu chứng sức khỏe\n• ❓ Trả lời các câu hỏi về y tế\n• 📖 Hướng dẫn sử dụng hệ thống",
            'metadata': {
                'quick_replies': [
                    'Đặt lịch hẹn',
                    'Dự đoán bệnh',
                    'Tư vấn triệu chứng',
                    'Câu hỏi thường gặp'
                ]
            }
        }