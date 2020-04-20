# ------------------------------------------------------------------------------------
# This is the main code for a Flask RESTful application which runs over a cloud sever
# The application demonstrates a range of REST API calls and links to an external REST
# API service dogs.ceo
# The application is connected to the Cassandra Database 
# Author: Courtney Graves
# ------------------------------------------------------------------------------------

# Import statements
from flask import Flask, request, render_template, jsonify
from flask_basicauth import BasicAuth
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from cassandra.cluster import Cluster
import json
import requests

# Connection points for the Cassandra Database
cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)

# To set the HTTP authorisation
auth = HTTPBasicAuth()

# Adding users to the HTTP authorisation
users = {
        "test": generate_password_hash("test"),
        "courts": generate_password_hash("ilovedogs"),
        "username": generate_password_hash("password")
}

# Method to verify the username and password
@auth.verify_password
def verify_password(username, password):
        if username in users:
              return check_password_hash(users.get(username), password)
        return False

# Adding a user for the Basic Authorisation
app.config['BASIC_AUTH_USERNAME'] = 'courts'
app.config['BASIC_AUTH_PASSWORD'] = 'ilovedogs'

# To set the basic authorisation
basic_auth = BasicAuth(app)

# The route for the main home page, featuring a basic html template
@app.route('/dogs')
def home():
        return render_template('home.html')

# Route for the login page for HTTP authorisation, returns a simple welcome message
@app.route('/')
@auth.login_required
def index():
        return "Hello, %s, you now have access to the Doggo Database!" % auth.username()

# Route for basic authorisation, returns simple message
@app.route('/secret')
@basic_auth.required
def secret_view():
        return jsonify('Log in succesful!')

# Connection points for the Cassandra Database
@app.route('/dogs/external/list', methods=['GET'])
def all():
        dog_API_url_template = 'https://dog.ceo/api/breeds/list/all'
        dog_API_url = dog_API_url_template
        resp = requests.get(dog_API_url)
        if resp.ok:
                dogs = resp.json()
                return jsonify(resp.json())
        else:
                print(resp.reason)

# Call to external API with parameter set in the code
@app.route('/dogs/external', methods=['GET'])
def hound():
        dog_API_url_template = 'https://dog.ceo/api/breed/{breed}/list'
        my_breed = 'hound'
        dog_API_url = dog_API_url_template.format(breed = my_breed)
        resp = requests.get(dog_API_url)
        if resp.ok:
                dogs = resp.json()
                return jsonify(resp.json())
        else:
                print(resp.reason)

# Call to external API returning images, used with html to display the images
@app.route('/dogs/external/images', methods=['GET'])
def images():
        dog_API_url_template = 'https://dog.ceo/api/breeds/image/random/4'
        dog_API_url = dog_API_url_template
        resp = requests.get(dog_API_url)
        if resp.ok:
                dogs = resp.json()
                dog_images = dogs["message"]
                return render_template("image.html", images=dog_images)

# Call to external API with parameters set in url
@app.route('/dogs/external/<breed>', methods=['GET'])
def breed(breed):
        dog_API_url_template = 'https://dog.ceo/api/breed/{breed}/list'
        my_breed = format(breed)
        dog_API_url = dog_API_url_template.format(breed = my_breed)
        resp = requests.get(dog_API_url)
        if resp.ok:
                dogs = resp.json()
                return jsonify(resp.json()), 200
        else:
                print(resp.reason)

# Get method for information stored in the database, parameter accepted in URL
@app.route('/dogs/<name>', methods=['GET'])
def profile(name):
        rows = session.execute( """Select*From Dogs.Dog_Table
                                where name = '{}' allow filtering""".format(name))
        for Dogs in rows:
                return jsonify('<h1>This Dog {}, aged {}, is a {} and a {}! They are very petable and has a would pet rating of {} out of 10!</h1>'.format(name,Dogs.age,Dogs.breed,Dogs.good_girl_or_boy,Dogs.would_pet_rating)), 200

        return jsonify('<h1>Error, this Dog is not in the system yet!</h1>'), 404

# Post method to add to the database, used with a curl to add the data
@app.route('/dogs/add', methods=['POST'])
def create():
        session.execute("""INSERT INTO Dogs.Dog_Table(id, name) VALUES( {}, '{}' )""".format(int(request.json['id']),(request.json['name'])))
        return jsonify({'Message': 'Created: /dogs/{}'.format(request.json['name'])}), 201

# Put method to update the database, used with a curl to change the data
@app.route('/dogs/update/<name>', methods=['PUT'])
def update(name):
        session.execute("""UPDATE Dogs.Dog_table SET breed = '{}' WHERE id = {}""".format(request.json['breed'],(int(request.json['id']))))
        return jsonify({'Message':'Updated: dogs/{}'.format(request.json['name'])}), 200

# Delete method to delete information in the database, parameters accepted in the URL
@app.route('/dogs/delete/<id>', methods=['DELETE'])
def delete(id):
        session.execute("""DELETE FROM Dogs.Dog_table WHERE id = {}""".format(int(id)))
        return jsonify({'Message': 'Deleted: dogs/delete/{}'.format(int(id))}), 200

# Code to start the application, host & port are defined here
if __name__ == '__main__':
        app.run(port=443, host='0.0.0.0', debug=True)
       #app.run(ssl_context=('cert.pem', 'key.pem'))
