from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Recruiter
from placement_team.models import RecruiterJobFair, Job_fairs
from students.models import RecruiterStudentAttendance, StudentRegistration
from django.http import JsonResponse

def recruiter_login(request):
    if 'recruiter_id' in request.session:
        # If recruiter is already logged in, redirect to dashboard
        return redirect('recruiter_dashboard')
        
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            recruiter = Recruiter.objects.get(recruiter_email=email, recruiter_password=password)
            # Store recruiter ID in session
            request.session['recruiter_id'] = recruiter.recruiter_id
            request.session['recruiter_email'] = recruiter.recruiter_email
            return redirect('recruiter_dashboard')
        except Recruiter.DoesNotExist:
            messages.error(request, "Invalid email or password")
    
    return render(request, 'recruiters_app/login.html')

def recruiter_dashboard(request):
    if 'recruiter_id' not in request.session:
        # If recruiter is not logged in, redirect to login page
        return redirect('recruiter_login')
    
    recruiter_id = request.session['recruiter_id']
    recruiter_email = request.session['recruiter_email']
    
    try:
        recruiter = Recruiter.objects.get(recruiter_id=recruiter_id)
        
        # Get the recruiter's job fairs
        recruiter_job_fair = RecruiterJobFair.objects.filter(recruiter=recruiter).first()
        
        qr_code_url = None
        job_fair = None
        attendances = []
        
        if recruiter_job_fair:
            job_fair = recruiter_job_fair.job_fair
            if recruiter_job_fair.qr_code:
                qr_code_url = recruiter_job_fair.qr_code.url
            
            # Get student attendances for this recruiter at this job fair
            attendance_records = RecruiterStudentAttendance.objects.filter(
                recruiter_id=recruiter_id, 
                job_fair_id=job_fair.job_fair_id
            )
            
            # Enhance attendance records with student details
            for record in attendance_records:
                try:
                    student = StudentRegistration.objects.get(
                        registration_number=record.student_registration_number,
                        job_fair_id=job_fair.job_fair_id
                    )
                    attendances.append({
                        'timestamp': record.timestamp,
                        'student': student
                    })
                except StudentRegistration.DoesNotExist:
                    # Handle case where student record not found
                    pass
        
        return render(request, 'recruiters_app/dashboard.html', {
            'recruiter_email': recruiter_email,
            'recruiter_id': recruiter_id,
            'qr_code_url': qr_code_url,
            'job_fair': job_fair,
            'attendances': attendances
        })
        
    except Recruiter.DoesNotExist:
        # Handle invalid session data
        del request.session['recruiter_id']
        del request.session['recruiter_email']
        return redirect('recruiter_login')

def recruiter_logout(request):
    # Clear session data
    if 'recruiter_id' in request.session:
        del request.session['recruiter_id']
    if 'recruiter_email' in request.session:
        del request.session['recruiter_email']
    return redirect('recruiter_login')