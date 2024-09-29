# Use the official Python image as a base image
# FROM python:3.11.5-slim
FROM python:3.11.5

# Set environment variables
# This prevents Python from writing .pyc files, which aren’t necessary in production.
ENV PYTHONDONTWRITEBYTECODE 1
# This makes sure that Python output is sent straight to the terminal (useful for logging).
ENV PYTHONUNBUFFERED 1

# Create a non-root user
# Creates a non-root user for security reasons.
RUN adduser --disabled-password myuser
USER myuser

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
# Copies files with the appropriate ownership, which is important for security.
COPY --chown=myuser:myuser requirements.txt /app/

# Copy the requirements file and install dependencies
# COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/
# Copy the project files
COPY --chown=myuser:myuser . /app/














