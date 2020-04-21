# Doggo Database

This project was designed to use REST services for a database which is for putting dog information. The project is written in Python's Flask and uses a Cassandra Database to store the information. The main page uses html code to present the first page. The application is deployed in a Docker Container and run over HTTP. 

## Getting started

These instructions are provided to show how the application can be set up to run over a cloud platform.

## Prerequisites
This software is needed in order to run the application, provided are the statements for the command line. The applcation uses the Python3 package.
 
Pip needs to be installed from the Python3 package.
 ``` 
 sudo apt install python3 pip
 ```

Flask is then installed from the pip package.
 ``` 
 sudo install Flask
 ```

 Docker is needed to containerise the application.
 ``` 
 sudo apt install docker.io
 ```

## Usage
### Cassandra database
The Cassandra database is the first aspect to set up. This is where the information is stored for the dogs which are to be displayed.
These commands are used to set up the basic database. See also, Docker deployment for the docker version of cassandra.

To create a keyspace:
``` 
CREATE keyspace Dogs with replication = {'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

In the keyspace to create a simple table:
```
CREATE TABLE Dog_Table(
Id int PRIMARY KEY,
Name text,
Breed text,
Age int,
Good_Girl_Or_Boy text,
Would_Pet_Rating int);
```
Note here the 'ID' is the primary key which is used.

An example of how to add information to the table:
```
INSERT INTO Dogs.Dog_Table (Id, Name, Breed, Age, Good_Girl_Or_Boy, Would_Pet_Rating)
VALUES (1, 'Holly', 'West Highland Terrier', 14, 'Good Girl', 15);
```

Optionally for extra security adding roles provides a restriction to user access:
```
CREATE ROLE Courts WITH PASSWORD = 'CourtsD0gs' AND LOGIN = true;
```

Granting permissions will enable more security as it prevents everyone from being able to change the database
```
CREATE ROLE Dogs_Admin;
GRANT ALL PERMISSIONS on KEYSPACE Dogs to Dogs_Admin; GRANT Dogs_Admin TO Courts;
```
Note if Cassandra is being used for this the cassandra.yaml file will have to be edited from 'AllowAllAutheticator' to 'PasswordAuthenticator' for the authentication section. This can be found in '/etc/cassandra/cassandra.yaml'

### Framework for Flask Application
This is the section of code which will run the application. The top line calls the relevant parts of the packages. The next line creates a the connection point to the Cassandra database. The line after this instance of the class. 
The next lines usually at the end of the code tell the application which host and port to use. The debug is set here too for extra infromation on errors.

Import code:
```
from flask import Flask, request, render_template, jsonify
from flask_basicauth import BasicAuth
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from cassandra.cluster import Cluster
import json
import requests
```

Call to Cassandra connection point and instance of application class created:
``` 
cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)
```

Code to run the application:
``` 
if __name__ == '__main__':
        app.run(port=443, host='0.0.0.0', debug=True)
```

### URL entrance page
This is the the page which will be displayed for the '/' of the URL. This page has a html file added which displays a user friendly frontend static page with images.

``` 
@app.route('/')
def home():
        return render_template('home.html')
```

Example of the code which retrives the images from a shared Dropbox link:
``` 
<img src="https://www.dropbox.com/s/lu3pr3bxsrqdvuk/Holly.JPG?raw=1" width="250" height="250" alt "Holly image">
```
Note the ending of the Dropbox link must be changed to 'raw=1' to allow the server to recieve it.

### GET request call to external API
This GET request displays a simple text page which comes from dog.ceo API. It displays the breed information for the dogs. The first line of code is the URL route to the application. The method is set as GET which will retrieve the information. The next line is the function call. Below is the function which retrives the dog.ceo URL where their dog breed information is. The code will fetch the data from the dog.ceo URL and then display it or will print the reason why it could not find this.

``` 
@app.route('/dogs/external/list', methods=['GET'])
def external():
        dog_API_url_template = 'https://dog.ceo/api/breeds/list/all'
        dog_API_url = dog_API_url_template
        resp = requests.get(dog_API_url)
        if resp.ok:
                dogs = resp.json()
                return jsonify(resp.json()), 200
        else:
                print(resp.reason)
