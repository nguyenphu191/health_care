from django.contrib import admin
from .models import Specialization, Doctor, DoctorSchedule

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'experience_years', 'is_verified')
    list_filter = ('is_verified', 'specializations')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'weekday', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available')