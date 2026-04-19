import sqlite3
import json
import requests
from flask import Blueprint, render_template, session, redirect, url_for
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from routes.auth import login_required, get_managed_guilds

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/landing')
def landing():
    return render_template('landing.html')

def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_guilds():
    try:
        with open(config.GUILDS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_guilds(data):
    with open(config.GUILDS_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def get_bot_guild_ids():
    try:
        headers = {'Authorization': f'Bot {config.BOT_TOKEN}'}
        res = requests.get(f"{config.DISCORD_API_BASE}/users/@me/guilds", headers=headers)
        if res.status_code == 200:
            return {str(g['id']) for g in res.json()}
    except:
        pass
    return set()

def enrich_guild(guild):
    icon = guild.get('icon')
    if icon:
        guild['icon_url'] = f"https://cdn.discordapp.com/icons/{guild['id']}/{icon}.png"
    else:
        guild['icon_url'] = None
    return guild

@dashboard_bp.route('/servers')
@login_required
def servers():
    user_guilds = session.get('guilds', [])
    managed = get_managed_guilds(user_guilds)
    bot_ids = get_bot_guild_ids()
    for g in managed:
        enrich_guild(g)
        g['bot_in_server'] = str(g['id']) in bot_ids
    return render_template('servers.html', user=session['user'], guilds=managed, client_id=config.DISCORD_CLIENT_ID)

@dashboard_bp.route('/dashboard/<guild_id>')
@login_required
def guild_dashboard(guild_id):
    managed_ids = [str(g['id']) for g in get_managed_guilds(session.get('guilds', []))]
    if guild_id not in managed_ids:
        return redirect(url_for('dashboard_bp.servers'))

    db = get_db()
    total_stock = db.execute("SELECT COUNT(*) as c FROM accounts WHERE guild_id=?", (guild_id,)).fetchone()['c']
    total_users = db.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    total_services = db.execute("SELECT COUNT(DISTINCT service_name) as c FROM accounts WHERE guild_id=?", (guild_id,)).fetchone()['c']
    total_genned = db.execute("SELECT COALESCE(SUM(amount_genned), 0) as c FROM users").fetchone()['c']
    recent_users = db.execute("SELECT * FROM users ORDER BY amount_genned DESC LIMIT 5").fetchall()
    db.close()

    guild_info = next((enrich_guild(g) for g in session.get('guilds', []) if str(g['id']) == guild_id), {})
    guild_config = load_guilds().get(guild_id, {})
    guild_name = guild_info.get('name', 'Unknown Guild')

    return render_template('dashboard.html',
        user=session['user'],
        guild=guild_info,
        guild_config=guild_config,
        guild_id=guild_id,
        guild_name=guild_name,
        total_stock=total_stock,
        total_users=total_users,
        total_services=total_services,
        total_genned=total_genned,
        recent_users=recent_users
    )

@dashboard_bp.route('/dashboard/<guild_id>/stock')
@login_required
def guild_stock(guild_id):
    managed_ids = [str(g['id']) for g in get_managed_guilds(session.get('guilds', []))]
    if guild_id not in managed_ids:
        return redirect(url_for('dashboard_bp.servers'))

    db = get_db()
    services = db.execute(
        "SELECT service_name, COUNT(*) as count FROM accounts WHERE guild_id=? GROUP BY service_name",
        (guild_id,)
    ).fetchall()
    db.close()

    guild_info = next((enrich_guild(g) for g in session.get('guilds', []) if str(g['id']) == guild_id), {})
    guild_name = guild_info.get('name', 'Unknown Guild')
    return render_template('stock.html', user=session['user'], guild=guild_info, guild_id=guild_id, guild_name=guild_name, services=services)

@dashboard_bp.route('/dashboard/<guild_id>/users')
@login_required
def guild_users(guild_id):
    managed_ids = [str(g['id']) for g in get_managed_guilds(session.get('guilds', []))]
    if guild_id not in managed_ids:
        return redirect(url_for('dashboard_bp.servers'))

    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY amount_genned DESC").fetchall()
    db.close()

    guild_info = next((enrich_guild(g) for g in session.get('guilds', []) if str(g['id']) == guild_id), {})
    guild_name = guild_info.get('name', 'Unknown Guild')
    return render_template('users.html', user=session['user'], guild=guild_info, guild_id=guild_id, guild_name=guild_name, users=users)

@dashboard_bp.route('/dashboard/<guild_id>/settings')
@login_required
def guild_settings(guild_id):
    managed_ids = [str(g['id']) for g in get_managed_guilds(session.get('guilds', []))]
    if guild_id not in managed_ids:
        return redirect(url_for('dashboard_bp.servers'))

    guild_info = next((enrich_guild(g) for g in session.get('guilds', []) if str(g['id']) == guild_id), {})
    guild_config = load_guilds().get(guild_id, {})
    guild_name = guild_info.get('name', 'Unknown Guild')
    
    gen_channels = guild_config.get('gen-channels', [])
    premium_gen_channels = guild_config.get('premium-gen-channels', [])
    admin_roles = guild_config.get('admin-roles', [])
    suggestions_channel_id = guild_config.get('suggestions-channel-id', '')
    review_channel_id = guild_config.get('review-channel-id', '')
    
    return render_template('settings.html', user=session['user'], guild=guild_info, guild_id=guild_id, guild_name=guild_name,
        gen_channels=gen_channels,
        premium_gen_channels=premium_gen_channels,
        admin_roles=admin_roles,
        suggestions_channel_id=suggestions_channel_id,
        review_channel_id=review_channel_id
    )
