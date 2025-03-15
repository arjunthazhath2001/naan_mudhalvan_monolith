# Naan Mudhalvan Job Fair Platform

This is a comprehensive web application for managing job fairs in the Naan Mudhalvan program. It facilitates interaction between students, recruiters, placement teams, and program managers in a streamlined digital environment.

![Naan Mudhalvan Logo](https://www.naanmudhalvan.tn.gov.in/_nuxt/img/logo.13a0474.png)

## Features

### Multiple User Roles

- **Students**: Register for job fairs, mark attendance at company booths via QR code scanning, track application status
- **Recruiters**: Manage student candidates through multiple interview rounds, update statuses real-time
- **Placement Team**: Create job fairs, generate QR codes, add companies, view comprehensive analytics
- **Program Managers**: District-level oversight of job fairs, companies, and placement statistics

### Key Functionalities

- **QR Code Generation**: Automatic QR code creation for job fairs and recruiters
- **Real-time Updates**: WebSocket integration for instant attendance notifications and status changes
- **Multi-round Interview Process**: Structured flow through recruitment rounds with proper status tracking
- **Analytics Dashboard**: Comprehensive data visualization for placement teams and program managers
- **Responsive Design**: Optimized for both desktop and mobile devices

## Technology Stack

- **Backend**: Django 5.1
- **Database**: PostgreSQL 13
- **Web Socket**: Django Channels with Daphne ASGI server
- **Frontend**: Bootstrap 5.2, JavaScript
- **Containerization**: Docker, Docker Compose

## Project Structure

The application follows a modular structure with four main Django apps:

- `students`: Handles student registration, login, and interaction with recruiters
- `recruiters`: Manages recruiter authentication and student selection process
- `placement_team`: Provides tools for creating job fairs and adding companies
- `program_managers`: District-level management and oversight

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/naan-mudhalvan-job-fair.git
   cd naan-mudhalvan-job-fair
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up -d
   ```

3. Create a superuser for admin access:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. Create program managers for each district:
   ```bash
   docker-compose exec web python manage.py create_program_managers
   ```

5. Access the application at `http://localhost:8000/nm/`

### Default Credentials

- **Program Managers**: Username: `manager_<district_name>`, Password: `pass_<district_name>`
- **Placement Team**: Create via Django Admin
- **Recruiters**: Added by placement team or program managers
- **Students**: Self-registration through job fair QR codes

## Usage Flow

1. **Placement Team/Program Manager**:
   - Create a job fair for a specific district
   - Add recruiters to the job fair
   - Download and share QR codes

2. **Students**:
   - Scan job fair QR code to register
   - Receive login credentials
   - Visit company booths and scan their QR codes

3. **Recruiters**:
   - Login to view student interactions in real-time
   - Update student status (Pending → Next Round → Placed/Rejected)
   - Manage multiple interview rounds

4. **Analytics**:
   - Track registration count, company attendance, placement statistics
   - Filter by various parameters including rounds and status

## Development

### Project Structure

```
naan_mudhalvan_monolith/
├── placement_team/        # Job fair creation, recruiter management
├── students/              # Student registration and interaction
├── recruiters/            # Recruiter dashboard and candidate management
├── program_managers/      # District-level management
├── naan_mudhalvan_monolith/  # Project settings
```

### Key Components

- **WebSockets**: Used for real-time notifications in `recruiters/consumers.py`
- **Database Models**: Core data structure in each app's `models.py`
- **Views**: Business logic in each app's `views.py`
- **Templates**: UI implementation in each app's `templates/` directory

## Deployment

The application is Dockerized for easy deployment. The `Dockerfile` and `docker-compose.yml` files provide all necessary configuration.

For production deployment:

1. Update the `ALLOWED_HOSTS` and `DEBUG` settings in `docker-compose.yml`
2. Set a strong `SECRET_KEY` in an environment variable
3. Configure proper database credentials
4. Set up HTTPS using a reverse proxy like Nginx

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Naan Mudhalvan program for the initiative
- Django community for the robust framework
- Bootstrap team for the responsive design components