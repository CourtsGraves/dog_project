# ------------------------------------------------------------------------------------
# This is the dockerfile statments for the application
# It contains the information the docker needs to run
# Author: Courtney Graves
# ------------------------------------------------------------------------------------

FROM python:3.7-alpine
WORKDIR /project
COPY . /project
RUN pip install -U -r requirements.txt
EXPOSE 443
CMD ["python", "project.py"]
