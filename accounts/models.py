from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('doctor', 'Bác sĩ'),
        ('patient', 'Bệnh nhân'),
        ('admin', 'Quản trị viên'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Thêm trường để theo dõi trạng thái tài khoản
    is_profile_complete = models.BooleanField(default=False)
    created_by_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_full_display_name(self):
        """Trả về tên đầy đủ hoặc username nếu không có tên"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def get_avatar_url(self):
        """Trả về URL avatar hoặc avatar mặc định"""
        if self.avatar:
            return self.avatar.url
        else:
            # Trả về avatar mặc định dựa trên user_type
            if self.user_type == 'doctor':
                return '/static/images/default_doctor_avatar.png'
            else:
                return '/static/images/default_patient_avatar.png'