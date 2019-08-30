import os

from dotenv import load_dotenv
load_dotenv()

class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')

class ProdConfig(Config):
	DEBUG = False
	RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
	RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')


class CeleryConfig:
	broker_url = os.getenv('REDIS_URL')

class AWSConfig:
	aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
	aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
