import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# configurations from config.py
app.config.from_object('config')
db = SQLAlchemy(app)

# build the database
db.create_all()

# import routes here
from app.routes.products import product_blueprint
app.register_blueprint(product_blueprint)