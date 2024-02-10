FROM python:3.12-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install uwsgi
RUN apt-get update && apt-get -y install build-essential python3-dev && pip install uwsgi==2.0.23

# Add the current directory contents into the container at /app
COPY . /app

# Run uwsgi.ini when the container launches
CMD ["bash", "-c", "PORT=\"${PORT:=5000}\" && uwsgi --ini uwsgi.ini --http :${PORT}"]
