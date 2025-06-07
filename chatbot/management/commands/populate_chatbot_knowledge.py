from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledge, ChatbotIntent

class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Populating chatbot knowledge base...')
        
        # FAQ Knowledge
        faq_data = [
            {
                'category': 'faq',
                'question_keywords': 'làm thế nào để đặt lịch hẹn, đặt lịch, book appointment',
                'answer': 'Để đặt lịch hẹn, bạn có thể:\n1. Đăng nhập vào tài khoản bệnh nhân\n2. Chọn "Đặt lịch hẹn" từ menu\n3. Chọn bác sĩ và thời gian phù hợp\n4. Mô tả triệu chứng và xác nhận\n\nHoặc bạn có thể nói với tôi "Đặt lịch hẹn" để được hỗ trợ.',
                'follow_up_questions': ['Tìm bác sĩ chuyên khoa', 'Phí khám bệnh', 'Hủy lịch hẹn'],
                'priority': 10
            },
            {
                'category': 'faq',
                'question_keywords': 'phí khám, chi phí, giá cả, bao nhiều tiền',
                'answer': 'Phí khám bệnh phụ thuộc vào:\n• Bác sĩ và chuyên khoa\n• Loại dịch vụ khám\n• Thời gian khám\n\nBạn có thể xem phí tư vấn của từng bác sĩ khi đặt lịch hẹn. Phí khám thường từ 200.000 - 500.000 VNĐ.',
                'follow_up_questions': ['Thanh toán như thế nào', 'Bảo hiểm y tế', 'Khám miễn phí'],
                'priority': 8
            },
            {
                'category': 'faq',
                'question_keywords': 'giờ làm việc, thời gian, mở cửa',
                'answer': 'Hệ thống hoạt động 24/7, nhưng lịch khám của bác sĩ có thể khác nhau:\n• Sáng: 8:00 - 12:00\n• Chiều: 14:00 - 18:00\n• Tối: 19:00 - 21:00\n\nBạn có thể xem lịch cụ thể của từng bác sĩ khi đặt hẹn.',
                'follow_up_questions': ['Khám cuối tuần', 'Khám ban đêm', 'Lịch bác sĩ'],
                'priority': 7
            }
        ]
        
        # Medical Knowledge
        medical_data = [
            {
                'category': 'medical',
                'question_keywords': 'đau đầu, nhức đầu, migraine, đau nửa đầu',
                'answer': 'Đau đầu có thể do nhiều nguyên nhân:\n• Căng thẳng, stress\n• Thiếu ngủ, mệt mỏi\n• Sinus, cảm cúm\n• Migraine\n\nCách giảm đau tạm thời:\n• Nghỉ ngơi trong phòng tối\n• Massage nhẹ thái dương\n• Uống đủ nước\n• Thuốc giảm đau (theo chỉ dẫn)\n\nNếu đau đầu thường xuyên hoặc dữ dội, hãy đặt lịch khám.',
                'follow_up_questions': ['Khi nào cần đi khám', 'Thuốc giảm đau đầu', 'Bác sĩ thần kinh'],
                'priority': 9
            },
            {
                'category': 'medical',
                'question_keywords': 'sốt, nóng sốt, có sốt',
                'answer': 'Sốt là phản ứng tự nhiên của cơ thể chống lại nhiễm trùng.\n\nCách xử lý sốt:\n• Nghỉ ngơi tuyệt đối\n• Uống nhiều nước\n• Lau mình bằng nước ấm\n• Thuốc hạ sốt (paracetamol)\n• Theo dõi nhiệt độ\n\n⚠️ Đi khám ngay nếu:\n• Sốt trên 39°C\n• Sốt kéo dài > 3 ngày\n• Có kèm co giật, khó thở',
                'follow_up_questions': ['Thuốc hạ sốt', 'Khi nào cần cấp cứu', 'Sốt ở trẻ em'],
                'priority': 10
            },
            {
                'category': 'medical',
                'question_keywords': 'ho, ho khan, ho có đờm',
                'answer': 'Ho có thể do:\n• Cảm lạnh, cúm\n• Viêm họng\n• Dị ứng\n• Khói bụi\n\nCách giảm ho:\n• Uống nước ấm, mật ong\n• Súc miệng nước muối\n• Tránh khói thuốc, bụi\n• Máy tạo ẩm\n• Ngậm kẹo ho\n\nĐi khám nếu ho kéo dài > 2 tuần hoặc có máu.',
                'follow_up_questions': ['Thuốc ho', 'Ho có máu', 'Bác sĩ tai mũi họng'],
                'priority': 8
            }
        ]
        
        # System Knowledge
        system_data = [
            {
                'category': 'system',
                'question_keywords': 'đăng ký tài khoản, tạo tài khoản, sign up',
                'answer': 'Để đăng ký tài khoản:\n\nBệnh nhân:\n1. Nhấn "Đăng ký BN" trên trang chủ\n2. Điền thông tin cá nhân\n3. Xác nhận email\n4. Đăng nhập và cập nhật hồ sơ\n\nBác sĩ:\n1. Nhấn "Đăng ký BS" trên trang chủ\n2. Điền thông tin và chuyên môn\n3. Chờ admin xét duyệt\n4. Nhận thông báo kích hoạt',
                'follow_up_questions': ['Quên mật khẩu', 'Đăng nhập', 'Cập nhật thông tin'],
                'priority': 6
            },
            {
                'category': 'system',
                'question_keywords': 'quên mật khẩu, reset password, đổi mật khẩu',
                'answer': 'Nếu quên mật khẩu:\n1. Nhấn "Quên mật khẩu" tại trang đăng nhập\n2. Nhập email đã đăng ký\n3. Kiểm tra email reset\n4. Tạo mật khẩu mới\n\nNếu không nhận được email, liên hệ hỗ trợ.',
                'follow_up_questions': ['Đăng nhập', 'Liên hệ hỗ trợ', 'Bảo mật tài khoản'],
                'priority': 7
            }
        ]
        
        # Emergency Knowledge
        emergency_data = [
            {
                'category': 'emergency',
                'question_keywords': 'cấp cứu, khẩn cấp, emergency, nguy hiểm',
                'answer': '🚨 TÌNH HUỐNG KHẨN CẤP\n\nGọi ngay:\n• 115 - Cấp cứu y tế\n• 114 - Cứu hỏa\n• 113 - Công an\n\nBệnh viện gần:\n• BV Bạch Mai: 024 3869 3731\n• BV Việt Đức: 024 3825 3531\n• BV 103: 024 3972 5134\n• BV Đại học Y: 024 3852 3798\n\n⚠️ Chatbot không thể thay thế cấp cứu y tế!',
                'follow_up_questions': ['Bệnh viện gần nhất', 'Triệu chứng nguy hiểm', 'Sơ cứu cơ bản'],
                'priority': 10
            }
        ]
        
        # Combine all data
        all_data = faq_data + medical_data + system_data + emergency_data
        
        # Create knowledge entries
        for data in all_data:
            knowledge, created = ChatbotKnowledge.objects.get_or_create(
                question_keywords=data['question_keywords'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created: {knowledge.question_keywords[:50]}...')
            else:
                self.stdout.write(f'Exists: {knowledge.question_keywords[:50]}...')
        
        # Create intents
        intents_data = [
            {
                'name': 'greeting',
                'description': 'Lời chào, khởi đầu cuộc hội thoại',
                'training_phrases': ['xin chào', 'chào bạn', 'hello', 'hi', 'hey'],
                'action': 'handle_greeting',
                'response_templates': ['Xin chào! Tôi có thể giúp gì cho bạn?']
            },
            {
                'name': 'appointment_booking',
                'description': 'Đặt lịch hẹn với bác sĩ',
                'training_phrases': ['đặt lịch', 'book appointment', 'hẹn bác sĩ', 'khám bệnh'],
                'action': 'handle_appointment',
                'response_templates': ['Tôi sẽ giúp bạn đặt lịch hẹn với bác sĩ.']
            },
            {
                'name': 'symptom_inquiry',
                'description': 'Hỏi về triệu chứng sức khỏe',
                'training_phrases': ['tôi bị đau', 'triệu chứng', 'không khỏe', 'bệnh'],
                'action': 'handle_symptoms',
                'response_templates': ['Hãy mô tả triệu chứng của bạn để tôi có thể tư vấn.']
            },
            {
                'name': 'emergency',
                'description': 'Tình huống cấp cứu',
                'training_phrases': ['cấp cứu', 'khẩn cấp', 'nguy hiểm', 'emergency'],
                'action': 'handle_emergency',
                'response_templates': ['Đây là tình huống khẩn cấp. Hãy gọi 115 ngay!']
            }
        ]
        
        for intent_data in intents_data:
            intent, created = ChatbotIntent.objects.get_or_create(
                name=intent_data['name'],
                defaults=intent_data
            )
            if created:
                self.stdout.write(f'Created intent: {intent.name}')
            else:
                self.stdout.write(f'Intent exists: {intent.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated chatbot knowledge base!')
        )