import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-wildf22l-ssadsadn111141322f1dwqdqdsd4e22ver-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # REDIS_HOST = os.environ.get('REDIS_URL') or 'localhost'
    # REDIS_PORT = 6379
    # REDIS_DB = 0

    
