# Base image
FROM python:3.11.1-alpine3.17

# Set the working directory in the container
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry and project dependencies
RUN pip install --no-cache-dir poetry && \
    poetry install --no-root --no-interaction --no-ansi

# Copy the project code to the container
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=0 \
    PORT=8000

# Expose the Django development server port
EXPOSE ${PORT}

# Copy Gunicorn configuration file
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Run Gunicorn with your Django app using the config file
WORKDIR /app/src
# CMD ["poetry", "run", "gunicorn", "--config", "/app/gunicorn.conf.py", "bookingsystem.wsgi:application"]
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "bookingsystem.wsgi:application"]





# CMD ["poetry", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]