```

Example of code where the parameter is set for the dog.ceo URL in the application:
```
@app.route('/dogs/external', methods=['GET'])
def hound():
        dog_API_url_template = 'https://dog.ceo/api/breed/{breed}/list'
        my_breed = 'hound'
        dog_API_url = dog_API_url_template.format(breed = my_breed)
```

Example of code where the parameter is set in the URL:
``` 
@app.route('/dogs/external/<breed>', methods=['GET'])
def breed(breed):
        dog_API_url_template = 'https://dog.ceo/api/breed/{breed}/list'
        my_breed = format(breed)
        dog_API_url = dog_API_url_template.format(breed = my_breed)
        resp = requests.get(dog_API_url)
```

html example to display the images from dog.ceo:
``` 
<!DOCTYPE html>
<html>
<body>
{% for image in images %}
<img src={{image}} width="350" height="350" alt="dog images">
{% endfor %}
</body>
</html>
```

### GET request for Cassandra database
This code is a GET request to return information which is stored in the cassandra database. The first line of the code is the URL route and accepts the request in the URL. The Cassandra cqlsh code is written to be executed, this will find the relevant infomation. The lines after this bring the information to the application and display it on the static webpage. They format the information. 

``` 
@app.route('/dogs/<name>', methods=['GET'])
def profile(name):
        rows = session.execute( """Select*From Dogs.Dog_Table
                                where name = '{}' allow filtering""".format(name))
        for Dogs in rows:
                return jsonify('This Dog {}, aged {}, is a {} and a {}! They are very petable and has a would pet rating of {} out of 10!'.format(name,Dogs.age,Dogs.breed,Dogs.good_girl_or_boy,Dogs.would_pet_rating)), 200
        return jsonify('Error, this Dog is not in the system yet!'), 400
```

### POST request for Cassandra database
This code is a example of the POST request which will add new dog information directly to the database without having to open Cassandra and do it there. Here the request only accepts name and id but it could be expanded to include all the information.

```
@app.route('/dogs/add', methods=['POST'])
def create():
        session.execute("""INSERT INTO Dogs.Dog_Table(id, name) VALUES( {}, '{}' )""".format(int(request.json['id']),(request.json['name'])))
        return jsonify({'Message': 'Created: /Dogs/{}'.format(request.json['name'])}), 201
 ```

Example of the curl request: 
``` 
curl -i -H "Content-Type: application/json" -X POST -d '{"id":"11", "name":"Muffin"}' host:443/dogs/add
```

Successful output:
``` 
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 41
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Mon, 20 Apr 2020 10:02:22 GMT

{
  "Message": "Created: /dogs/Muffin"
}
```

### PUT request for Cassandra database
This is an example of a PUT request for the Cassandra database. This code will update existing information for a dog in the table.

```
@app.route('/dogs/update/<name>', methods=['PUT'])
def update(name):
        session.execute("""UPDATE Dogs.Dog_table SET breed = '{}' WHERE id ={}""".format(request.json['breed'],(int(request.json['id']))))
        return jsonify({'Message':'Updated: dogs/{}'.format(name)}), 200
```

Example of the curl request: 
``` 
curl -i -H "Content-Type: application/json" -X PUT -d '{"breed":"Yorksire Terrier","id":"12"}' host:443/dogs/update/Dodge
```

Successful output:
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 39
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Mon, 20 Apr 2020 17:10:06 GMT

{
  "Message": "Updated: dogs/Dodge"
}
```

### DELETE request for Cassandra database
This DELETE method will delete a dogs information from the database. The parameter is the Cassandra primary key which is accepted in the URL.

