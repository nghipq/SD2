from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEME_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "f781f2912c6ba76de63a12148f5d1edb933a58ad691cc57f"

db = SQLAlchemy(app)
ma = Marshmallow(app)

from server import routes
