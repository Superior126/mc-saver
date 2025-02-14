from flask import Flask, send_from_directory, request, g, make_response
from flask_cors import CORS
import os
from utils.config_interface import ConfigInterface
from utils.db_interface import DatabaseInterface

app = Flask(__name__, static_folder='flask_static')
CORS(app)

config = ConfigInterface()

def get_db():
    if 'db' not in g:
        g.db = DatabaseInterface().get_connection()
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Ensure root user exists
with app.app_context():
    db = get_db()
    database = DatabaseInterface()
    database.ensure_root_user_exist()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index_route(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    database = DatabaseInterface()

    # Get request data
    try:
        data = request.get_json()
    except Exception:
        return {'error': 'Invalid JSON data'}, 400

    # Check if username and password are present
    if 'username' not in data or 'password' not in data:
        return {'error': 'Username and password are required'}, 400

    # Authenticate user with database
    try:
        session, expiration_time = database.login(data['username'], data['password'])

        # Create json response as well as set session cookie
        response = make_response({'session': session, 'expires': expiration_time})
        response.set_cookie('session_id', session, max_age=86400, httponly=True) # Cookie will expire in 24 hours

        return response, 200

    except database.Exceptions.InvalidCredentials:
        return {'error': 'Invalid credentials'}, 401

    except Exception as e:
        print(e)
        return {'error': 'An internal error occurred'}, 500
    
@app.route('/api/auth/logout', methods=['GET'])
def logout():
    database = DatabaseInterface()

    # Get session id from cookie
    session_id = request.cookies.get('session_id')

    # Check if session id is present
    if not session_id:
        return {'error': 'Session id is required'}, 400

    # Logout user
    try:
        database.logout(session_id)

        # Prepare response and delete session cookie
        response = make_response({'message': 'Logged out'})
        response.set_cookie('session_id', '', expires=0)

        return response, 200

    except Exception as e:
        print(e)
        return {'error': 'An internal error occurred'}, 500
    
# TESTING PLS REMOVE
@app.route('/login_panel', methods=['GET'])
def login_panel():
    return send_from_directory(app.static_folder, 'login_panel.html')

if __name__ == "__main__":
    app.run()
