from django.core.management.base import BaseCommand
from doctors.models import Specialization

class Command(BaseCommand):
    help = 'Create initial specializations'

    def handle(self, *args, **options):
        specializations = [
            ('Nội khoa', 'Chuyên khoa nội tổng quát'),
            ('Ngoại khoa', 'Chuyên khoa phẫu thuật'),
            ('Tim mạch', 'Chuyên khoa tim mạch'),
            ('Thần kinh', 'Chuyên khoa thần kinh'),
            ('Nhi khoa', 'Chuyên khoa nhi'),
            ('Sản phụ khoa', 'Chuyên khoa sản phụ'),
            ('Mắt', 'Chuyên khoa mắt'),
            ('Tai mũi họng', 'Chuyên khoa tai mũi họng'),
            ('Da liễu', 'Chuyên khoa da liễu'),
            ('Tâm thần', 'Chuyên khoa tâm thần'),
        ]
        
        for name, description in specializations:
            Specialization.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created specializations')
        )