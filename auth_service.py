# OSU CS 361
# auth_service.py

import os
import json
import portalocker    # locks data when the file is being written
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt     # used for password hashing

# app setup
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_dev_secret_key')
USER_DATA_FILE = 'users.json'   # name of the local JSON file that stores user data


# helpers
def ensure_user_file():
    """
    check that the user data file exists
    if not, it creates a new file
    """
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as user_data:
            json.dump({}, user_data)

def load_users():
    """
    loads user data from the JSON file
    locks it to prevent other processes from writing to the file while it's being read
    """
    ensure_user_file()
    with open(USER_DATA_FILE, 'r') as user_data:
        portalocker.lock(user_data, portalocker.LOCK_EX)
        return json.load(user_data)

def save_users(users):
    """
    takes a dictionary containing all the user data that needs to be saved
    and saves user data to the JSON file
    lock used to prevent data corruption
    """
    ensure_user_file()
    with open(USER_DATA_FILE, 'w') as user_data:
        portalocker.lock(user_data, portalocker.LOCK_EX)
        json.dump(users, user_data, indent=4)   # indent=4 just makes the json legible

# REGISTER USER
@app.route('/register', methods=['POST'])
def register():
    """
    handles new user registration requests
    expects a JSON payload with 'username' and 'password'
    """
    data = request.get_json()
    # ensure request contains all required fields
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request. Username and password are required.'}), 400

    username = data['username']
    password = data['password']

    # ensure username and password fields are not empty
    if not username.strip() or not password.strip():
        return jsonify({'error': 'Username and password cannot be empty.'}), 400

    # load exisiting users from file
    users = load_users()

    # check if username already taken
    if username in users:
        return jsonify({'error': 'Username already exists.'}), 409 # conflict

    # hash password & save
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    users[username] = {
        'password': hashed_pw,
        'wins': 0,
        'losses': 0,
        'games_played': 0
    }

    # save data to file
    save_users(users)

    return jsonify({'message': f"User '{username}' registered successfully."}), 201 # registered

# LOGIN USER
@app.route('/login', methods=['POST'])
def login():
    """
    handles login requests
    expects a JSON payload with 'username' and 'password'
    """
    data = request.get_json()
    # ensure  the request body contains all required fields
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request. Username and password are required.'}), 400

    username = data['username']
    password = data['password']

    # load exisiting users from file
    users = load_users()

    # check if username matches
    if username not in users:
        return jsonify({'error': 'Invalid username or password.'}), 401 # unauthorized

    # check if password matches
    stored_hash = users[username]['password']
    if not bcrypt.check_password_hash(stored_hash, password):
        return jsonify({'error': 'Invalid username or password.'}), 401 # unauthorized

    return jsonify({'message': f"Login successful for user '{username}'."}), 200 # OK

@app.route('/update_stats', methods=['POST'])
def update_stats():
    """
    Update a user's win/loss/games_played stats.
    Expects JSON: {'username': ..., 'wins': int, 'losses': int, 'games_played': int}
    Only provided fields will be updated.
    """
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username required.'}), 400

    username = data['username']
    users = load_users()
    if username not in users:
        return jsonify({'error': 'User not found.'}), 404

    # Update only provided fields
    if 'result' in data:
        if data['result'] == 'win':
            users[username]['wins'] = users[username].get('wins', 0) + 1
            users[username]['games_played'] = users[username].get('games_played', 0) + 1
        elif data['result'] == 'loss':
            users[username]['losses'] = users[username].get('losses', 0) + 1
            users[username]['games_played'] = users[username].get('games_played', 0) + 1

    save_users(users)
    return jsonify({'message': 'Stats updated.'}), 200

@app.route('/get_stats', methods=['GET'])
def get_stats():
    """
    Get a user's stats.
    Expects args: ?username=...
    """
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username required.'}), 400

    users = load_users()
    if username not in users:
        return jsonify({'error': 'User not found.'}), 404

    stats = {
        'wins': users[username].get('wins', 0),
        'losses': users[username].get('losses', 0),
        'games_played': users[username].get('games_played', 0)
    }
    return jsonify(stats), 200


# run main
if __name__ == '__main__':
    # check data exists
    ensure_user_file()
    # run app at following location
    app.run(host='0.0.0.0', port=5000, debug=True)