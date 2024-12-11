from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import os

from dotenv import find_dotenv, load_dotenv

path = find_dotenv()

load_dotenv(path)


app = Flask(__name__)



user= os.getenv('SQL_USERNAME') 
password= os.getenv('SQL_PASSWORD') 
host='aws-0-us-east-1.pooler.supabase.com'
port=6543 
dbname= os.getenv('SQL_DBNAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from TripAdvisor import routes

