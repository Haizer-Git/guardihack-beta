import os
import redis
from flask_sqlalchemy import SQLAlchemy
from services.mail_service import MailService

db = SQLAlchemy()

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
mail_service = MailService()