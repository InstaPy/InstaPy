import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hammadi-store-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hammadi_store.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-hammadi-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Payment Methods
    LIBYANA_NUMBER = '0923334826'
    MADAR_NUMBER = '0910882830'
    
    # Contact Info
    WHATSAPP_NUMBER = '0910882830'
    TELEGRAM_CHANNEL = 'https://t.me/hammadi_store'
    
    # User Levels
    BRONZE_THRESHOLD = 0
    SILVER_THRESHOLD = 500
    GOLD_THRESHOLD = 2000
