FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=main.py \
    FLASK_ENV=production

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy .env file if present (for environment variables)
COPY .env .env

# Create a non-root user and switch to it
RUN adduser -D -g '' appuser && chown -R appuser:appuser /app
USER appuser

# Create necessary directories for Flask session
RUN mkdir -p /app/flask_session && chmod 755 /app/flask_session

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
