FROM python

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=naan_mudhalvan_monolith.settings

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run the application using Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "naan_mudhalvan_monolith.asgi:application"]