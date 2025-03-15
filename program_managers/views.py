# program_managers/views.py
import os
import random
import string
from django.contrib import messages 
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count, Q

from .models import ProgramManager
from recruiters.models import Recruiter
from placement_team.models import Job_fairs, RecruiterJobFair
from students.models import StudentRegistration, RecruiterStudentAttendance

def program_manager_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'program_manager_id' not in request.session:
            messages.error(request, "Please log in to access this page.")
            return redirect('program_manager_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    if 'program_manager_id' in request.session:
        return redirect('program_manager_index')
        
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            manager = ProgramManager.objects.get(username=username, password=password)
            # Store manager info in session
            request.session['program_manager_id'] = manager.manager_id
            request.session['program_manager_username'] = manager.username
            request.session['program_manager_district'] = manager.district
            return redirect('program_manager_index')
        except ProgramManager.DoesNotExist:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'program_managers/login.html')

def logout_view(request):
    # Clear all session data related to program manager
    if 'program_manager_id' in request.session:
        del request.session['program_manager_id']
    if 'program_manager_username' in request.session:
        del request.session['program_manager_username']
    if 'program_manager_district' in request.session:
        del request.session['program_manager_district']
    
    messages.success(request, "You have been logged out successfully.")
    return redirect('program_manager_login')

@program_manager_login_required
def index(request):
    district = request.session.get('program_manager_district')
    # Get job fairs specific to the manager's district
    job_fairs = Job_fairs.objects.filter(district=district).order_by('-date_of_creation')
    
    return render(request, 'program_managers/index.html', {
        'job_fairs': job_fairs,
        'district': district
    })

@program_manager_login_required
def companies(request):
    district = request.session.get('program_manager_district')
    job_fairs = Job_fairs.objects.filter(district=district)
    selected_job_fair_id = None
    
    if request.method == "POST":
        job_fair_id = request.POST.get('job_fair')
        selected_job_fair_id = job_fair_id
        recruiter_email = request.POST.get('recruiter_email')
        
        if not job_fair_id or not recruiter_email:
            return redirect('program_manager_companies')
            
        # Ensure the job fair belongs to this district
        try:
            job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
        except Job_fairs.DoesNotExist:
            messages.error(request, "Invalid job fair")
            return redirect('program_manager_companies')
            
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        recruiter, created = Recruiter.objects.get_or_create(
            recruiter_email=recruiter_email, 
            defaults={'recruiter_password': password}
        )
        
        if not created and not recruiter.recruiter_password:
            recruiter.recruiter_password = password
            recruiter.save()
        
        # Create the recruiter_job_fair relationship
        recruiter_job_fair, created_rjf = RecruiterJobFair.objects.get_or_create(
            recruiter=recruiter,
            job_fair=job_fair
        )
        
        if not recruiter_job_fair.qr_code:
            from placement_team.views import generate_recruiter_qr_code
            from django.core.files.base import ContentFile
            
            qr_code_image = generate_recruiter_qr_code(job_fair_id, recruiter.recruiter_id)
            recruiter_job_fair.qr_code.save(
                f"recruiter_job_fair_{job_fair_id}_{recruiter.recruiter_id}.png", 
                ContentFile(qr_code_image)
            )
            recruiter_job_fair.save()
        
        return redirect(f'/nm/pmanager/companies?job_fair_id={job_fair_id}')
    else:
        selected_job_fair_id = request.GET.get('job_fair_id')
    
    return render(request, 'program_managers/companies.html', {
        'job_fair_list': job_fairs,
        'selected_job_fair_id': selected_job_fair_id,
        'district': district
    })

@program_manager_login_required
def analytics(request):
    district = request.session.get('program_manager_district')
    job_fairs = Job_fairs.objects.filter(district=district).order_by('-date_of_creation')
    selected_job_fair = None
    student_count = 0
    company_count = 0
    companies = []

    # Get the selected job fair ID from the query parameter
    job_fair_id = request.GET.get('job_fair_id')
    
    if job_fair_id:
        try:
            selected_job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
            
            # Count students registered for this job fair
            student_count = StudentRegistration.objects.filter(job_fair_id=job_fair_id).count()
            
            # Get recruiters who attended this job fair
            recruiter_job_fairs = RecruiterJobFair.objects.filter(job_fair=selected_job_fair)
            company_count = recruiter_job_fairs.count()
            
            # Get attendance data for each company
            for rjf in recruiter_job_fairs:
                # Count attendance statistics
                attendance_stats = RecruiterStudentAttendance.objects.filter(
                    job_fair_id=job_fair_id,
                    recruiter_id=rjf.recruiter.recruiter_id
                ).aggregate(
                    student_count=Count('student_registration_number'),
                    shortlisted=Count('student_registration_number', filter=Q(status='shortlisted')),
                    placed=Count('student_registration_number', filter=Q(status='placed')),
                    rejected=Count('student_registration_number', filter=Q(status='rejected'))
                )
                
                companies.append({
                    'recruiter_id': rjf.recruiter.recruiter_id,
                    'email': rjf.recruiter.recruiter_email,
                    'student_count': attendance_stats['student_count'],
                    'shortlisted': attendance_stats['shortlisted'],
                    'placed': attendance_stats['placed'],
                    'rejected': attendance_stats['rejected']
                })
            
            # Sort companies by student attendance count (descending)
            companies.sort(key=lambda x: x['student_count'], reverse=True)
            
        except Job_fairs.DoesNotExist:
            pass
    
    return render(request, 'program_managers/analytics.html', {
        'job_fairs': job_fairs,
        'selected_job_fair': selected_job_fair,
        'student_count': student_count,
        'company_count': company_count,
        'companies': companies,
        'district': district
    })




