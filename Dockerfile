# Pull base image 
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

#install pipenv
RUN pip install pipenv

# Install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system

# Copy project
COPY . .

EXPOSE 8000