from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Doctor, DoctorSchedule
from appointments.models import Appointment
from qa_system.models import Question, Answer
from qa_system.forms import AnswerForm

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-created_at')[:5]
    pending_appointments = appointments.filter(status='pending').count()
    questions = Question.objects.all().order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'pending_appointments': pending_appointments,
        'questions': questions,
    }
    return render(request, 'doctors/dashboard.html', context)

@login_required
def doctor_appointments(request):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-created_at')
    
    return render(request, 'doctors/appointments.html', {
        'appointments': appointments
    })

@login_required
def update_appointment_status(request, appointment_id):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        diagnosis = request.POST.get('diagnosis', '')
        prescription = request.POST.get('prescription', '')
        
        appointment.status = status
        appointment.diagnosis = diagnosis
        appointment.prescription = prescription
        appointment.save()
        
        messages.success(request, 'Cập nhật lịch hẹn thành công!')
    
    return redirect('doctor_appointments')

@login_required
def doctor_schedule(request):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    schedules = DoctorSchedule.objects.filter(doctor=doctor).order_by('weekday', 'start_time')
    
    if request.method == 'POST':
        weekday = request.POST.get('weekday')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # Kiểm tra trùng lặp
        existing_schedule = DoctorSchedule.objects.filter(
            doctor=doctor,
            weekday=int(weekday),
            start_time=start_time
        ).first()
        
        if existing_schedule:
            messages.error(request, 'Lịch làm việc này đã tồn tại!')
        else:
            DoctorSchedule.objects.create(
                doctor=doctor,
                weekday=int(weekday),
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Thêm lịch làm việc thành công!')
        return redirect('doctor_schedule')
    
    return render(request, 'doctors/schedule.html', {
        'schedules': schedules,
        'weekdays': DoctorSchedule.WEEKDAYS
    })

@login_required
def update_schedule(request, schedule_id):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id, doctor__user=request.user)
    
    if request.method == 'POST':
        weekday = request.POST.get('weekday')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_available = request.POST.get('is_available') == 'on'
        
        schedule.weekday = int(weekday)
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.is_available = is_available
        schedule.save()
        
        messages.success(request, 'Cập nhật lịch làm việc thành công!')
    
    return redirect('doctor_schedule')

@login_required
def delete_schedule(request, schedule_id):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id, doctor__user=request.user)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Xóa lịch làm việc thành công!')
    
    return redirect('doctor_schedule')

@login_required
def answer_question(request, question_id):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.doctor = doctor
            answer.question = question
            answer.save()
            messages.success(request, 'Trả lời câu hỏi thành công!')
            return redirect('question_detail', question_id=question.id)
    else:
        form = AnswerForm()
    
    return render(request, 'doctors/answer_question.html', {
        'form': form,
        'question': question
    })