def get_recruiters_for_job_fair(request, job_fair_id):
    """Get recruiters for a specific job fair"""
    if 'program_manager_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
        
    district = request.session.get('program_manager_district')
    
    try:
        job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
        
        # Get all RecruiterJobFair entries for this job fair
        recruiter_job_fairs = RecruiterJobFair.objects.filter(job_fair=job_fair)
        
        # Get all associated recruiters
        recruiters_data = []
        for rjf in recruiter_job_fairs:
            recruiters_data.append({
                'id': rjf.recruiter.recruiter_id,
                'email': rjf.recruiter.recruiter_email,
                'password': rjf.recruiter.recruiter_password,
                'qr_code_url': rjf.qr_code.url if rjf.qr_code else None
            })
        
        return JsonResponse({'recruiters': recruiters_data})
    except Job_fairs.DoesNotExist:
        return JsonResponse({'error': 'Job fair not found or not in your district'}, status=404)

def reset_recruiter_password(request):
    if 'program_manager_id' not in request.session:
        return redirect('program_manager_login')
        
    district = request.session.get('program_manager_district')
        
    if request.method == "POST":
        recruiter_id = request.POST.get('recruiter_id')
        job_fair_id = request.POST.get('job_fair_id')
        
        try:
            # Verify job fair belongs to this district
            job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
            
            # Generate a new random password
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Update the recruiter's password
            recruiter = Recruiter.objects.get(recruiter_id=recruiter_id)
            recruiter.recruiter_password = new_password
            recruiter.save()
            
            # Redirect with the job fair ID to maintain selection
            return redirect(f'/nm/pmanager/companies?job_fair_id={job_fair_id}')
        except (Job_fairs.DoesNotExist, Recruiter.DoesNotExist):
            pass
    
    return redirect('program_manager_companies')

def delete_recruiter_from_job_fair(request):
    if 'program_manager_id' not in request.session:
        return redirect('program_manager_login')
        
    district = request.session.get('program_manager_district')
    
    if request.method == "POST":
        recruiter_id = request.POST.get('recruiter_id')
        job_fair_id = request.POST.get('job_fair_id')
        
        if not recruiter_id or not job_fair_id:
            return redirect('program_manager_companies')
            
        try:
            # Verify job fair belongs to this district
            job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
            recruiter = Recruiter.objects.get(recruiter_id=recruiter_id)
            
            recruiter_job_fair = RecruiterJobFair.objects.filter(
                recruiter=recruiter,
                job_fair=job_fair
            ).first()
            
            if recruiter_job_fair:
                # Delete the QR code file if it exists
                if recruiter_job_fair.qr_code:
                    try:
                        if os.path.isfile(recruiter_job_fair.qr_code.path):
                            os.remove(recruiter_job_fair.qr_code.path)
                    except Exception as e:
                        # Just log the error but continue with deletion
                        print(f"Error removing QR code file: {e}")
                
                # Delete the recruiter-job fair relationship
                recruiter_job_fair.delete()
            
        except (Job_fairs.DoesNotExist, Recruiter.DoesNotExist):
            pass
        
        # Redirect back to the companies page with the job fair ID to maintain selection
        return redirect(f'/nm/pmanager/companies?job_fair_id={job_fair_id}')
    
    return redirect('program_manager_companies')






def get_company_students(request, job_fair_id, recruiter_id):
    """API to get students who visited a specific company at a job fair"""
    if 'program_manager_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    district = request.session.get('program_manager_district')
    
    try:
        # Verify job fair belongs to this district
        job_fair = Job_fairs.objects.get(job_fair_id=job_fair_id, district=district)
        
        # Get attendance records for this company
        attendances = RecruiterStudentAttendance.objects.filter(
            job_fair_id=job_fair_id,
            recruiter_id=recruiter_id
        ).order_by('-timestamp')
        
        students = []
        for attendance in attendances:
            try:
                student = StudentRegistration.objects.get(
                    job_fair_id=job_fair_id,
                    registration_number=attendance.student_registration_number
                )
                
                # Create round history to track which rounds the student participated in
                round_history = []
                
                # Round 1 - all students who visited should have data for round 1
                round_1_data = {
                    'round_number': 1,
                    'status': attendance.round_1 if attendance.round_1 != 'not_started' else 'pending'
                }
                round_history.append(round_1_data)
                
                # Round 2 - only include if the student actually participated in round 2
                # This means they passed round 1 or their current round is at least 2
                if attendance.round_1 == 'passed' or attendance.current_round >= 2:
                    round_2_data = {
                        'round_number': 2,
                        'status': attendance.round_2
                    }
                    round_history.append(round_2_data)
                
                # Round 3 - only include if the student actually participated in round 3
                # This means they passed round 2 or their current round is 3
                if attendance.round_2 == 'passed' or attendance.current_round >= 3:
                    round_3_data = {
                        'round_number': 3,
                        'status': attendance.round_3
                    }
                    round_history.append(round_3_data)
                
                students.append({
                    'registration_number': student.registration_number,
                    'name': student.name,
                    'college': student.college_name,
                    'status': attendance.status,
                    'timestamp': attendance.timestamp.strftime('%d/%m/%Y %I:%M %p'),
                    'current_round': attendance.current_round,
                    'round_history': round_history,
                    'highest_round': max([r['round_number'] for r in round_history]),
                    'round_1_status': attendance.round_1,
                    'round_2_status': attendance.round_2,
                    'round_3_status': attendance.round_3
                })
            except StudentRegistration.DoesNotExist:
                # Skip if student record not found
                pass
        
        return JsonResponse({'students': students})
    
    except Job_fairs.DoesNotExist:
        return JsonResponse({'error': 'Job fair not found or not in your district'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)