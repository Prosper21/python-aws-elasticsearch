import os

from dotenv import load_dotenv
load_dotenv()

class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')

class ProdConfig(Config):
    DEBUG = False

class CeleryConfig:
	broker_url = os.getenv('REDIS_URL')