import requests
import urllib.parse
from functools import wraps
from flask import Blueprint, redirect, request, session, url_for, render_template
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

auth_bp = Blueprint('auth_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_bp.login_page'))
        return f(*args, **kwargs)
    return decorated

def get_managed_guilds(user_guilds):
    managed = []
    for guild in user_guilds:
        permissions = int(guild.get('permissions', 0))
        if permissions & 0x20 or permissions & 0x8:
            managed.append(guild)
    return managed

@auth_bp.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard_bp.servers'))
    return render_template('login.html')

@auth_bp.route('/auth/discord')
def discord_login():
    params = {
        'client_id': config.DISCORD_CLIENT_ID,
        'redirect_uri': config.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify guilds'
    }
    url = f"{config.DISCORD_OAUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('auth_bp.login_page'))

    data = {
        'client_id': config.DISCORD_CLIENT_ID,
        'client_secret': config.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.DISCORD_REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_res = requests.post(config.DISCORD_TOKEN_URL, data=data, headers=headers)
    token_data = token_res.json()

    if 'access_token' not in token_data:
        return redirect(url_for('auth.login_page'))

    access_token = token_data['access_token']

    user_res = requests.get(
        f"{config.DISCORD_API_BASE}/users/@me",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_data = user_res.json()

    guilds_res = requests.get(
        f"{config.DISCORD_API_BASE}/users/@me/guilds",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    guilds_data = guilds_res.json()

    session['user'] = user_data
    session['access_token'] = access_token
    session['guilds'] = guilds_data

    return redirect(url_for('dashboard_bp.servers'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login_page'))
