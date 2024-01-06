FROM python:3.12-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install uWSGI
RUN pip install uwsgi

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run uwsgi.ini when the container launches
CMD ["uwsgi", "uwsgi.ini"]