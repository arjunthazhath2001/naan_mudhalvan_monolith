from django.contrib import messages 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Job_fairs
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'placement_team_app/login.html')

def generate_qr_code_image(job_fair_id, district):
    # Create the QR code with slightly reduced box size to make room for text
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L, 
                       box_size=8,  # Reduced from 10 to make room for text
                       border=4)
    
    registration_link = f"http://localhost:8000/nm/students/register/{job_fair_id}/"
    
    qr.add_data(registration_link)
    qr.make(fit=True)

    # Create the QR code image with a white background
    qr_img = qr.make_image(fill="black", back_color='white')
    
    # Convert to RGB mode to allow drawing
    img = qr_img.convert('RGB')
    
    # Get image dimensions
    width, height = img.size
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font with fallback
    try:
        # Increased font sizes
        font_district = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
        font_instruction = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    except IOError:
        # Fallback to default font if TrueType font is not available
        font_district = ImageFont.load_default()
        font_instruction = ImageFont.load_default()
    
    # Prepare text
    district_text = f"{district} Job Fair"
    instruction_text = "STUDENTS MUST REGISTER"
    
    # Calculate text sizes
    district_bbox = draw.textbbox((0, 0), district_text, font=font_district)
    instruction_bbox = draw.textbbox((0, 0), instruction_text, font=font_instruction)
    
    district_text_width = district_bbox[2] - district_bbox[0]
    instruction_text_width = instruction_bbox[2] - instruction_bbox[0]
    
    # Position text (centered horizontally)
    # Move text further down and ensure it's within the image
    district_position = ((width - district_text_width) // 2, height + 10)
    instruction_position = ((width - instruction_text_width) // 2, height + 50)
    
    # Create a new image with extra white space at the bottom
    new_img = Image.new('RGB', (width, height + 100), color='white')
    new_img.paste(img, (0, 0))
    
    # Create a new drawing context for the expanded image
    draw = ImageDraw.Draw(new_img)
    
    # Draw text (black color)
    draw.text(district_position, district_text, font=font_district, fill=(0, 0, 0))
    draw.text(instruction_position, instruction_text, font=font_instruction, fill=(0, 0, 0))
    
    # Save the image to BytesIO
    byte_io = BytesIO()
    new_img.save(byte_io, 'PNG')
    byte_io.seek(0)
    
    return byte_io.getvalue()


@login_required(login_url='login')
def index(request):
    success_message = ""
    qr_image = None
    district = None
    
    if request.method == "POST":
        district = request.POST.get('district')
        date_of_job_fair = request.POST.get('job-fair-date')
        
        job_fair = Job_fairs(district=district, date_of_job_fair=date_of_job_fair)
        job_fair.save()
        
        # Pass district to QR code generation
        qr_code_image = generate_qr_code_image(job_fair.job_fair_id, district)
        
        job_fair.qr_code.save(f"qr_{job_fair.job_fair_id}.png", ContentFile(qr_code_image))
        job_fair.save()
        
        success_message = "Job fair created and QR generated"
        qr_image = job_fair.qr_code.url
    
    return render(request, 'placement_team_app/index.html', {
        'success_message': success_message,
        'qr_image': qr_image,
        'district': district
    })


@login_required(login_url='login')
def companies(request):
    job_fairs= Job_fairs.objects.all()
    job_fair_list = [f"{job_fair.district} - {job_fair.date_of_job_fair}" for job_fair in job_fairs]
    recruiters = [
        {'email': 'hr@axis.com', 'password': 'axis098$$'},
        {'email': 'hr@avionltd.com', 'password': 'avio03@4#'},
        {'email': 'hr@axis.com', 'password': 'axis098$$'}
    ]
    return render(request, 'placement_team_app/companies.html', {'job_fair_list':job_fair_list, 'recruiters': recruiters})