```
@app.route('/dogs/delete/<id>', methods=['DELETE'])
def delete(id)
        session.execute("""DELETE FROM Dogs.Dog_table WHERE id = {}""".format(int(id)))
        return jsonify({'Message': 'Deleted: dogs/delete/{}'.format(int(id))}), 200
```

Example of the curl delete request: 
```
curl -X DELETE host:443/dogs/delete/12
```

Successful output:
```
{
  "Message": "Deleted: dogs/delete/12"
}
```

### To serve the applciation over HTTPS
This is a simple way to set up HTTPS. Adding this code to the application will allow it to be served over HTTPS which adds extra security. The following steps show how to generate a certifcate and add the code into the application to allow it to run using the certificates.

To install SSL package from pip in the command line:
```
sudo pip install pyopenssl
```

An example of creating a certificate:
```
sudo openssl req -x509 -newkey ras:4096 -nodes -out certdog.pem -keyout keydog.pem -days 10
```

Adding the following line to the applicatio will allow the application to use our self-signed certificate and for the application the be served over HTTPS:
```
app.run(ssl_context=('certdog.pem', 'keydog.pem'))
```

### Simple Authorisation 
This is a way to add a simple log in to the application. It uses Flask-BasicAuth. This method is not very secure as it does not hash any of the information it is all plaintext. It protects only part of the application.

Flask Basic-Auth: 
```
sudo pip3 install Flask-BasicAuth
```

Example of usage for BasicAuth:
```
app.config['BASIC_AUTH_USERNAME'] = 'courts'
app.config['BASIC_AUTH_PASSWORD'] = 'ilovedogs'

basic_auth = BasicAuth(app)

@app.route('/secret')
@basic_auth.required
def secret_view():
        return jsonify('Log in succesful!')
```

### HTTP Authorisation
This is another slightly more complex security method which offers more protection. It uses HTTP in this method. This extention stores the user information in the application but a more complex security method would store it in a secure database. For this application this was enough protection.

Flask HTTPAuth: 
```
sudo pip3 install Flask-HTTPAuth
```

Example of usage for HTTPBasicAuth:
```
auth = HTTPBasicAuth()

users = {
        "test": generate_password_hash("test"),
        "courts": generate_password_hash("ilovedogs"),
        "username": generate_password_hash("password")

@auth.verify_password
def verify_password(username, password):
        if username in users:
              return check_password_hash(users.get(username), password)
        return False

@app.route('/')
@auth.login_required
def index():
        return "Hello, %s, you now have access to the Doggo Database!" % auth.username()
```

### Deployment in a Docker Container
To wrap this application in a container these are the following steps. This is good practice because they are more lightweight than a complete VM.

To install Docker: 
```
sudo apt update docker.io
```

Example of Dockerfile, this has what the application needs to create a docker image: 
```
FROM python:3.7-alpine
WORKDIR /project
COPY . /project
RUN pip install -U -r requirements.txt
EXPOSE 443
CMD ["python", "project.py"]
```

Example of requirements.txt, which is a list of the required of the modules and packages we are using: 
```
pip
Flask
cassandra-driver
requests
Flask-basicauth
Flask-HTTPAuth
```

To get the Cassandra Docker Image:
```
sudo docker pull cassandra:latest
```

To create a cassandra instance in the docker:
```
sudo docker run --name cassandra-dogs -p 9042:9042 -d cassandra:latest
```

To build the image container: 
```
sudo docker build . --tag=cassandra-dogs
```

To port bind the application container: 
```
sudo docker run -d 443:443 cassandra-dogs
```

### Built with
- Python
- Flask
- Pip
- Cassadra Apache
- Docker

### Authors 
Courtney Graves

### Acknowledgements
https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

https://dog.ceo/dog-api/

https://github.com/miguelgrinberg/Flask-HTTPAuth
