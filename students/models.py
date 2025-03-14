# students/models.py - Update the StudentRegistration model

from django.db import models

class StudentRegistration(models.Model):
    job_fair_id = models.IntegerField()
    name = models.CharField(max_length=100)
    college_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    registration_time = models.DateTimeField(auto_now_add=True)
    
    # Authentication fields
    password = models.CharField(max_length=50, null=True, blank=True)
    is_first_login = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'student_registrations'
        constraints = [
            models.UniqueConstraint(
                fields=['job_fair_id', 'registration_number'], 
                name='unique_student_job_fair_registration'
            )]
    
    def __str__(self):
        return f"{self.name} - {self.college_name}"


# Update the RecruiterStudentAttendance model in students/models.py

class RecruiterStudentAttendance(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('next', 'Next Round'),  # Changed from 'shortlisted' to 'next'
        ('placed', 'Placed'),
        ('rejected', 'Rejected'),
        ('removed', 'Placed Elsewhere')  # New status when placed by another recruiter
    )
    
    ROUND_STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    )
    
    job_fair_id = models.IntegerField()
    recruiter_id = models.IntegerField()
    student_registration_number = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Status field for overall status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Round status fields
    round_1 = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES, default='not_started')
    round_2 = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES, default='not_started')
    round_3 = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES, default='not_started')
    
    # Current round number (1, 2, or 3)
    current_round = models.IntegerField(default=1)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'job_fair_recruiter_student_attendance'
        constraints = [
            models.UniqueConstraint(
                fields=['job_fair_id', 'recruiter_id', 'student_registration_number'], 
                name='unique_student_recruiter_attendance'
            )
        ]