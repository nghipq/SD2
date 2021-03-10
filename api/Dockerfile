#use python-3.7.3 image
FROM python:3.7.3-stretch

#Set the working directory to /server
WORKDIR /server

#Copy the current directory contents into the container at /server
ADD . /server

#Install the dependencies
RUN pip install -r requirement.txt

#run the command to start uWSGI
CMD ["uwsgi", "app.ini"]

