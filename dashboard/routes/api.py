import sqlite3
import json
from flask import Blueprint, request, jsonify, session
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from routes.auth import login_required, get_managed_guilds

api = Blueprint('api', __name__)

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

def is_authorized(guild_id):
    managed_ids = [str(g['id']) for g in get_managed_guilds(session.get('guilds', []))]
    return guild_id in managed_ids

@api.route('/api/guild/<guild_id>/stock')
@login_required
def get_stock(guild_id):
    if not is_authorized(guild_id):
        return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    services = db.execute(
        "SELECT service_name, COUNT(*) as count FROM accounts WHERE guild_id=? GROUP BY service_name",
        (guild_id,)
    ).fetchall()
    db.close()
    return jsonify([dict(s) for s in services])

@api.route('/api/guild/<guild_id>/stock/delete', methods=['POST'])
@login_required
def delete_stock(guild_id):
    if not is_authorized(guild_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    service = data.get('service_name')
    if not service:
        return jsonify({'error': 'service_name required'}), 400
    db = get_db()
    db.execute("DELETE FROM accounts WHERE guild_id=? AND service_name=?", (guild_id, service))
    db.commit()
    db.close()
    return jsonify({'success': True})

@api.route('/api/guild/<guild_id>/users/blacklist', methods=['POST'])
@login_required
def blacklist_user(guild_id):
    if not is_authorized(guild_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    user_id = data.get('user_id')
    status = data.get('status', True)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    db = get_db()
    db.execute("UPDATE users SET is_blacklisted=? WHERE user_id=?", (1 if status else 0, user_id))
    db.commit()
    db.close()
    return jsonify({'success': True})

@api.route('/api/guild/<guild_id>/settings', methods=['POST'])
@login_required
def update_settings(guild_id):
    if not is_authorized(guild_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    guilds = load_guilds()
    if guild_id not in guilds:
        guilds[guild_id] = {}
    allowed = ['gen-channels', 'premium-gen-channels', 'admin-roles', 'suggestions-channel-id', 'review-channel-id']
    for key in allowed:
        if key in data:
            guilds[guild_id][key] = data[key]
    save_guilds(guilds)
    return jsonify({'success': True})

@api.route('/api/stats')
def public_stats():
    db = get_db()
    try:
        server_count = db.execute("SELECT COUNT(DISTINCT guild_id) FROM accounts").fetchone()[0] or 0
        user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0
        generated = db.execute("SELECT COALESCE(SUM(amount_genned), 0) + COALESCE(SUM(prem_amount_genned), 0) FROM users").fetchone()[0] or 0
        db.close()
        return jsonify({
            "servers": int(server_count),
            "users": int(user_count),
            "generated": int(generated)
        })
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 500
