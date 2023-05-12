# Use Python 3.9 Buster as a base image
FROM python:3.9-buster
ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Update the package lists
RUN apt-get clean all && \
    apt-get update

# Install Vim and OpenSSH
RUN apt-get install -y vim openssh-server

# clean-up apt-get
RUN apt-get clean all && \
    rm -rf /var/lib/apt/lists*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run pytest when the container launches
CMD ["pytest"]
