import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.join(basedir, '..')
load_dotenv(os.path.join(project_root, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SENDER_PRIVATE_KEY_PATH = os.path.join(project_root, os.environ.get('SENDER_PRIVATE_KEY_PATH'))
    SENDER_PUBLIC_KEY_PATH = os.path.join(project_root, os.environ.get('SENDER_PUBLIC_KEY_PATH'))
    RECEIVER_PRIVATE_KEY_PATH = os.path.join(project_root, os.environ.get('RECEIVER_PRIVATE_KEY_PATH'))
    RECEIVER_PUBLIC_KEY_PATH = os.path.join(project_root, os.environ.get('RECEIVER_PUBLIC_KEY_PATH'))
    
    RECORDS_ROOM_PASSWORD = os.environ.get('RECORDS_ROOM_PASSWORD')