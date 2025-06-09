from django.core.management.base import BaseCommand
from chatbot.models import Symptom, Disease, DiseaseSymptom

class Command(BaseCommand):
    help = 'Populate initial disease and symptom data'

    def handle(self, *args, **options):
        self.stdout.write('Populating disease and symptom data...')
        
        # Tạo symptoms - bao gồm cả những triệu chứng thiếu
        symptoms_data = [
            # General symptoms
            ('Sốt', 'Thân nhiệt trên 37.5°C', 'general', 2.0),
            ('Đau đầu', 'Cảm giác đau ở vùng đầu', 'neurological', 1.5),
            ('Mệt mỏi', 'Cảm giác kiệt sức, uể oải', 'general', 1.0),
            ('Chóng mặt', 'Cảm giác quay cuồng, mất thăng bằng', 'neurological', 1.5),
            ('Buồn nôn', 'Cảm giác muốn nôn', 'digestive', 1.2),
            ('Nôn', 'Việc nôn ra thức ăn hoặc dịch', 'digestive', 2.0),
            ('Mất ngủ', 'Khó ngủ hoặc ngủ không sâu giấc', 'neurological', 1.0),
            
            # Respiratory symptoms
            ('Ho', 'Ho khan hoặc ho có đờm', 'respiratory', 1.5),
            ('Ho có đờm', 'Ho kèm theo đờm', 'respiratory', 2.0),
            ('Khó thở', 'Cảm giác thiếu hơi thở', 'respiratory', 2.5),
            ('Đau ngực', 'Cảm giác đau ở vùng ngực', 'respiratory', 2.0),
            ('Nghẹt mũi', 'Mũi bị tắc, khó thở qua mũi', 'respiratory', 1.0),
            ('Sổ mũi', 'Chảy nước mũi', 'respiratory', 1.0),
            ('Đau họng', 'Cảm giác đau khi nuốt', 'respiratory', 1.5),
            ('Khó nuốt', 'Gặp khó khăn khi nuốt thức ăn', 'respiratory', 2.0),  # Thêm triệu chứng thiếu
            
            # Digestive symptoms
            ('Đau bụng', 'Cảm giác đau ở vùng bụng', 'digestive', 2.0),
            ('Tiêu chảy', 'Đi ngoài nhiều lần, phân lỏng', 'digestive', 2.0),
            ('Táo bón', 'Khó đi ngoài', 'digestive', 1.0),
            ('Đầy hơi', 'Cảm giác căng tức ở bụng', 'digestive', 1.0),
            ('Ợ hơi', 'Khí thoát ra từ dạ dày', 'digestive', 1.0),
            ('Đau dạ dày', 'Đau ở vùng thượng vị', 'digestive', 2.0),
            ('Mất ngon miệng', 'Không cảm thấy thèm ăn', 'digestive', 1.5),
            
            # Cardiovascular symptoms
            ('Đau tim', 'Cảm giác đau ở vùng tim', 'cardiovascular', 3.0),
            ('Nhịp tim nhanh', 'Tim đập nhanh hơn bình thường', 'cardiovascular', 2.0),
            ('Hồi hộp', 'Cảm giác tim đập mạnh', 'cardiovascular', 1.5),
            
            # Musculoskeletal symptoms
            ('Đau cơ', 'Cảm giác đau ở các cơ', 'musculoskeletal', 1.5),
            ('Đau khớp', 'Đau ở các khớp', 'musculoskeletal', 2.0),
            ('Cứng khớp', 'Khó cử động khớp', 'musculoskeletal', 2.0),
            ('Đau lưng', 'Đau ở vùng lưng', 'musculoskeletal', 1.5),
            ('Sưng khớp', 'Khớp bị sưng phù', 'musculoskeletal', 2.5),  # Thêm triệu chứng thiếu
            ('Hạn chế vận động', 'Khó khăn trong việc di chuyển', 'musculoskeletal', 2.0),  # Thêm triệu chứng thiếu
            
            # Dermatological symptoms
            ('Phát ban', 'Xuất hiện đốm đỏ trên da', 'dermatological', 1.5),
            ('Ngứa', 'Cảm giác ngứa trên da', 'dermatological', 1.0),
            ('Da vàng', 'Da có màu vàng', 'dermatological', 3.0),
            ('Da nhợt nhạt', 'Da mất màu hồng tự nhiên', 'dermatological', 1.5),  # Thêm triệu chứng thiếu
            
            # Mental symptoms
            ('Lo âu', 'Cảm giác bất an, lo lắng', 'mental', 1.5),
            ('Trầm cảm', 'Cảm giác buồn bã kéo dài', 'mental', 2.0),
            ('Căng thẳng', 'Cảm giác stress', 'mental', 1.0),
        ]
        
        # Tạo symptoms
        for name, desc, category, weight in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'category': category,
                    'severity_weight': weight
                }
            )
            if created:
                self.stdout.write(f'Created symptom: {name}')
        
        # Tạo diseases và liên kết với symptoms (đã sửa)
        diseases_data = [
            {
                'name': 'Cảm cúm',
                'description': 'Bệnh nhiễm virus gây viêm đường hô hấp trên',
                'category': 'infection',
                'severity': 'low',
                'treatment': 'Nghỉ ngơi, uống nhiều nước, thuốc hạ sốt nếu cần',
                'when_doctor': 'Nếu sốt cao > 39°C, khó thở, hoặc triệu chứng kéo dài > 7 ngày',
                'prevention': 'Rửa tay thường xuyên, tránh tiếp xúc người bệnh, tiêm vaccine',
                'symptoms': [
                    ('Sốt', 0.8), ('Đau đầu', 0.7), ('Ho', 0.9), ('Đau họng', 0.8),
                    ('Nghẹt mũi', 0.7), ('Sổ mũi', 0.8), ('Mệt mỏi', 0.9), ('Đau cơ', 0.6)
                ]
            },
            {
                'name': 'Viêm họng',
                'description': 'Viêm niêm mạc họng do virus hoặc vi khuẩn',
                'category': 'infection',
                'severity': 'low',
                'treatment': 'Súc miệng nước muối, uống nhiều nước ấm, thuốc giảm đau',
                'when_doctor': 'Nếu đau họng kèm sốt cao, khó nuốt, hoặc không cải thiện sau 3 ngày',
                'prevention': 'Giữ ấm họng, tránh hút thuốc, uống đủ nước',
                'symptoms': [
                    ('Đau họng', 0.95), ('Khó nuốt', 0.8), ('Sốt', 0.6),
                    ('Đau đầu', 0.5), ('Mệt mỏi', 0.7)
                ]
            },
            {
                'name': 'Viêm phế quản',
                'description': 'Viêm niêm mạc phế quản, thường do virus',
                'category': 'infection',
                'severity': 'medium',
                'treatment': 'Nghỉ ngơi, uống nhiều nước, thuốc long đờm',
                'when_doctor': 'Nếu ho có máu, khó thở, sốt cao, hoặc triệu chứng kéo dài',
                'prevention': 'Tránh hút thuốc, giữ ấm cơ thể, tăng cường miễn dịch',
                'symptoms': [
                    ('Ho có đờm', 0.9), ('Ho', 0.8), ('Khó thở', 0.7),
                    ('Đau ngực', 0.6), ('Sốt', 0.7), ('Mệt mỏi', 0.8)
                ]
            },
            {
                'name': 'Viêm dạ dày',
                'description': 'Viêm niêm mạc dạ dày do nhiều nguyên nhân',
                'category': 'chronic',
                'severity': 'medium',
                'treatment': 'Ăn nhẹ, tránh thức ăn cay nóng, thuốc kháng acid',
                'when_doctor': 'Nếu đau dạ dày dữ dội, nôn ra máu, hoặc giảm cân nhanh',
                'prevention': 'Ăn điều độ, tránh rượu bia, không lạm dụng thuốc giảm đau',
                'symptoms': [
                    ('Đau dạ dày', 0.9), ('Buồn nôn', 0.8), ('Nôn', 0.6),
                    ('Đầy hơi', 0.7), ('Mất ngon miệng', 0.7), ('Đau bụng', 0.8)
                ]
            },
            {
                'name': 'Ngộ độc thực phẩm',
                'description': 'Bệnh do ăn phải thực phẩm nhiễm khuẩn',
                'category': 'acute',
                'severity': 'medium',
                'treatment': 'Uống nhiều nước, nghỉ ngơi, ORS nếu tiêu chảy nhiều',
                'when_doctor': 'Nếu tiêu chảy kéo dài, sốt cao, có máu trong phân',
                'prevention': 'Ăn thức ăn chín, nước sạch, bảo quản thực phẩm đúng cách',
                'symptoms': [
                    ('Nôn', 0.9), ('Tiêu chảy', 0.9), ('Đau bụng', 0.8),
                    ('Sốt', 0.7), ('Buồn nôn', 0.9), ('Mệt mỏi', 0.8)
                ]
            },
            {
                'name': 'Cao huyết áp',
                'description': 'Huyết áp tăng cao kéo dài',
                'category': 'chronic',
                'severity': 'high',
                'treatment': 'Thuốc hạ áp theo chỉ định bác sĩ, chế độ ăn ít muối',
                'when_doctor': 'Cần theo dõi thường xuyên với bác sĩ tim mạch',
                'prevention': 'Ăn ít muối, tập thể dục, giảm cân, không hút thuốc',
                'symptoms': [
                    ('Đau đầu', 0.8), ('Chóng mặt', 0.7), ('Hồi hộp', 0.6),
                    ('Nhịp tim nhanh', 0.6), ('Mệt mỏi', 0.7)
                ]
            },
            {
                'name': 'Viêm khớp',
                'description': 'Viêm các khớp gây đau và cứng khớp',
                'category': 'chronic',
                'severity': 'medium',
                'treatment': 'Thuốc chống viêm, vật lý trị liệu, nghỉ ngơi',
                'when_doctor': 'Nếu đau khớp kéo dài, sưng khớp, hạn chế vận động',
                'prevention': 'Tập thể dục nhẹ nhàng, giữ cân nặng hợp lý',
                'symptoms': [
                    ('Đau khớp', 0.95), ('Cứng khớp', 0.9), ('Sưng khớp', 0.8),
                    ('Hạn chế vận động', 0.8), ('Đau cơ', 0.6)
                ]
            },
            {
                'name': 'Stress/Căng thẳng',
                'description': 'Trạng thái căng thẳng tâm lý kéo dài',
                'category': 'mental',
                'severity': 'medium',
                'treatment': 'Thư giãn, tập yoga, tâm lý trị liệu',
                'when_doctor': 'Nếu căng thẳng ảnh hưởng đến cuộc sống hàng ngày',
                'prevention': 'Quản lý thời gian, thư giãn, tập thể dục',
                'symptoms': [
                    ('Căng thẳng', 0.95), ('Lo âu', 0.8), ('Mất ngủ', 0.8),
                    ('Đau đầu', 0.7), ('Mệt mỏi', 0.8), ('Hồi hộp', 0.6)
                ]
            },
            {
                'name': 'Dị ứng',
                'description': 'Phản ứng dị ứng với chất kích thích',
                'category': 'autoimmune',
                'severity': 'low',
                'treatment': 'Tránh chất gây dị ứng, thuốc kháng histamine',
                'when_doctor': 'Nếu dị ứng nghiêm trọng, khó thở, sưng mặt',
                'prevention': 'Xác định và tránh chất gây dị ứng',
                'symptoms': [
                    ('Phát ban', 0.9), ('Ngứa', 0.95), ('Sổ mũi', 0.7),
                    ('Nghẹt mũi', 0.7), ('Ho', 0.6)
                ]
            },
            {
                'name': 'Thiếu máu',
                'description': 'Giảm số lượng hồng cầu hoặc hemoglobin',
                'category': 'chronic',
                'severity': 'medium',
                'treatment': 'Bổ sung sắt, vitamin B12, cải thiện dinh dưỡng',
                'when_doctor': 'Cần xét nghiệm máu để xác định nguyên nhân',
                'prevention': 'Ăn đủ chất sắt, vitamin B12, folate',
                'symptoms': [
                    ('Mệt mỏi', 0.9), ('Chóng mặt', 0.8), ('Khó thở', 0.7),
                    ('Da nhợt nhạt', 0.8), ('Hồi hộp', 0.6)
                ]
            }
        ]
        
        # Tạo diseases
        for disease_data in diseases_data:
            disease, created = Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults={
                    'description': disease_data['description'],
                    'category': disease_data['category'],
                    'severity_level': disease_data['severity'],
                    'treatment_advice': disease_data['treatment'],
                    'when_to_see_doctor': disease_data['when_doctor'],
                    'prevention_tips': disease_data['prevention']
                }
            )
            
            if created:
                self.stdout.write(f'Created disease: {disease_data["name"]}')
            
            # Liên kết với symptoms
            for symptom_name, probability in disease_data['symptoms']:
                try:
                    symptom = Symptom.objects.get(name=symptom_name)
                    disease_symptom, created = DiseaseSymptom.objects.get_or_create(
                        disease=disease,
                        symptom=symptom,
                        defaults={'probability': probability}
                    )
                    if created:
                        self.stdout.write(f'  - Linked {symptom_name} with probability {probability}')
                except Symptom.DoesNotExist:
                    self.stdout.write(f'  - Warning: Symptom "{symptom_name}" not found')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated disease and symptom data!')
        )