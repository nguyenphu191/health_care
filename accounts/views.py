from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorRegistrationForm, PatientRegistrationForm

def home(request):
    return render(request, 'home.html')

def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Đăng ký thành công! Tài khoản của bạn đang chờ xét duyệt.')
            return redirect('login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'registration/doctor_register.html', {'form': form})

def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'registration/patient_register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.user_type == 'doctor':
        return redirect('doctor_dashboard')
    elif request.user.user_type == 'patient':
        return redirect('patient_dashboard')
    else:
        return redirect('home')