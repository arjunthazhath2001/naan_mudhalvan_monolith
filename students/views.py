from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import StudentRegistration
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError



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
                # Now save the instance
                student_registration.save()
                
                # Store student registration number in session
                request.session['student_registration_number'] = student_registration.registration_number
                
                messages.success(request, 'Registration successful! Thank you for registering for the job fair.')
                return redirect('registration_success')
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
    return render(request, 'students_app/registration_success.html')


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
    
    if created:
        message = "Attendance marked successfully!"
    else:
        message = "You've already visited this recruiter!"
    
    return render(request, 'students_app/attendance_marked.html', {'message': message})