# Use official lightweight Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent straight to terminal (not buffered)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Run the task manager; -i flag required when running: docker run -it kevalarmano/console-app
CMD ["python", "task_manager.py"]
