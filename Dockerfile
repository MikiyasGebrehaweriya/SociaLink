# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /usr/src/app/


# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "socialink.wsgi:application"]





# # Use the official Python image.
# FROM python:3.11-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set work directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     && apt-get clean

# # Install Python dependencies
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY . /app/



# # Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "socialink.wsgi:application"]










# FROM python:3.11.5-slim

# # Copy requirements.txt to the container
# COPY ./requirements.txt /requirements.txt

# # Copy the entire project root directory (where your Django code and Dockerfile reside) to /app in the container
# COPY . /app

# # Set /app as the working directory
# WORKDIR /app

# # Set up a virtual environment and install dependencies
# RUN python -m venv /py && \
#     /py/bin/pip install --upgrade pip && \
#     /py/bin/pip install -r /requirements.txt && \
#     adduser --disabled-password --no-create-home django-user

# # Update PATH for the virtual environment
# ENV PATH="/py/bin:$PATH"
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Run the application as a non-root user
# USER django-user


# # Run Gunicorn to serve the Django application
# CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 socialink.wsgi:application












































# # Use an official Python runtime as a parent image
# FROM python:3.11.5

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file into the container at /app
# COPY requirements.txt /app/

# # Install dependencies
# RUN pip install -r requirements.txt

# # Copy the rest of the application code into the container at /app
# COPY . /app/

# # Set environment variables
# ENV PYTHONUNBUFFERED=1

# # Expose the port the app runs on
# EXPOSE 4000

# # Run the Django development server
# CMD ["python", "manage.py", "runsslserver", "0.0.0.0:4000"]
