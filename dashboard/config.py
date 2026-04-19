import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

main_config = json.load(open(os.path.join(BASE_DIR, 'config.json')))

SECRET_KEY = os.getenv('SECRET_KEY', 'glorious-secret-key')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_API_BASE = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = 'https://discord.com/api/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
BOT_TOKEN = main_config.get('token')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
GUILDS_PATH = os.path.join(BASE_DIR, 'guilds.json')
NEON_GREEN = '#39FF14'
