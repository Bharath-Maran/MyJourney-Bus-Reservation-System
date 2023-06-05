#Esential importations for the web application.
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_mysqldb import MySQL
import json
import configparser

#Creates a instance of the Flask and assigns it to 'app'.
app = Flask(__name__)

#Parsing the configuration file
config = configparser.ConfigParser()
config.read('config.cfg')
host = config.get('mysql', 'host')
user = config.get('mysql', 'user')
password = config.get('mysql', 'password')
db = config.get('mysql', 'db')
secret_key = config.get('app', 'secret_key')


#Database configuration.   
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = db

#Secret key to store the session data in server-side.
app.secret_key = secret_key

#Creates the instance of the MySQL and assigns it to 'mysql'.
mysql = MySQL(app)

