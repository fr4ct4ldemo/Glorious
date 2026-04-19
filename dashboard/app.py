import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, redirect, url_for
from flask_session import Session
from flask_cors import CORS
import config

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')

os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

Session(app)
CORS(app)

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.api import api

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api)

@app.route('/')
def index():
    return redirect(url_for('auth_bp.login_page'))

if __name__ == '__main__':
    print("[+] Glorious Dashboard running at http://localhost:5000")
    app.run(debug=True, port=5000)
