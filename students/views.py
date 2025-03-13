# students/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import StudentRegistration
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import random
import string

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.utils import timezone

# Helper function to generate a random password
def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def register_for_job_fair(request, job_fair_id):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if student is already registered
            registration_number = form.cleaned_data['registration_number']
            existing_registration = StudentRegistration.objects.filter(
                job_fair_id=job_fair_id,
                registration_number=registration_number
            ).first()
            
            if existing_registration:
                # If already registered, add error message to the form
                form.add_error('registration_number', 'This registration number has already been registered for this job fair.')
                # Return the form with the error message
                return render(request, 'students_app/registration_form.html', {
                    'form': form,
                    'job_fair_id': job_fair_id
                })
            
            try:
                # Create but don't save the form instance yet
                student_registration = form.save(commit=False)
                # Add the job_fair_id
                student_registration.job_fair_id = job_fair_id
                
                # Check if this registration_number exists in any other job fair
                existing_student = StudentRegistration.objects.filter(
                    registration_number=registration_number
                ).first()
                
                if existing_student:
                    # If student exists in another job fair, use the same password
                    student_registration.password = existing_student.password
                    student_registration.is_first_login = False
                else:
                    # Generate a password for new student
                    student_registration.password = generate_password()
                
                # Now save the instance
                student_registration.save()
                
                # Store student registration number in session
                request.session['student_registration_number'] = student_registration.registration_number
                request.session['student_password'] = student_registration.password
                request.session['is_new_registration'] = not existing_student
                
                messages.success(request, 'Registration successful! You can now login with your registration number and password.')
                return redirect('student_registration_success')
            except IntegrityError:
                # This is a fallback in case of race conditions
                form.add_error('registration_number', 'This registration number has already been registered for this job fair.')
                return render(request, 'students_app/registration_form.html', {
                    'form': form,
                    'job_fair_id': job_fair_id
                })
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students_app/registration_form.html', {
        'form': form,
        'job_fair_id': job_fair_id
    })

def registration_success(request):
    registration_number = request.session.get('student_registration_number')
    password = request.session.get('student_password')
    is_new_registration = request.session.get('is_new_registration', False)
    
    return render(request, 'students_app/registration_success.html', {
        'registration_number': registration_number,
        'password': password,
        'is_new_registration': is_new_registration
    })

def student_login(request):
    if 'student_id' in request.session:
        # If student is already logged in, redirect to dashboard
        return redirect('student_dashboard')
        
    if request.method == "POST":
        registration_number = request.POST.get('registration_number')
        password = request.POST.get('password')
        
        try:
            student = StudentRegistration.objects.filter(
                registration_number=registration_number,
                password=password
            ).first()
            
            if student:
                # Store student info in session
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                request.session['student_registration_number'] = student.registration_number
                return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid registration number or password")
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
    
    # Pre-populate fields if coming from registration
    registration_number = request.session.get('student_registration_number', '')
    password = request.session.get('student_password', '')
    
    return render(request, 'students_app/login.html', {
        'registration_number': registration_number,
        'password': password
    })

def student_dashboard(request):
    if 'student_id' not in request.session:
        # If student is not logged in, redirect to login page
        return redirect('student_login')
    
    student_registration_number = request.session.get('student_registration_number')
    student_name = request.session.get('student_name')
    
    # Get all job fairs the student has registered for
    student_registrations = StudentRegistration.objects.filter(
        registration_number=student_registration_number
    ).order_by('-registration_time')
    
    # Get the selected job fair (from query parameter or default to the first one)
    selected_job_fair_id = request.GET.get('job_fair_id')
    
    if not selected_job_fair_id and student_registrations.exists():
        selected_job_fair_id = student_registrations.first().job_fair_id
    
    # Get all company interactions for the selected job fair
    attendances = []
    if selected_job_fair_id:
        from .models import RecruiterStudentAttendance
        from recruiters.models import Recruiter
        from placement_team.models import RecruiterJobFair, Job_fairs
        
        attendance_records = RecruiterStudentAttendance.objects.filter(
            job_fair_id=selected_job_fair_id,
            student_registration_number=student_registration_number
        ).order_by('-timestamp')
        
        for record in attendance_records:
            try:
                recruiter = Recruiter.objects.get(recruiter_id=record.recruiter_id)
                attendances.append({
                    'recruiter_email': recruiter.recruiter_email,
                    'timestamp': record.timestamp,
                    'status': record.status,
                    'round_1': record.round_1,
                    'round_2': record.round_2,
                    'round_3': record.round_3,
                })
            except Recruiter.DoesNotExist:
                pass
        
        try:
            selected_job_fair = Job_fairs.objects.get(job_fair_id=selected_job_fair_id)
        except Job_fairs.DoesNotExist:
            selected_job_fair = None
    else:
        selected_job_fair = None
    
    # Prepare job fairs for the dropdown
    job_fairs = []
    for reg in student_registrations:
        try:
            job_fair = Job_fairs.objects.get(job_fair_id=reg.job_fair_id)
            job_fairs.append({
                'id': job_fair.job_fair_id,
                'district': job_fair.district,
                'date': job_fair.date_of_job_fair,
            })
        except Job_fairs.DoesNotExist:
            pass
    
    return render(request, 'students_app/dashboard.html', {
        'student_name': student_name,
        'registration_number': student_registration_number,
        'job_fairs': job_fairs,
        'selected_job_fair': selected_job_fair,
        'attendances': attendances
    })

def student_logout(request):
    # Clear student session data
    if 'student_id' in request.session:
        del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    if 'student_registration_number' in request.session:
        del request.session['student_registration_number']
    return redirect('student_login')


@csrf_exempt
def mark_recruiter_attendance(request, job_fair_id, recruiter_id):
    # Get the student registration number from the session
    student_reg_number = request.session.get('student_registration_number')
    
    if not student_reg_number:
        message = "Please register for the job fair first!"
        return render(request, 'students_app/attendance_marked.html', {'message': message})

    # Check if the student is registered for this job fair
    student_registration = StudentRegistration.objects.filter(
        job_fair_id=job_fair_id, 
        registration_number=student_reg_number
    ).first()
    
    if not student_registration:
        message = "You are not registered for this job fair!"
        return render(request, 'students_app/attendance_marked.html', {'message': message})
    
    # Record the attendance
    from .models import RecruiterStudentAttendance
    
    attendance, created = RecruiterStudentAttendance.objects.get_or_create(
        job_fair_id=job_fair_id,
        recruiter_id=recruiter_id,
        student_registration_number=student_reg_number
    )
    
    # If this is a new attendance, send WebSocket notification
    if created:
        # Get student details
        student_data = {
            'registration_number': student_registration.registration_number,
            'name': student_registration.name,
            'college_name': student_registration.college_name,
            'has_resume': bool(student_registration.resume),
            'resume_url': student_registration.resume.url if student_registration.resume else None,
        }
        
        # Format timestamp
        timestamp = timezone.localtime(attendance.timestamp).strftime("%b %d, %Y, %I:%M %p")
        
        # Send notification to channel
        channel_layer = get_channel_layer()
        room_group_name = f'recruiter_{recruiter_id}_jobfair_{job_fair_id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'new_attendance',
                'student': student_data,
                'timestamp': timestamp,
                'status': attendance.status,
                'round_1': attendance.round_1,
                'round_2': attendance.round_2,
                'round_3': attendance.round_3,
                'notes': attendance.notes
            }
        )
        
        message = "Attendance marked successfully!"
    else:
        message = "You've already visited this recruiter!"
    
    return render(request, 'students_app/attendance_marked.html', {'message': message})