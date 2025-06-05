from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    license_number = models.CharField(max_length=50, unique=True)
    specializations = models.ManyToManyField(Specialization)
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class DoctorSchedule(models.Model):
    WEEKDAYS = [
        (0, 'Thứ 2'),
        (1, 'Thứ 3'),
        (2, 'Thứ 4'),
        (3, 'Thứ 5'),
        (4, 'Thứ 6'),
        (5, 'Thứ 7'),
        (6, 'Chủ nhật'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'weekday', 'start_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} ({self.start_time}-{self.end_time})"