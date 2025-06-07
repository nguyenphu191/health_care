from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from appointments.models import Appointment
from appointments.forms import AppointmentForm
from qa_system.models import Question
from qa_system.forms import QuestionForm

@login_required
def patient_dashboard(request):
    if request.user.user_type != 'patient':
        return redirect('home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    # Sửa lỗi: Phải lấy toàn bộ appointments trước, sau đó filter và slice riêng biệt
    all_appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')
    appointments = all_appointments[:5]  # Lấy 5 appointments gần nhất để hiển thị
    upcoming_appointments = all_appointments.filter(status__in=['pending', 'confirmed']).count()  # Đếm upcoming từ toàn bộ appointments
    
    questions = Question.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
        'questions': questions,
    }
    return render(request, 'patients/dashboard.html', context)

@login_required
def patient_appointments(request):
    if request.user.user_type != 'patient':
        return redirect('home')
    
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'patients/appointments.html', {
        'appointments': appointments
    })

@login_required
def book_appointment(request):
    if request.user.user_type != 'patient':
        return redirect('home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, 'Đặt lịch hẹn thành công!')
            return redirect('patient_appointments')
    else:
        form = AppointmentForm()
    
    return render(request, 'patients/book_appointment.html', {'form': form})