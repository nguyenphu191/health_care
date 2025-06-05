from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import DoctorRegistrationForm, PatientRegistrationForm, DoctorProfileForm, PatientProfileForm
from doctors.models import Doctor
from patients.models import Patient

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

# Admin functions
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_doctors = Doctor.objects.count()
    pending_doctors = Doctor.objects.filter(is_verified=False).count()
    verified_doctors = Doctor.objects.filter(is_verified=True).count()
    total_patients = Patient.objects.count()
    
    context = {
        'total_doctors': total_doctors,
        'pending_doctors': pending_doctors,
        'verified_doctors': verified_doctors,
        'total_patients': total_patients,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@user_passes_test(is_admin)
def manage_doctors(request):
    doctors_list = Doctor.objects.all().order_by('-user__date_joined')
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status == 'pending':
        doctors_list = doctors_list.filter(is_verified=False)
    elif status == 'verified':
        doctors_list = doctors_list.filter(is_verified=True)
    
    # Pagination
    paginator = Paginator(doctors_list, 10)
    page = request.GET.get('page')
    doctors = paginator.get_page(page)
    
    context = {
        'doctors': doctors,
        'current_status': status,
    }
    return render(request, 'admin_panel/manage_doctors.html', context)

@user_passes_test(is_admin)
def toggle_doctor_verification(request, doctor_id):
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, user_id=doctor_id)
        doctor.is_verified = not doctor.is_verified
        doctor.save()
        
        status = "kích hoạt" if doctor.is_verified else "hủy kích hoạt"
        messages.success(request, f'Đã {status} tài khoản bác sĩ {doctor.user.get_full_name()} thành công!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_verified': doctor.is_verified,
                'message': f'Đã {status} tài khoản thành công!'
            })
    
    return redirect('manage_doctors')

@user_passes_test(is_admin)
def doctor_detail_admin(request, doctor_id):
    doctor = get_object_or_404(Doctor, user_id=doctor_id)
    appointments = doctor.appointments.all()[:10]
    answers = doctor.answers.all()[:10]
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'answers': answers,
    }
    return render(request, 'admin_panel/doctor_detail.html', context)

# Admin functions for creating accounts
@user_passes_test(is_admin)
def admin_create_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.created_by_admin = True
            user.save()
            
            # Admin tạo thì tự động verify
            doctor = Doctor.objects.get(user=user)
            doctor.is_verified = True
            doctor.save()
            
            messages.success(request, f'Đã tạo tài khoản bác sĩ {user.get_full_name()} thành công!')
            return redirect('manage_doctors')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'admin_panel/create_doctor.html', {'form': form})

@user_passes_test(is_admin)
def admin_create_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.created_by_admin = True
            user.save()
            
            messages.success(request, f'Đã tạo tài khoản bệnh nhân {user.get_full_name()} thành công!')
            return redirect('admin_dashboard')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'admin_panel/create_patient.html', {'form': form})

@user_passes_test(is_admin)
def manage_patients(request):
    patients_list = Patient.objects.all().order_by('-user__date_joined')
    
    # Pagination
    paginator = Paginator(patients_list, 10)
    page = request.GET.get('page')
    patients = paginator.get_page(page)
    
    context = {
        'patients': patients,
    }
    return render(request, 'admin_panel/manage_patients.html', context)

@user_passes_test(is_admin)
def patient_detail_admin(request, patient_id):
    patient = get_object_or_404(Patient, user_id=patient_id)
    appointments = patient.appointments.all()[:10]
    questions = patient.questions.all()[:10]
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'questions': questions,
    }
    return render(request, 'admin_panel/patient_detail.html', context)
@login_required
def edit_profile(request):
    if request.user.user_type == 'doctor':
        return redirect('edit_doctor_profile')
    elif request.user.user_type == 'patient':
        return redirect('edit_patient_profile')
    else:
        return redirect('home')

@login_required
def edit_doctor_profile(request):
    if request.user.user_type != 'doctor':
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=request.user, doctor_instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=request.user, doctor_instance=doctor)
    
    return render(request, 'accounts/edit_doctor_profile.html', {'form': form, 'doctor': doctor})

@login_required
def edit_patient_profile(request):
    if request.user.user_type != 'patient':
        return redirect('home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=request.user, patient_instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=request.user, patient_instance=patient)
    
    return render(request, 'accounts/edit_patient_profile.html', {'form': form, 'patient': patient})