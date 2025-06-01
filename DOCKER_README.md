# Learning Management System - Docker Setup

This document provides instructions for running the Learning Management System using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd learning-management-system
   ```

2. Configure environment variables:
   - Copy the example environment file:
     ```
     cp backend/.env.example backend/.env
     ```
   - Edit `backend/.env` with your actual configuration values

3. Build and start the containers:
   ```
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Environment Variables

### Backend Environment Variables

The backend requires several environment variables to be set in the `backend/.env` file:

- `OPENAI_API_KEY`: Your Azure OpenAI API key
- `OPENAI_API_BASE`: Azure OpenAI API base URL
- `OPENAI_API_TYPE`: Set to "azure" for Azure OpenAI
- `OPENAI_API_VERSION`: Azure OpenAI API version
- `OPENAI_DEPLOYMENT_NAME`: Your Azure OpenAI deployment name
- `SECRET_KEY`: Secret key for Flask sessions
- `MONGODB_URL`: MongoDB connection string

### Docker Compose Environment Variables

You can customize the MongoDB credentials by setting these environment variables before running docker-compose:

- `MONGO_USERNAME`: MongoDB username (default: admin)
- `MONGO_PASSWORD`: MongoDB password (default: password)

Example:
```
export MONGO_USERNAME=myuser
export MONGO_PASSWORD=mypassword
docker-compose up -d
```

## Container Management

- Start containers: `docker-compose up -d`
- Stop containers: `docker-compose down`
- View logs: `docker-compose logs -f`
- Rebuild containers: `docker-compose up -d --build`

## Data Persistence

The application uses Docker volumes for data persistence:

- `mongodb_data`: Stores MongoDB data
- `backend_data`: Stores Flask session data

## Troubleshooting

1. If the frontend can't connect to the backend, check:
   - Backend container is running: `docker ps`
   - Backend logs for errors: `docker logs lms-backend`
   - CORS configuration in the backend

2. If MongoDB connection fails:
   - Check MongoDB container is running: `docker ps`
   - Verify MongoDB credentials in `.env` file
   - Check MongoDB logs: `docker logs mongodb`